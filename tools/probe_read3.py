# The read, third attempt: correct the version type, and walk the base classes.
#
# Run: Device Monitor -> Diagnostics -> Advanced -> Run Script.
# Mod plugged in. READ ONLY. **One AX attempt only** - timeouts cost bench time.
#
# ---------------------------------------------------------------------------
# WHAT RUN 2 ESTABLISHED, AND WHAT WAS MY MISTAKE
#
# Ruled out for real:
#   * AX's Boolean[] is not the problem. Both a Boolean[3] of True and an
#     empty Boolean[0] timed out identically.
#
# Two things that looked like findings and were not:
#
#   1. **"UserModeVersion could not be set"** - it is `Nullable<Int32>`, and I
#      passed a `UInt32`. The conversion failed, so the version was never
#      actually set and the leading hypothesis was never tested. Fixed here by
#      passing a plain Int32.
#
#   2. **"The Programmer exposes no layout"** - `GetProperties` does **not**
#      return non-public members inherited from a base class, and `A.ECC`
#      derives from `OCC`, which is where kb/16 found `IE : LogicalLayout`
#      exposed as `NM`. A two-property dump is an artefact of how I asked.
#      This walks the whole type chain, properties and fields, declared-only
#      at each level.
#
# Order matters this time: set the version **before** Initialize(), since a
# handshake it cannot perform is what we are standing in for.
#
# SAFETY: Initialize() and AX() are the download half - no PerformUpload, no
# write, no erase. Setting UserModeVersion writes to our own in-memory object.
# ---------------------------------------------------------------------------

DEVICE, VERSION = 109, 1
EXPECT_VERSION = 311105588
UE_ADDRESS = 128

lines = []
def say(s):
    try: lines.append(str(s))
    except: lines.append("<unprintable>")

class _Done(Exception):
    pass

def _out_path():
    try: return Directories.Documents.Path + "\\read-probe3.txt"
    except Exception: return "read-probe3.txt"

def _write():
    txt = "\n".join(lines)
    try:
        f = open(_out_path(), "w"); f.write(txt); f.close()
        UI.Message("report: " + _out_path())
    except:
        try: UI.ShowTextInEditor(txt)
        except: pass

import clr
from System import AppDomain, Array, Object, Func, Boolean, Int32
from System.Reflection import BindingFlags
FLAGS = (BindingFlags.Public | BindingFlags.NonPublic |
         BindingFlags.Static | BindingFlags.Instance)
DECL = (BindingFlags.Public | BindingFlags.NonPublic |
        BindingFlags.Instance | BindingFlags.DeclaredOnly)

def types_of(a):
    try: return a.GetTypes()
    except Exception, e:
        try: return [t for t in e.clsException.Types if t is not None]
        except: return []

def err(e):
    try:
        inner = e.clsException.InnerException
        if inner is not None: return str(inner.Message).split("\n")[0]
    except: pass
    return str(e).split("\n")[0]


