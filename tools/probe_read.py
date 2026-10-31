# Step 3: open a link, get a Programmer that HAS the layout, and READ.
#
# Run: Device Monitor -> Diagnostics -> Advanced -> Run Script.
# **Plug the mod in.** The port string is derived from the connected device;
# `dna-port.txt` is only a fallback if enumeration fails.
#
# ---------------------------------------------------------------------------
# WHY A READ AND NOT THE DRY RUN
#
# `PerformUpload(ctx, progress, dontUpload: true)` sounds like the safe first
# step and is not the right one. It validates **the plan it is given**, not
# whether that plan fits this board, and it needs a context object nobody has
# identified. A read exercises exactly the same chain - link, Programmer,
# layout, transfer - and cannot write anything. kb/16 has said so since the
# architecture was first mapped; this is that experiment, now that PYB.UE
# exists to supply a Programmer with a real layout.
#
# probe_programmer.py established that UE takes `Func<A.POT>` - a factory for
# the HID link - so this is the first step that genuinely needs the mod.
#
# ---------------------------------------------------------------------------
# WHAT THIS DOES AND DOES NOT DO
#
#   does:     opens a HID link, builds a Programmer, Initialize(), reads the
#             user-mode version, then AX() to pull the settings image back
#   does NOT: call PerformUpload, write settings, write firmware, erase
#             anything, or change a single byte on the device
#
# Initialize() sends `get version`, which is a query. AX() is the download
# half of the protocol - the same thing EScribe does when you click
# "Download Settings from Device". **Nothing here can modify the mod.**
#
# Close any other tool holding the device first; kb/16 records that a second
# HID handle makes replies interleave.
# ---------------------------------------------------------------------------

PORT_FILE = "dna-port.txt"    # HID: + base64 of vid'pid'serial - keeps the serial out of the repo
DEVICE, VERSION = 109, 1
EXPECT_VERSION = 311105588    # from EScribe's own debug log

lines = []
def say(s):
    try: lines.append(str(s))
    except: lines.append("<unprintable>")

def _out_path():
    try: return Directories.Documents.Path + "\\read-probe.txt"
    except Exception: return "read-probe.txt"

def _write():
    txt = "\n".join(lines)
    try:
        f = open(_out_path(), "w"); f.write(txt); f.close()
        UI.Message("report: " + _out_path())
    except:
        try: UI.ShowTextInEditor(txt)
        except: pass

import clr
from System import AppDomain, Array, Object, Func
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
        if t.Name in ("GGQ","UWB","PYB","POT","BGQ") and t.Name not in T: T[t.Name] = t

# ---- A. the PYB, device-free (proven) ----
say("=== A. build the PYB (no device) ===")
pyb = None
try:
    clr.AddReference("System.Xml.Linq")
    from System.Xml.Linq import XElement
    el = XElement.Parse("<DESabertooth Device=\"%d\" Version=\"%d\" />" % (DEVICE, VERSION))
    gc = [c for c in T["GGQ"].GetConstructors(FLAGS)
          if len(c.GetParameters()) == 1
          and c.GetParameters()[0].ParameterType.Name == "XElement"][0]
    ggq = gc.Invoke(Array[Object]([el]))
    fe = [m for m in T["UWB"].GetMethods(FLAGS)
          if m.Name == "FE" and m.IsStatic and len(m.GetParameters()) == 1
          and m.GetParameters()[0].ParameterType.Name == "GGQ"][0]
    dwb = fe.Invoke(None, Array[Object]([ggq]))
    pyb = dwb.GetType().GetMethod("JSL", FLAGS).Invoke(dwb, Array[Object]([None, ggq, None]))
    say("  GGQ %r -> %s -> %s" % (ggq, dwb.GetType().Name, pyb.GetType().Name))
except Exception, e:
    say("  FAILED: %s" % e); _write(); raise SystemExit

# ---- B. open the link ----
say("")
say("=== B. open the HID link ===")
pot = None
# Build the port string from the connected device rather than from a file.
# kb/16: "HID:" + base64 of "<vid_decimal>'<pid_decimal>'<serial>". Deriving it
# here means no setup step, and the serial stays in memory - it is never
# written to disk, printed, or put anywhere near the repo (kb/12).
port = None
try:
    clr.AddReference("HidSharp")
    from HidSharp import DeviceList
    from System import Convert
    from System.Text import Encoding
    devs = [d for d in DeviceList.Local.GetHidDevices(0x268B, 0x0433)]
    say("  HID devices matching VID_268B/PID_0433: %d" % len(devs))
    for d in devs:
        try: serial = d.GetSerialNumber()
        except Exception: serial = None
        if not serial: continue
        raw = "%d'%d'%s" % (9867, 1075, serial)
        port = "HID:" + Convert.ToBase64String(Encoding.UTF8.GetBytes(raw))
        say("  built the port string from the live device (%d chars, serial not printed)" % len(port))
        break
