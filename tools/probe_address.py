# Find the invalid "address" that stops PYB.UE.
#
# Run: Device Monitor -> Diagnostics -> Advanced -> Run Script.
# Device-free - nothing is opened, nothing is written.
#
# ---------------------------------------------------------------------------
# WHERE WE ARE
#
# UE throws ArgumentOutOfRangeException("address") from
#     A.DDY..ctor(Byte address, NDY) <- A.TCC.Initialize() <- A.SRB.EE <- UE
# before it ever calls its Func, and for every Int32 tried. So the bad address
# is already sitting in the PYB when UE is called.
#
# probe_pyb_state.py found where it probably lives. KE() returns FOUR memory
# areas by name:
#
#     'EEPROM' : WYB      '' : WYB      'KERNEL' : WYB      'FLASH' : WYB
#
# but PE() reports only THREE regions - and one of those keys is the **empty
# string**. A nameless, possibly unpopulated area is exactly the shape of
# thing that would hand a Byte constructor an address it cannot use.
#
# This script reads each WYB's own fields looking for that address, so we can
# see which area is malformed and what it holds.
#
# It also answers the second thing that went wrong: passing a real document to
# JSL failed with "expected object, got NoneType", which is an IronPython
# *marshalling* complaint, not a .NET one - the call shape was wrong, not the
# argument. So it enumerates every JSL overload with full parameter types, and
# retries using an explicitly typed Object[] rather than a Python list.
#
# SAFETY: reads fields on objects that already exist, and calls only JSL, PE
# and KE - all of which are already proven harmless. No link, no Programmer,
# no upload path.
# ---------------------------------------------------------------------------

DEVICE, VERSION = 109, 1

lines = []
def say(s):
    try: lines.append(str(s))
    except: lines.append("<unprintable>")

class _Done(Exception):
    pass

def _out_path():
    try: return Directories.Documents.Path + "\\address-probe.txt"
    except Exception: return "address-probe.txt"

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
INST = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance

def types_of(a):
    try: return a.GetTypes()
    except Exception, e:
        try: return [t for t in e.clsException.Types if t is not None]
        except: return []


def main():
    T = {}
    for a in AppDomain.CurrentDomain.GetAssemblies():
        for t in types_of(a):
            if t.Name in ("GGQ", "UWB", "PYB", "DWB", "WYB", "DDY") and t.Name not in T:
                T[t.Name] = t

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
    say("DWB: %s" % dwb.GetType().FullName)

    # ---- 1. every JSL overload, in full ----
    say("")
    say("=== 1. JSL overloads on %s ===" % dwb.GetType().Name)
    jsls = []
    for m in dwb.GetType().GetMethods(FLAGS):
        if m.Name != "JSL": continue
        ps = m.GetParameters()
        say("  JSL(%s) -> %s"
            % (", ".join("%s %s" % (p.ParameterType.FullName, p.Name or "?") for p in ps),
               m.ReturnType.Name))
        jsls.append((m, ps))

    # ---- 2. the PYB, and the memory areas it holds ----
    say("")
    say("=== 2. memory areas in a null-document PYB ===")
    m0 = jsls[0][0]
    args = Array[Object](3)
    args[0] = None; args[1] = ggq; args[2] = None
    pyb = m0.Invoke(dwb, args)
    say("  PYB: %s" % pyb.GetType().Name)

    try:
        layout = pyb.GetType().GetMethod("PE", FLAGS).Invoke(pyb, Array[Object](0))
        say("  PE(): %d regions" % len([r for r in layout.Regions]))
        for i, r in enumerate(layout.Regions):
            say("    region %d: size %d  dev 0x%06X" % (i, r.Size, r.DeviceOffset))
    except Exception, e:
        say("  PE() failed: %s" % e)

    try:
        ke = pyb.GetType().GetMethod("KE", FLAGS).Invoke(pyb, Array[Object](0))
        say("")
        say("  KE() has %d areas. Fields of each:" % ke.Count)
        for k in ke.Keys:
            v = ke[k]
            say("")
            say("    [%r] -> %s" % (k, v.GetType().Name if v is not None else "None"))
            if v is None: continue
            for f in v.GetType().GetFields(INST):
                try: val = f.GetValue(v)
                except Exception, e: val = "<%s>" % e
                tn = f.FieldType.Name
                if tn in ("Byte", "SByte", "Int16", "Int32", "UInt32", "UInt16",
                          "Boolean", "String", "Int64", "UInt64"):
                    say("        %-6s %-8s = %s" % (f.Name, tn, val))
                else:
                    say("        %-6s %-8s = %s" % (f.Name, tn,
                        "None" if val is None else val.GetType().Name))
    except Exception, e:
        say("  KE() failed: %s" % e)

    # ---- 3. the PYB's own numeric fields ----
    say("")
    say("=== 3. the PYB's own fields ===")
    for f in pyb.GetType().GetFields(INST):
        try: val = f.GetValue(pyb)
        except Exception, e: val = "<%s>" % e
        tn = f.FieldType.Name
        if tn in ("Byte", "Int32", "UInt32", "Boolean", "String", "UInt16"):
            say("  %-4s %-14s = %s" % (f.Name, tn, val))
        else:
            say("  %-4s %-14s = %s" % (f.Name, tn, "None" if val is None else val.GetType().Name))

    # ---- 4. what does DDY want? ----
    say("")
    say("=== 4. DDY constructors - the thing that rejects the address ===")
    if T.get("DDY") is not None:
        for c in T["DDY"].GetConstructors(FLAGS):
            say("  ctor(%s)"
                % ", ".join("%s %s" % (p.ParameterType.Name, p.Name or "?")
                            for p in c.GetParameters()))
    else:
        say("  DDY not found")

    # ---- 5. retry JSL with a real document, properly marshalled ----
    say("")
    say("=== 5. JSL with a real first argument, typed Object[] ===")
    for label, first in (("XElement", el), ("string", "x")):
        try:
            a2 = Array[Object](3)
            a2[0] = first; a2[1] = ggq; a2[2] = None
            p2 = m0.Invoke(dwb, a2)
            say("  JSL(%s, ...) -> %s" % (label, p2.GetType().Name if p2 else "None"))
            try:
                ue = [m for m in T["PYB"].GetMethods(FLAGS) if m.Name == "UE"][0]
                ua = Array[Object](2); ua[0] = None; ua[1] = 0
                occ = ue.Invoke(p2, ua)
                say("    UE -> %s  <<<<< GOT A PROGRAMMER"
                    % (occ.GetType().FullName if occ else "None"))
            except Exception, e:
                inner = None
                try: inner = e.clsException.InnerException
                except: pass
                say("    UE threw: %s" % str(inner.Message if inner else e).split("\n")[0])
        except Exception, e:
            inner = None
            try: inner = e.clsException.InnerException
            except: pass
            say("  JSL(%s, ...) threw: %s" % (label, str(inner.Message if inner else e).split("\n")[0]))

    say("")
    say("Nothing was written and no link was opened.")


try:
    main()
except _Done:
    pass
except Exception, e:
    say("UNEXPECTED: %s" % e)
_write()
