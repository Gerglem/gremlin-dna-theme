# Step 3: open a link, get a Programmer that HAS the layout, and READ.
#
# Run: Device Monitor -> Diagnostics -> Advanced -> Run Script.
# **Plug the mod in.** The port string is derived from the connected device.
#
# ---------------------------------------------------------------------------
# WHY A READ AND NOT THE DRY RUN
#
# PerformUpload(ctx, progress, dontUpload: true) sounds like the safe first
# step and is not. It validates the plan it is given, not whether that plan
# fits this board, and needs a context object nobody has identified. A read
# exercises the same chain - link, Programmer, layout, transfer - and cannot
# write. kb/16 has said so since the architecture was mapped; this is that
# experiment, now that PYB.UE can supply a Programmer with a real layout.
#
# WHAT THIS DOES AND DOES NOT DO
#   does:     opens a HID link, builds a Programmer, Initialize(), reads the
#             user-mode version, then AX() to pull the settings image back
#   does NOT: call PerformUpload, write settings or firmware, erase anything,
#             or change a single byte on the device
#
# Two things learned the hard way, both fixed here:
#   * `raise SystemExit` makes the host pop a "Script Error" dialog. Exits go
#     through a private exception caught at the bottom instead.
#   * HidSharp is **obfuscated in place** (kb/16), so `from HidSharp import ...`
#     fails - its public namespace is not there. The serial comes from Windows
#     via WMI instead, which is not obfuscated. It stays in memory: never
#     written, never printed (kb/12).
# ---------------------------------------------------------------------------

PORT_FILE = "dna-port.txt"    # optional fallback; normally not needed
DEVICE, VERSION = 109, 1
EXPECT_VERSION = 311105588    # from EScribe's own debug log

lines = []
def say(s):
    try: lines.append(str(s))
    except: lines.append("<unprintable>")

class _Done(Exception):
    pass

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


def main():
    T = {}
    for a in AppDomain.CurrentDomain.GetAssemblies():
        for t in types_of(a):
            if t.Name in ("GGQ", "UWB", "PYB", "POT", "BGQ") and t.Name not in T:
                T[t.Name] = t

    # ---- A. the PYB, device-free (proven) ----
    say("=== A. build the PYB (no device) ===")
    try:
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
        say("  GGQ %r -> %s -> %s" % (ggq, dwb.GetType().Name, pyb.GetType().Name))
    except Exception, e:
        say("  FAILED: %s" % e); raise _Done()

    # ---- B. the port string, from Windows ----
    say("")
    say("=== B. find the device and open the link ===")
    port = None
    try:
        clr.AddReference("System.Management")
        from System.Management import ManagementObjectSearcher
        from System import Convert
        from System.Text import Encoding
        q = "SELECT DeviceID FROM Win32_PnPEntity WHERE DeviceID LIKE '%VID_268B%PID_0433%'"
        ids = []
        for o in ManagementObjectSearcher(q).Get():
            try: ids.append(str(o["DeviceID"]))
            except: pass
        say("  Windows reports %d matching USB entries" % len(ids))
        for did in ids:
            if "MI_" in did:
                continue                       # want the composite parent, not an interface
            serial = did.split("\\")[-1]
            if not serial:
                continue
            raw = "%d'%d'%s" % (9867, 1075, serial)
            port = "HID:" + Convert.ToBase64String(Encoding.UTF8.GetBytes(raw))
            say("  port string built from the live device (%d chars; serial not printed)" % len(port))
            break
        if port is None and ids:
            say("  only interface entries (MI_) were returned, no composite parent")
    except Exception, e:
        say("  WMI lookup failed: %s" % e)

    if port is None:
        try:
            port = open(PORT_FILE).read().strip()
            say("  fell back to %s (%d chars)" % (PORT_FILE, len(port)))
        except Exception, e:
            say("  no port string available (%s)" % e)
            say("  Is the mod plugged in? kb/16: all four interfaces read Present: False when it is not.")
            raise _Done()

    # The opener takes SEVEN arguments, not four - an earlier version of this
    # probe searched for a 4-parameter FE and found nothing. The working call
    # is the one probe_open_link.py proved:
    #   BGQ.FE(port, vid, pid, ver, OpenConfiguration, 1, enum0) -> POT
    # CSH and IGI are HidSharp types. The assembly is present and named
    # HidSharp, but its *types* are obfuscated (kb/16), which is why they are
    # located by reflection rather than imported.
    pot = None
    try:
        from System import Activator, Enum
        hid = None
        for a in AppDomain.CurrentDomain.GetAssemblies():
            try:
                if a.GetName().Name == "HidSharp": hid = a
            except: pass
        CSH = IGI = None
        if hid is not None:
            for t in types_of(hid):
                if t.Name == "CSH": CSH = t
                if t.Name == "IGI": IGI = t
        say("  BGQ=%s CSH=%s IGI=%s"
            % (T.get("BGQ") is not None, CSH is not None, IGI is not None))

        fe2 = None
        if T.get("BGQ") is not None:
            for m in T["BGQ"].GetMethods(FLAGS):
                if m.Name == "FE" and m.ReturnType.Name == "POT":
                    fe2 = m; break
        if fe2 is None:
            say("  BGQ.FE returning POT was not found"); raise _Done()
        say("  FE(%s)" % ", ".join(x.ParameterType.Name for x in fe2.GetParameters()))

        cfg = Activator.CreateInstance(CSH) if CSH is not None else None
        igi0 = Enum.ToObject(IGI, 0) if IGI is not None else None
        for vid, pid, ver in ((9867, 1075, 0), (9867, 1075, 257), (0, 0, 0)):
            try:
                pot = fe2.Invoke(None, Array[Object]([port, vid, pid, ver, cfg, 1, igi0]))
                say("  FE(port, %d, %d, %d) -> %s"
                    % (vid, pid, ver, pot.GetType().FullName if pot else "None"))
                if pot is not None: break
            except Exception, e:
                inner = None
                try: inner = e.clsException.InnerException
                except: pass
                say("  FE(port, %d, %d, %d) threw: %s"
                    % (vid, pid, ver, inner.Message if inner else e))
        if pot is None:
            say("  no link"); raise _Done()
    except _Done:
        raise
    except Exception, e:
        say("  FAILED: %s" % e); raise _Done()

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
        raise _Done()

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
            img = ax.Invoke(occ, Array[Object]([None] * len(ps)))
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


try:
    main()
except _Done:
    pass
except Exception, e:
    say("UNEXPECTED: %s" % e)
_write()