except Exception, e:
    say("  could not enumerate HID devices: %s" % e)

if port is None:
    try:
        port = open(PORT_FILE).read().strip()
        say("  fell back to %s (%d chars)" % (PORT_FILE, len(port)))
    except Exception, e:
        say("  no port string: enumeration found nothing and %s is absent (%s)" % (PORT_FILE, e))
        say("  Is the mod plugged in? kb/16: all four interfaces read Present: False when it is not.")
        _write(); raise SystemExit
try:
    fe2 = None
    for t in (T.get("BGQ"), T.get("POT")):
        if t is None: continue
        for m in t.GetMethods(FLAGS):
            if m.Name == "FE" and m.IsStatic and len(m.GetParameters()) == 4:
                fe2 = m
    if fe2 is None:
        say("  the 4-argument FE opener was not found"); _write(); raise SystemExit
    pot = fe2.Invoke(None, Array[Object]([port, 9867, 1075, 0]))
    say("  link -> %s" % (pot.GetType().FullName if pot else "None"))
except Exception, e:
    say("  FAILED: %s" % e); _write(); raise SystemExit

# ---- C. a Programmer that carries the layout ----
say("")
say("=== C. PYB.UE(Func<POT> -> our link, n) ===")
occ = None
try:
    pyPOT = clr.GetPythonType(T["POT"])
    def _give_link(): return pot
    factory = Func[pyPOT](_give_link)
    ue = [m for m in T["PYB"].GetMethods(FLAGS) if m.Name == "UE"][0]
    for n in (0, 1, 2, 3):
        try:
            occ = ue.Invoke(pyb, Array[Object]([factory, n]))
            say("  UE(factory, %d) -> %s" % (n, occ.GetType().FullName if occ else "None"))
            if occ is not None: break
        except Exception, e:
            m = str(e)
            try: m = str(e.clsException.InnerException or e.clsException)
            except: pass
            say("  UE(factory, %d) failed: %s" % (n, m.split("\n")[0]))
except Exception, e:
    say("  FAILED: %s" % e)

if occ is None:
    say("")
    say("  no Programmer - stopping before anything else.")
    _write(); raise SystemExit

say("")
say("=== does it carry the layout? ===")
for nm in ("NM", "IE"):
    try:
        pr = occ.GetType().GetProperty(nm, FLAGS)
        if pr is None: continue
        v = pr.GetValue(occ, None)
        if v is None:
            say("  %s -> None" % nm); continue
        say("  %s -> %s  PCSizeUsed=%s regions=%s"
            % (nm, v.GetType().Name, v.PCSizeUsed, len([r for r in v.Regions])))
    except Exception, e:
        say("  %s: %s" % (nm, e))

# ---- D. Initialize and read the version ----
say("")
say("=== D. Initialize() and UserModeVersion  (a query, writes nothing) ===")
try:
    occ.GetType().GetMethod("Initialize", FLAGS).Invoke(occ, Array[Object]([]))
    say("  Initialize() returned")
except Exception, e:
    m = str(e)
    try: m = str(e.clsException.InnerException or e.clsException)
    except: pass
    say("  Initialize() failed: %s" % m.split("\n")[0])
try:
    pr = occ.GetType().GetProperty("UserModeVersion", FLAGS)
    v = pr.GetValue(occ, None) if pr else None
    say("  UserModeVersion = %s   (expect %d)" % (v, EXPECT_VERSION))
    if v is not None and int(v) == EXPECT_VERSION:
        say("  *** THE LINK IS GENUINELY UP ***")
except Exception, e:
    say("  UserModeVersion failed: %s" % e)

# ---- E. the read ----
say("")
say("=== E. AX() - download the settings image. READ ONLY ===")
try:
    ax = None
    for m in occ.GetType().GetMethods(FLAGS):
        if m.Name == "AX": ax = m
    if ax is None:
        say("  AX not found")
    else:
        ps = ax.GetParameters()
        say("  AX(%s)" % ", ".join("%s %s" % (p.ParameterType.Name, p.Name) for p in ps))
        args = [None] * len(ps)
        img = ax.Invoke(occ, Array[Object](args))
        if img is None:
            say("  -> None")
        else:
            say("  -> %s" % img.GetType().Name)
            try: say("  length = %s bytes" % len(img))
            except: pass
except Exception, e:
    m = str(e)
    try: m = str(e.clsException.InnerException or e.clsException)
    except: pass
    say("  AX failed: %s" % m.split("\n")[0])

say("")
say("Nothing was written to the device by this script.")
_write()
