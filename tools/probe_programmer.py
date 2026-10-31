# Step 2: get a Programmer that actually HAS the layout.
#
# Run: Device Monitor -> Diagnostics -> Advanced -> Run Script.
#
# ---------------------------------------------------------------------------
# WHAT THIS IS FOR
#
# probe_layout.py built a PYB with no device attached and read the real flash
# map off it. The next object in the chain is the Programmer:
#
#     pyb.UE(Func<>, Int32) -> OCC
#
# This matters because the *original* failure in kb/16 was a Programmer with no
# layout: Programmer.CreateForDNAColor never sets one, so AX() threw
# NullReferenceException every way it was tried. The question here is simply
# whether UE() returns one whose layout is populated - which is what the whole
# PYB detour was for.
#
# It also prints UE's exact signature first, because Func<> says nothing about
# what the delegate is for, and reads PYB.KE() - the settings dictionary - as
# a read-only sanity check that the PYB is a real, populated object.
#
# ---------------------------------------------------------------------------
# SAFETY
#
#   * no link is opened - no port, no HID path, no Stream assigned
#   * Initialize() is NOT called
#   * AX() is NOT called, PerformUpload is NOT called
#   * nothing is written, uploaded, erased or sent
#
# A Programmer with no Stream talks to nothing. **The mod need not be plugged
# in.** Worst realistic outcome is an EScribe restart (kb/07 #28).
# ---------------------------------------------------------------------------

DEVICE, VERSION = 109, 1

lines = []
def say(s):
    try: lines.append(str(s))
    except: lines.append("<unprintable>")

def _out_path():
    try: return Directories.Documents.Path + "\\programmer-probe.txt"
    except Exception: return "programmer-probe.txt"

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

T = {}
for a in AppDomain.CurrentDomain.GetAssemblies():
    for t in types_of(a):
        if t.Name in ("GGQ", "UWB", "PYB", "OCC") and t.Name not in T:
            T[t.Name] = t

# ---- rebuild the PYB (proven in probe_layout.py) ----
say("=== rebuild the PYB ===")
pyb = None
try:
    clr.AddReference("System.Xml.Linq")
    from System.Xml.Linq import XElement
    el = XElement.Parse("<DESabertooth Device=\"%d\" Version=\"%d\" />" % (DEVICE, VERSION))
    ctor = None
    for c in T["GGQ"].GetConstructors(FLAGS):
        ps = c.GetParameters()
        if len(ps) == 1 and ps[0].ParameterType.Name == "XElement": ctor = c
    ggq = ctor.Invoke(Array[Object]([el]))
    fe = None
    for m in T["UWB"].GetMethods(FLAGS):
        if m.Name == "FE" and m.IsStatic:
            ps = m.GetParameters()
            if len(ps) == 1 and ps[0].ParameterType.Name == "GGQ": fe = m
    dwb = fe.Invoke(None, Array[Object]([ggq]))
    pyb = dwb.GetType().GetMethod("JSL", FLAGS).Invoke(dwb, Array[Object]([None, ggq, None]))
    say("  GGQ %r -> DWB %s -> PYB %s"
        % (ggq, dwb.GetType().Name, pyb.GetType().Name if pyb else "None"))
except Exception, e:
    say("  FAILED: %s" % e); _write(); raise SystemExit

# ---- is the PYB actually populated? read-only ----
say("")
say("=== PYB.KE() - the settings dictionary (read-only sanity check) ===")
try:
    ke = pyb.GetType().GetMethod("KE", FLAGS).Invoke(pyb, Array[Object]([]))
    say("  -> %s   count=%s" % (ke.GetType().Name if ke else "None",
                                ke.Count if ke else "-"))
except Exception, e:
    say("  KE() failed: %s" % e)

# ---- what does UE actually want? ----
say("")
say("=== PYB.UE signatures ===")
ues = []
try:
    for m in T["PYB"].GetMethods(FLAGS):
        if m.Name != "UE": continue
        ps = m.GetParameters()
        say("  UE(%s) -> %s"
            % (", ".join("%s %s" % (p.ParameterType.FullName, p.Name) for p in ps),
               m.ReturnType.Name))
        ues.append((m, ps))
except Exception, e:
    say("  failed: %s" % e)

# ---- try to get a Programmer ----
#
# Run 1 showed UE(Func<A.POT>, Int32). A.POT is the HID *link* object - the
# thing probe_open_link.py's FE(port, vid, pid, 0) returns - so the Func is a
# connection factory. Passing None for it threw
# ArgumentOutOfRangeException("address") from inside TCC.Initialize(), which
# is consistent with the null delegate rather than with the Int32.
#
# So: pass a REAL delegate that returns null. If UE is lazy - if it only calls
# the factory when it actually needs a link - we get a Programmer and can read
# its layout with the mod still untouched. If it calls the factory eagerly,
# the error moves, and that tells us the device-free path ends here.
say("")
say("=== calling UE ===")

POT = None
for a in AppDomain.CurrentDomain.GetAssemblies():
    for t in types_of(a):
        if t.Name == "POT" and t.Namespace == "A": POT = t
say("  A.POT type: %s" % ("found" if POT is not None else "NOT FOUND"))

null_factory = None
if POT is not None:
    try:
        from System import Func
        pyPOT = clr.GetPythonType(POT)
        def _no_link():
            return None
        null_factory = Func[pyPOT](_no_link)
        say("  built Func[POT] that returns null - it opens nothing")
    except Exception, e:
        say("  could not build the delegate: %s" % e)

occ = None
for m, ps in ues:
    if occ is not None: break
    for fac, facname in ((null_factory, "nullFunc"), (None, "None")):
        if fac is None and facname == "nullFunc": continue
        for n in (0, 1, 2, 3, VERSION, DEVICE):
            if len(ps) != 2: continue
            try:
                occ = m.Invoke(pyb, Array[Object]([fac, n]))
                say("  UE(%s, %s) -> %s"
                    % (facname, n, occ.GetType().FullName if occ else "None"))
                if occ is not None: break
            except Exception, e:
                msg = str(e)
                try: msg = str(e.clsException.InnerException or e.clsException)
                except: pass
                say("  UE(%s, %s) failed: %s" % (facname, n, msg.split("
")[0]))
        if occ is not None: break

# ---- THE QUESTION: does it have a layout? ----
say("")
say("=== does the Programmer carry the layout? ===")
if occ is None:
    say("  no Programmer - UE needs a real delegate for its Func<> argument.")
    say("  The signature printed above says what it must return.")
else:
    found = False
    for nm in ("NM", "IE"):
        try:
            pr = occ.GetType().GetProperty(nm, FLAGS)
            if pr is None: continue
            v = pr.GetValue(occ, None)
            say("  %s -> %s" % (nm, v.GetType().Name if v is not None else "None"))
            if v is not None:
                found = True
                try:
                    say("     PCSize=%s PCSizeUsed=%s regions=%s"
                        % (v.PCSize, v.PCSizeUsed, len([r for r in v.Regions])))
                except Exception, e:
                    say("     could not read it: %s" % e)
        except Exception, e:
            say("  %s failed: %s" % (nm, e))
    say("")
    say("  VERDICT: %s" % ("Programmer HAS a layout - this is the object "
                           "CreateForDNAColor could never produce"
                           if found else
                           "layout is null - UE may need the Func<> to supply it"))

_write()
