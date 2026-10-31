# Sweep UE's Int32 across every byte value, and see what NDY is.
#
# Run: Device Monitor -> Diagnostics -> Advanced -> Run Script.
# Device-free. Nothing is opened, nothing is written.
#
# ---------------------------------------------------------------------------
# WHAT THE LAST RUN SETTLED, AND WHAT IT RULED OUT
#
# The memory map is **not** malformed - that hypothesis is dead. KE()'s four
# areas are start/end pairs that tile the layout exactly:
#
#     EEPROM  0x000000..0x000600            |
#     ''      0x000600..0x018E00            |  = region 0, 101888 bytes
#     KERNEL  0x018E00..0x018F00               = region 1, 256 bytes
#     FLASH   0x500000..0x518000               = region 2, 98304 bytes
#
# The nameless area is simply the settings block between EEPROM and KERNEL.
#
# Also dead: the idea that JSL wants a real document. Given a non-null first
# argument it **returns null** - it does not throw - so JSL(None, ggq, None)
# is the correct call and the PYB we already build is the right one.
#
# What is left is `DDY..ctor(Byte address, NDY)`. The parameter is a **Byte**,
# so the valid range is 0..255 - and every address in the map above is far
# larger than that. So `address` is not a memory offset; it is a small
# identifier of some kind, and UE's Int32 is the only thing we control that
# could reach it. Only 0, 1, 2, 3, 109 and the version have been tried.
#
# This sweeps all 256, and reports what NDY is - if it is an enum, its names
# may say what kind of address this is.
#
# SAFETY: builds the PYB exactly as before and calls UE with a **null** Func,
# so even a UE that succeeds cannot reach the device - it has no way to get a
# connection. No link, no Initialize, no AX, no upload.
# ---------------------------------------------------------------------------

DEVICE, VERSION = 109, 1

lines = []
def say(s):
    try: lines.append(str(s))
    except: lines.append("<unprintable>")

class _Done(Exception):
    pass

def _out_path():
    try: return Directories.Documents.Path + "\\ue-sweep.txt"
    except Exception: return "ue-sweep.txt"

def _write():
    txt = "\n".join(lines)
    try:
        f = open(_out_path(), "w"); f.write(txt); f.close()
        UI.Message("report: " + _out_path())
    except:
        try: UI.ShowTextInEditor(txt)
        except: pass

import clr
from System import AppDomain, Array, Object
from System.Reflection import BindingFlags
FLAGS = (BindingFlags.Public | BindingFlags.NonPublic |
         BindingFlags.Static | BindingFlags.Instance)

def types_of(a):
    try: return a.GetTypes()
    except Exception, e:
        try: return [t for t in e.clsException.Types if t is not None]
        except: return []


def main():
    T = {}
    for a in AppDomain.CurrentDomain.GetAssemblies():
        for t in types_of(a):
            if t.Name in ("GGQ", "UWB", "PYB", "NDY", "DDY", "TCC", "SRB") and t.Name not in T:
                T[t.Name] = t

    # ---- what is NDY? ----
    say("=== NDY, DDY's second argument ===")
    n = T.get("NDY")
    if n is None:
        say("  not found")
    else:
        say("  %s  enum=%s" % (n.FullName, n.IsEnum))
        if n.IsEnum:
            try:
                for nm in n.GetEnumNames():
                    say("    %s" % nm)
            except Exception, e:
                say("  names unreadable: %s" % e)
        else:
            for f in n.GetFields(BindingFlags.Public | BindingFlags.NonPublic |
                                 BindingFlags.Instance):
                say("    field %s : %s" % (f.Name, f.FieldType.Name))

    # ---- build the PYB the proven way ----
    say("")
    say("=== build the PYB ===")
    clr.AddReference("System.Xml.Linq")
    from System.Xml.Linq import XElement
    el = XElement.Parse('<DESabertooth Device="%d" Version="%d" />' % (DEVICE, VERSION))
    gc = [c for c in T["GGQ"].GetConstructors(FLAGS)
          if len(c.GetParameters()) == 1
          and c.GetParameters()[0].ParameterType.Name == "XElement"][0]
    ggq = gc.Invoke(Array[Object]([el]))
    fe = [m for m in T["UWB"].GetMethods(FLAGS)
          if m.Name == "FE" and m.IsStatic and len(m.GetParameters()) == 1
          and m.GetParameters()[0].ParameterType.Name == "GGQ"][0]
    dwb = fe.Invoke(None, Array[Object]([ggq]))
    pyb = dwb.GetType().GetMethod("JSL", FLAGS).Invoke(dwb, Array[Object]([None, ggq, None]))
    if pyb is None:
        say("  JSL returned null - stopping"); raise _Done()
    say("  %s -> %s" % (dwb.GetType().Name, pyb.GetType().Name))

    # ---- sweep ----
    say("")
    say("=== UE(null, n) for n = 0..255 ===")
    ue = [m for m in T["PYB"].GetMethods(FLAGS) if m.Name == "UE"][0]
    wins, errs = [], {}
    for i in range(256):
        try:
            occ = ue.Invoke(pyb, Array[Object]([None, i]))
            wins.append((i, occ.GetType().FullName if occ is not None else "None"))
        except Exception, e:
            msg = str(e)
            try:
                inner = e.clsException.InnerException
                if inner is not None: msg = inner.Message
            except: pass
            msg = msg.split("\n")[0].strip()
            errs.setdefault(msg, []).append(i)

    if wins:
        say("  *** %d value(s) produced a Programmer ***" % len(wins))
        for i, tn in wins:
            say("    UE(null, %d) -> %s" % (i, tn))
    else:
        say("  none of 0..255 worked.")

    say("")
    say("  distinct errors across the sweep:")
    for msg, idxs in errs.items():
        rng = "%d..%d" % (min(idxs), max(idxs)) if len(idxs) > 3 else str(idxs)
        say("    [%3d values, %s]  %s" % (len(idxs), rng, msg))

    if not wins:
        say("")
        say("  If every value gives the same error, UE's Int32 is not the address,")
        say("  and the bad one is computed inside TCC.Initialize from PYB state we")
        say("  have not identified. The next lead would be SRB.EE / TCC, not UE.")

    say("")
    say("Nothing was written and no link was opened.")


try:
    main()
except _Done:
    pass
except Exception, e:
    say("UNEXPECTED: %s" % e)
_write()