def main():
    T = {}
    for a in AppDomain.CurrentDomain.GetAssemblies():
        for t in types_of(a):
            if t.Name in ("GGQ", "UWB", "PYB", "POT", "BGQ") and t.Name not in T:
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
    pyb = dwb.GetType().GetMethod("JSL", FLAGS).Invoke(dwb, Array[Object]([None, ggq, None]))

    from System import Activator, Enum
    hid = None
    for a in AppDomain.CurrentDomain.GetAssemblies():
        try:
            if a.GetName().Name == "HidSharp": hid = a
        except: pass
    CSH = IGI = None
    for t in (types_of(hid) if hid else []):
        if t.Name == "CSH": CSH = t
        if t.Name == "IGI": IGI = t

    clr.AddReference("System.Management")
    from System.Management import ManagementObjectSearcher
    from System import Convert
    from System.Text import Encoding
    port = None
    q = "SELECT DeviceID FROM Win32_PnPEntity WHERE DeviceID LIKE '%VID_268B%PID_0433%'"
    for o in ManagementObjectSearcher(q).Get():
        did = str(o["DeviceID"])
        if "MI_" in did: continue
        serial = did.split("\\")[-1]
        if not serial: continue
        port = "HID:" + Convert.ToBase64String(
            Encoding.UTF8.GetBytes("%d'%d'%s" % (9867, 1075, serial)))
        break
    if port is None:
        say("no device found"); raise _Done()

    feo = None
    for m in T["BGQ"].GetMethods(FLAGS):
        if m.Name == "FE" and m.ReturnType.Name == "POT": feo = m; break
    cfg = Activator.CreateInstance(CSH) if CSH is not None else None
    igi0 = Enum.ToObject(IGI, 0) if IGI is not None else None
    pot = feo.Invoke(None, Array[Object]([port, 9867, 1075, 0, cfg, 1, igi0]))

    pyPOT = clr.GetPythonType(T["POT"])
    def _give_link(): return pot
    ue = [m for m in T["PYB"].GetMethods(FLAGS) if m.Name == "UE"][0]
    occ = ue.Invoke(pyb, Array[Object]([Func[pyPOT](_give_link), UE_ADDRESS]))
    say("PYB -> link -> Programmer: %s" % occ.GetType().FullName)

    # ---- 1. the WHOLE type chain, declared-only at each level ----
    say("")
    say("=== every member, walking up from %s ===" % occ.GetType().Name)
    t = occ.GetType()
    while t is not None and t.Name != "Object":
        say("")
        say("  --- %s ---" % t.FullName)
        try:
            for pr in sorted(t.GetProperties(DECL), key=lambda x: x.Name):
                val = "?"
                try:
                    if len(pr.GetIndexParameters()) == 0:
                        v = pr.GetValue(occ, None)
                        val = "None" if v is None else (
                            str(v) if pr.PropertyType.Name in
                            ("Int32", "UInt32", "Boolean", "String", "Byte") else v.GetType().Name)
                except Exception, e:
                    val = "<%s>" % err(e)
                say("    prop  %-20s %-18s = %s" % (pr.Name, pr.PropertyType.Name, val))
        except Exception, e:
            say("    props failed: %s" % err(e))
        try:
            for f in sorted(t.GetFields(DECL), key=lambda x: x.Name):
                val = "?"
                try:
                    v = f.GetValue(occ)
                    val = "None" if v is None else (
                        str(v) if f.FieldType.Name in
                        ("Int32", "UInt32", "Boolean", "String", "Byte") else v.GetType().Name)
                except Exception, e:
                    val = "<%s>" % err(e)
                say("    field %-20s %-18s = %s" % (f.Name, f.FieldType.Name, val))
        except Exception, e:
            say("    fields failed: %s" % err(e))
        t = t.BaseType

    # ---- 2. set the version, with the right type this time ----
    say("")
    say("=== set UserModeVersion = %d  (Nullable<Int32>, not UInt32) ===" % EXPECT_VERSION)
    try:
        pr = occ.GetType().GetProperty("UserModeVersion", FLAGS)
        pr.SetValue(occ, Int32(EXPECT_VERSION), None)
        say("  now reads: %s" % pr.GetValue(occ, None))
    except Exception, e:
        say("  failed: %s" % err(e))

    # ---- 3. Initialize AFTER the version is known ----
    say("")
    say("=== Initialize()  (after the version, this time) ===")
    try:
        occ.GetType().GetMethod("Initialize", FLAGS).Invoke(occ, Array[Object]([]))
        say("  returned")
        pr = occ.GetType().GetProperty("UserModeVersion", FLAGS)
        say("  UserModeVersion still reads: %s" % pr.GetValue(occ, None))
    except Exception, e:
        say("  threw: %s" % err(e))

    # ---- 4. ONE AX attempt ----
    say("")
    say("=== AX() - ONE attempt. READ ONLY ===")
    ax = None
    for m in occ.GetType().GetMethods(FLAGS):
        if m.Name == "AX": ax = m
    if ax is None:
        say("  AX not found"); raise _Done()
    try:
        img = ax.Invoke(occ, Array[Object]([None, Array[Boolean]([True, True, True])]))
        if img is None:
            say("  -> None")
        else:
            say("  -> %s" % img.GetType().Name)
            try: say("  length = %s bytes   *** THE READ WORKED ***" % len(img))
            except: pass
    except Exception, e:
        say("  threw: %s" % err(e))
        say("")
        say("  If this is still a timeout with the version set, the remaining")
        say("  suspect is HID contention: Device Monitor polls the board while")
        say("  this runs, and kb/16 records that a second handle interleaves")
        say("  replies.")

    say("")
    say("Nothing was written to the device by this script.")


try:
    main()
except _Done:
    pass
except Exception, e:
    say("UNEXPECTED: %s" % err(e))
_write()
