# The read, second attempt: hand the Programmer a version before asking it to talk.
#
# Run: Device Monitor -> Diagnostics -> Advanced -> Run Script.
# Mod plugged in. READ ONLY.
#
# ---------------------------------------------------------------------------
# WHERE THE FIRST ATTEMPT GOT TO
#
#     UE(factory, 128) -> A.ECC        a Programmer, with our live link
#     Initialize() returned            no exception
#     UserModeVersion = None
#     AX(IProgressMonitor, Boolean[])  -> TimeoutException
#
# Two things to take from that.
#
# 1. **UserModeVersion = None is expected, not a failure.** kb/16 established
#    by reading the IL that Initialize() is 36 bytes of wiring and performs no
#    handshake - DEScribe.Core is the orchestrator that sends `get version`
#    and then *sets* this property. Nothing in DEScribe.Upload ever writes it.
#    So the Programmer is sitting there not knowing what it is talking to,
#    which is a plausible reason for a read to hang.
#
# 2. **AX's second argument is a Boolean[]** and we passed null. If it selects
#    which regions to transfer, null may mean "nothing", or may be dereferenced
#    into a bad request.
#
# This tries, in order: dump every property on the Programmer (the last run
# printed nothing because it skipped missing ones silently - so we still do
# not know whether it carries the layout); set UserModeVersion ourselves;
# then AX with a properly shaped Boolean[].
#
# **At most two AX attempts**, because each timeout costs real time.
#
# SAFETY: Initialize() and AX() are the download half. No PerformUpload, no
# write, no erase. Setting UserModeVersion writes to a property on our own
# in-memory object, not to the device.
# ---------------------------------------------------------------------------

DEVICE, VERSION = 109, 1
EXPECT_VERSION = 311105588
UE_ADDRESS = 128          # bit 7 set; swept and confirmed in probe_ue_sweep

lines = []
def say(s):
    try: lines.append(str(s))
    except: lines.append("<unprintable>")

class _Done(Exception):
    pass

def _out_path():
    try: return Directories.Documents.Path + "\\read-probe2.txt"
    except Exception: return "read-probe2.txt"

def _write():
    txt = "\n".join(lines)
    try:
        f = open(_out_path(), "w"); f.write(txt); f.close()
        UI.Message("report: " + _out_path())
    except:
        try: UI.ShowTextInEditor(txt)
        except: pass

import clr
from System import AppDomain, Array, Object, Func, Boolean, UInt32
from System.Reflection import BindingFlags
FLAGS = (BindingFlags.Public | BindingFlags.NonPublic |
         BindingFlags.Static | BindingFlags.Instance)

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

    # ---- build the PYB and open the link (both proven) ----
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
    say("PYB: %s" % pyb.GetType().Name)

    from System import Activator, Enum
    hid = None
    for a in AppDomain.CurrentDomain.GetAssemblies():
        try:
            if a.GetName().Name == "HidSharp": hid = a
        except: pass
    CSH = IGI = None
    for t in types_of(hid) if hid else []:
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
        say("no device found - is it plugged in?"); raise _Done()
    say("port string: %d chars (serial not printed)" % len(port))

    feo = None
    for m in T["BGQ"].GetMethods(FLAGS):
        if m.Name == "FE" and m.ReturnType.Name == "POT": feo = m; break
    cfg = Activator.CreateInstance(CSH) if CSH is not None else None
    igi0 = Enum.ToObject(IGI, 0) if IGI is not None else None
    pot = feo.Invoke(None, Array[Object]([port, 9867, 1075, 0, cfg, 1, igi0]))
    say("link: %s" % (pot.GetType().FullName if pot else "None"))
    if pot is None: raise _Done()

    pyPOT = clr.GetPythonType(T["POT"])
    def _give_link(): return pot
    ue = [m for m in T["PYB"].GetMethods(FLAGS) if m.Name == "UE"][0]
    occ = ue.Invoke(pyb, Array[Object]([Func[pyPOT](_give_link), UE_ADDRESS]))
    say("Programmer: %s" % occ.GetType().FullName)

    # ---- 1. everything the Programmer exposes ----
    say("")
    say("=== every property on the Programmer ===")
    for pr in sorted(occ.GetType().GetProperties(FLAGS), key=lambda x: x.Name):
        tn = pr.PropertyType.Name
        val = "?"
        try:
            if len(pr.GetIndexParameters()) == 0:
                v = pr.GetValue(occ, None)
                val = "None" if v is None else (str(v) if tn in
                      ("Int32", "UInt32", "Boolean", "String", "Byte") else v.GetType().Name)
        except Exception, e:
            val = "<%s>" % err(e)
        say("  %-22s %-16s = %s" % (pr.Name, tn, val))

    # ---- 2. give it a version ----
    say("")
    say("=== set UserModeVersion = %d ===" % EXPECT_VERSION)
    try:
        pr = occ.GetType().GetProperty("UserModeVersion", FLAGS)
        if pr is None:
            say("  property not found")
        elif not pr.CanWrite:
            say("  property is read-only; looking for a setter method")
            for m in occ.GetType().GetMethods(FLAGS):
                if m.Name == "set_UserModeVersion":
                    say("    %s(%s)" % (m.Name, ", ".join(p.ParameterType.Name
                                                          for p in m.GetParameters())))
        else:
            pr.SetValue(occ, UInt32(EXPECT_VERSION), None)
            say("  now reads: %s" % pr.GetValue(occ, None))
    except Exception, e:
        say("  failed: %s" % err(e))

    # ---- 3. AX, at most twice ----
    say("")
    say("=== AX() - download. READ ONLY. at most two attempts ===")
    ax = None
    for m in occ.GetType().GetMethods(FLAGS):
        if m.Name == "AX": ax = m
    if ax is None:
        say("  AX not found"); raise _Done()
    say("  AX(%s)" % ", ".join("%s %s" % (p.ParameterType.Name, p.Name or "?")
                               for p in ax.GetParameters()))

    nregions = 3
    try:
        layout = pyb.GetType().GetMethod("PE", FLAGS).Invoke(pyb, Array[Object]([]))
        nregions = len([r for r in layout.Regions])
    except: pass
    say("  layout has %d regions, so trying a Boolean[%d] of True" % (nregions, nregions))

    flags_all = Array[Boolean]([True] * nregions)
    for label, arg in (("all-true Boolean[%d]" % nregions, flags_all),
                       ("empty Boolean[0]", Array[Boolean]([]))):
        say("")
        say("  -- AX(None, %s) --" % label)
        try:
            img = ax.Invoke(occ, Array[Object]([None, arg]))
            if img is None:
                say("     -> None")
            else:
                say("     -> %s" % img.GetType().Name)
                try: say("     length = %s bytes" % len(img))
                except: pass
                say("     *** THE READ WORKED ***")
                break
        except Exception, e:
            say("     threw: %s" % err(e))

    say("")
    say("Nothing was written to the device by this script.")


try:
    main()
except _Done:
    pass
except Exception, e:
    say("UNEXPECTED: %s" % err(e))
_write()
