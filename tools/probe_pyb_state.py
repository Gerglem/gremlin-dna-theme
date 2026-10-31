# Why does PYB.UE throw before it ever uses the link?
#
# Run: Device Monitor -> Diagnostics -> Advanced -> Run Script.
# The mod does not need to be plugged in for this one.
#
# ---------------------------------------------------------------------------
# WHAT WE KNOW
#
# probe_read.py got the link open - FE(port, 9867, 1075, 0) -> A.POT - and then
# PYB.UE(factory, n) threw ArgumentOutOfRangeException("address") for n in
# 0..3. The important part: **the same exception appeared with a null Func**,
# so UE is failing before it calls the factory. The Int32 and the link are
# both innocent; something about the PYB's own state is wrong.
#
# The obvious suspect is `JSL(Object, GGQ, Nullable)`, where we pass **None**
# for the first argument. PE() returns a layout without it - the flash map is
# per board - but UE builds a Programmer, and that may need the settings
# document the null is standing in for.
#
# The earlier stack was:
#     A.DDY..ctor(Byte address, NDY) <- A.TCC.Initialize() <- A.SRB.EE <- PYB.UE
# so a Byte "address" is computed from something and comes out invalid.
#
# This script:
#   1. dumps every member of PYB, so we can see what state it carries and what
#      might need setting before UE is callable;
#   2. inspects KE() - the settings dictionary - to see what is actually in it;
#   3. rebuilds the PYB with several different first arguments to JSL and
#      tries UE after each, reporting which (if any) gets further.
#
# SAFETY: no link is opened, nothing is written, no upload path is entered.
# UE only builds an object; with a null factory it cannot reach the device.
# ---------------------------------------------------------------------------

DEVICE, VERSION = 109, 1

lines = []
def say(s):
    try: lines.append(str(s))
    except: lines.append("<unprintable>")

class _Done(Exception):
    pass

def _out_path():
    try: return Directories.Documents.Path + "\\pyb-state.txt"
    except Exception: return "pyb-state.txt"

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
            if t.Name in ("GGQ", "UWB", "PYB", "DWB") and t.Name not in T:
                T[t.Name] = t

    clr.AddReference("System.Xml.Linq")
    from System.Xml.Linq import XElement, XDocument

    def make_ggq():
        el = XElement.Parse('<DESabertooth Device="%d" Version="%d" />' % (DEVICE, VERSION))
        gc = [c for c in T["GGQ"].GetConstructors(FLAGS)
              if len(c.GetParameters()) == 1
              and c.GetParameters()[0].ParameterType.Name == "XElement"][0]
        return el, gc.Invoke(Array[Object]([el]))

    def make_pyb(first):
        el, ggq = make_ggq()
        fe = [m for m in T["UWB"].GetMethods(FLAGS)
              if m.Name == "FE" and m.IsStatic and len(m.GetParameters()) == 1
              and m.GetParameters()[0].ParameterType.Name == "GGQ"][0]
        dwb = fe.Invoke(None, Array[Object]([ggq]))
        arg = el if first == "element" else (XDocument(el) if first == "document" else None)
        pyb = dwb.GetType().GetMethod("JSL", FLAGS).Invoke(dwb, Array[Object]([arg, ggq, None]))
        return pyb

    # ---- 1. what does a PYB actually carry? ----
    say("=== 1. PYB members ===")
    try:
        t = T["PYB"]
        say("  -- methods --")
        seen = set()
        for m in sorted(t.GetMethods(FLAGS), key=lambda x: x.Name):
            if m.Name.startswith("get_") or m.Name.startswith("set_"): continue
            sig = "%s(%s) -> %s" % (m.Name,
                                    ", ".join(p.ParameterType.Name for p in m.GetParameters()),
                                    m.ReturnType.Name)
            if sig in seen: continue
            seen.add(sig)
            say("    " + sig)
        say("  -- properties --")
        for pr in sorted(t.GetProperties(FLAGS), key=lambda x: x.Name):
            say("    %s : %s" % (pr.Name, pr.PropertyType.Name))
        say("  -- fields --")
        for f in sorted(t.GetFields(FLAGS), key=lambda x: x.Name):
            say("    %s : %s" % (f.Name, f.FieldType.Name))
    except Exception, e:
        say("  failed: %s" % e)

    # ---- 2. what is in KE()? ----
    say("")
    say("=== 2. the settings dictionary from a null-document PYB ===")
    try:
        pyb = make_pyb(None)
        ke = pyb.GetType().GetMethod("KE", FLAGS).Invoke(pyb, Array[Object]([]))
        say("  KE() -> %s  count=%s" % (ke.GetType().Name, ke.Count))
        n = 0
        for k in ke.Keys:
            v = ke[k]
            say("    %r : %s" % (k, v.GetType().Name if v is not None else "None"))
            n += 1
            if n >= 20: say("    ..."); break
    except Exception, e:
        say("  failed: %s" % e)

    # ---- 3. does a real first argument to JSL change anything? ----
    say("")
    say("=== 3. JSL first argument vs UE ===")
    ue = [m for m in T["PYB"].GetMethods(FLAGS) if m.Name == "UE"][0]
    for first in (None, "element", "document"):
        say("")
        say("  --- JSL(%s, ggq, None) ---" % (first or "None"))
        try:
            pyb = make_pyb(first)
            say("    PYB built: %s" % pyb.GetType().Name)
        except Exception, e:
            inner = None
            try: inner = e.clsException.InnerException
            except: pass
            say("    JSL threw: %s" % (inner.Message if inner else e)); continue
        try:
            layout = pyb.GetType().GetMethod("PE", FLAGS).Invoke(pyb, Array[Object]([]))
            say("    PE() -> %s regions"
                % (len([r for r in layout.Regions]) if layout is not None else "null"))
        except Exception, e:
            say("    PE() threw: %s" % e)
        for n in (0, 1):
            try:
                occ = ue.Invoke(pyb, Array[Object]([None, n]))
                say("    UE(None, %d) -> %s  <<<<< GOT A PROGRAMMER"
                    % (n, occ.GetType().FullName if occ else "None"))
            except Exception, e:
                inner = None
                try: inner = e.clsException.InnerException
                except: pass
                msg = str(inner.Message if inner else e).split("\n")[0]
                say("    UE(None, %d) threw: %s" % (n, msg))

    say("")
    say("Nothing was written and no link was opened.")


try:
    main()
except _Done:
    pass
except Exception, e:
    say("UNEXPECTED: %s" % e)
_write()
