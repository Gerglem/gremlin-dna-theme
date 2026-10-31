# The read, fourth attempt: stop fighting Device Monitor for the device.
#
# Run: Device Monitor -> Diagnostics -> Advanced -> Run Script.
# Mod plugged in. READ ONLY. At most two AX attempts.
#
# ---------------------------------------------------------------------------
# EVERY ARGUMENT-LEVEL SUSPECT IS NOW DEAD
#
# Run 3 confirmed the good news and killed the last cheap theory:
#
#     A.OCC  field IE : LogicalLayout = LogicalLayout   <- IT CARRIES THE LAYOUT
#            field YE : Byte          = 128             <- our address, as a Byte
#            prop  UserModeVersion    = 311105588       <- set, survived Initialize
#     AX()   -> TimeoutException
#
# So the Programmer is correctly built, correctly addressed, knows the
# firmware version, and holds the real flash map - and the transfer still
# hangs. Ruled out across runs 2 and 3: AX's Boolean[] (both shapes), the
# UserModeVersion (genuinely set this time), the UE address (swept), and the
# JSL document (returns null when given one).
#
# What is left is the thing kb/16 flagged before any of this started:
# **a second HID handle makes replies interleave.** This probe runs inside
# Device Monitor, which polls the board continuously, and we have been opening
# our *own* link alongside it and then wondering why nothing answers.
#
# Two ways out, both tried here:
#
#   1. **Do not open a second handle.** Find the link Device Monitor already
#      has - the `ECig` / `Device` global is `A.OJA` - and hand that to UE's
#      factory instead. One handle, no contention.
#   2. **Give AX a real progress monitor.** It takes an IProgressMonitor and
#      has been getting null. kb/16 lists three concrete monitors with
#      parameterless constructors. Cheap to rule in or out.
#
# SAFETY: still the download half only. No PerformUpload, no write, no erase.
# Nothing here closes or disposes Device Monitor's connection - it only looks
# for one to borrow.
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
    try: return Directories.Documents.Path + "\\contention-probe.txt"
    except Exception: return "contention-probe.txt"

def _write():
    txt = "\n".join(lines)
    try:
        f = open(_out_path(), "w"); f.write(txt); f.close()
        UI.Message("report: " + _out_path())
    except:
        try: UI.ShowTextInEditor(txt)
        except: pass

import clr
from System import AppDomain, Array, Object, Func, Boolean, Int32, Activator
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
            if t.Name in ("GGQ", "UWB", "PYB", "POT") and t.Name not in T:
                T[t.Name] = t

    # ---- 1. does Device Monitor already hold a link we can borrow? ----
    say("=== 1. hunting an existing POT inside the ECig/Device object ===")
    borrowed = None
    try:
        root = ECig
    except Exception:
        root = None
    if root is None:
        say("  no ECig global")
    else:
        say("  ECig is %s" % root.GetType().FullName)
        seen = set()
        queue = [("ECig", root, 0)]
        n = 0
        while queue and n < 4000 and borrowed is None:
            path, obj, d = queue.pop(0)
            n += 1
            try: tn = obj.GetType().Name
            except: continue
            if tn == "POT":
                borrowed = obj
                say("  FOUND a live POT at %s" % path)
                break
            if d >= 5: continue
            try: key = id(obj)
            except: continue
            if key in seen: continue
            seen.add(key)
            t = obj.GetType()
            while t is not None and t.Name != "Object":
                try: flds = t.GetFields(DECL)
                except: flds = []
                for f in flds:
                    if f.FieldType.Name in ("String", "Int32", "Boolean", "Double",
                                            "Byte", "DateTime", "Single"): continue
                    try: v = f.GetValue(obj)
                    except: continue
                    if v is None: continue
                    queue.append(("%s.%s" % (path, f.Name), v, d + 1))
                t = t.BaseType
        if borrowed is None:
            say("  no POT reachable from ECig after %d objects" % n)

    # ---- build the PYB ----
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

    # ---- a link: the borrowed one if we found it, else our own ----
    pot = borrowed
    if pot is None:
        say("")
        say("  opening our own link instead (this is the contention case)")
        from System import Enum
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
            say("  no device found"); raise _Done()
        BGQ = None
        for a in AppDomain.CurrentDomain.GetAssemblies():
            for t in types_of(a):
                if t.Name == "BGQ": BGQ = t
        feo = None
        for m in BGQ.GetMethods(FLAGS):
            if m.Name == "FE" and m.ReturnType.Name == "POT": feo = m; break
        pot = feo.Invoke(None, Array[Object](
            [port, 9867, 1075, 0,
             Activator.CreateInstance(CSH) if CSH else None, 1,
             Enum.ToObject(IGI, 0) if IGI else None]))
    say("  link in hand: %s%s"
        % (pot.GetType().FullName if pot else "None",
           "  (BORROWED - no second handle)" if borrowed is not None else "  (ours)"))
    if pot is None: raise _Done()

    pyPOT = clr.GetPythonType(T["POT"])
    def _give_link(): return pot
    ue = [m for m in T["PYB"].GetMethods(FLAGS) if m.Name == "UE"][0]
    occ = ue.Invoke(pyb, Array[Object]([Func[pyPOT](_give_link), UE_ADDRESS]))
    occ.GetType().GetProperty("UserModeVersion", FLAGS).SetValue(occ, Int32(EXPECT_VERSION), None)
    try:
        occ.GetType().GetMethod("Initialize", FLAGS).Invoke(occ, Array[Object]([]))
    except Exception, e:
        say("  Initialize threw: %s" % err(e))
    say("  Programmer ready, version %s"
        % occ.GetType().GetProperty("UserModeVersion", FLAGS).GetValue(occ, None))

    # ---- 2. AX, with a real progress monitor ----
    say("")
    say("=== 2. AX with a real IProgressMonitor ===")
    mon = None
    for nm in ("FMQ", "BTQ", "RXW", "PMW"):
        for a in AppDomain.CurrentDomain.GetAssemblies():
            for t in types_of(a):
                if t.Name != nm or t.IsAbstract: continue
                try:
                    cand = Activator.CreateInstance(t)
                    say("  built a %s as the monitor" % t.FullName)
                    mon = cand
                except Exception:
                    pass
                if mon is not None: break
            if mon is not None: break
        if mon is not None: break
    if mon is None:
        say("  none of Evolv's monitors could be constructed; using null")

    ax = None
    for m in occ.GetType().GetMethods(FLAGS):
        if m.Name == "AX": ax = m
    flags3 = Array[Boolean]([True, True, True])
    for label, margs in (("with monitor", [mon, flags3]), ("with null monitor", [None, flags3])):
        if label == "with null monitor" and mon is None: continue
        say("")
        say("  -- AX(%s) --" % label)
        try:
            img = ax.Invoke(occ, Array[Object](margs))
            if img is None:
                say("     -> None")
            else:
                say("     -> %s" % img.GetType().Name)
                try: say("     length = %s bytes  *** THE READ WORKED ***" % len(img))
                except: pass
                break
        except Exception, e:
            say("     threw: %s" % err(e))

    say("")
    if borrowed is None:
        say("NOTE: this run used its own second handle. If it timed out again,")
        say("the next thing to try is running the read with Device Monitor's own")
        say("polling stopped, or from outside EScribe entirely.")
    say("Nothing was written to the device by this script.")


try:
    main()
except _Done:
    pass
except Exception, e:
    say("UNEXPECTED: %s" % err(e))
_write()
