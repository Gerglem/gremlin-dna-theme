# In-process: open the device stream using EScribe's own opener, attach it to
# a Programmer, and read the version back.
#
# Run: Device Monitor -> Diagnostics -> Advanced -> Run Script.
#
# What this DOES touch: it opens a link and calls Initialize(), then reads
# UserModeVersion. That is the read-only half of kb/16's risk boundary.
# It does NOT call PerformUpload, writes no settings and no firmware.
#
# The port string is read from a scratchpad file so the board serial is never
# written into the repo or this script.

PORT_FILE = "dna-port.txt"   # one line: HID: plus base64 of vid'pid'serial - see kb/16

def _out_path():
    """Report destination. Uses Evolv's own Documents path (kb/14), so nothing
    here depends on a particular machine or user name."""
    try:
        return Directories.Documents.Path + "\\escribe-probe.txt"
    except Exception:
        return "escribe-probe.txt"


lines = []
def say(s):
    try: lines.append(str(s))
    except: lines.append("<unprintable>")

import clr
from System import AppDomain, Array, Object, Int32, Enum, Activator
from System.Reflection import BindingFlags
ALL = (BindingFlags.Public | BindingFlags.NonPublic |
       BindingFlags.Static | BindingFlags.Instance)

def asm(name):
    for a in AppDomain.CurrentDomain.GetAssemblies():
        try:
            if a.GetName().Name == name: return a
        except: pass
    return None

def find(a, n):
    if a is None: return None
    try: types = a.GetTypes()
    except Exception, e:
        try: types = [t for t in e.clsException.Types if t is not None]
        except: return None
    for t in types:
        if t.Name == n: return t
    return None

say("=== open-the-link probe ===")
common = asm("DimensionEngineering.Common")
hidsharp = asm("HidSharp")
upload = asm("DEScribe.Upload")
say("assemblies loaded: common=%s hidsharp=%s upload=%s"
    % (common is not None, hidsharp is not None, upload is not None))

port = open(PORT_FILE).read().strip()
say("port string read: %d chars, starts %r" % (len(port), port[:4]))

BGQ = find(common, "BGQ")
CSH = find(hidsharp, "CSH")
IGI = find(hidsharp, "IGI")
say("BGQ=%s CSH=%s IGI=%s" % (BGQ is not None, CSH is not None, IGI is not None))

FE = None
if BGQ is not None:
    for m in BGQ.GetMethods(ALL):
        if m.Name == "FE" and m.ReturnType.Name == "POT":
            FE = m; break
say("FE found: %s" % (FE is not None))

pot = None
if FE is not None:
    cfg = Activator.CreateInstance(CSH) if CSH is not None else None
    igi0 = Enum.ToObject(IGI, 0) if IGI is not None else None
    for vid, pid, ver in [(9867, 1075, 0), (9867, 1075, 257), (0, 0, 0)]:
        try:
            args = Array[Object]([port, vid, pid, ver, cfg, 1, igi0])
            pot = FE.Invoke(None, args)
            say("FE(port, %d, %d, %d) -> %s" % (vid, pid, ver, pot.GetType().FullName if pot else "<null>"))
            if pot is not None: break
        except Exception, e:
            inner = None
            try: inner = e.clsException.InnerException
            except: pass
            say("FE(port, %d, %d, %d) threw: %s" % (vid, pid, ver, inner.Message if inner else e))

# ---- attach it to a Programmer and read the version ---------------------
if pot is not None:
    say("")
    say("=== attach to Programmer ===")
    Prog = find(upload, "Programmer")
    try:
        occ = Prog.GetMethod("CreateForDNAColor", ALL).Invoke(None, Array[Object]([None]))
        say("programmer: %s" % occ.GetType().FullName)
        occ.GetType().GetProperty("Stream", ALL).SetValue(occ, pot, None)
        say("Stream assigned")
        occ.GetType().GetMethod("Initialize", ALL).Invoke(occ, Array[Object]([]))
        say("Initialize() returned")
        v = occ.GetType().GetProperty("UserModeVersion", ALL).GetValue(occ, None)
        say("UserModeVersion = %r   (expect 311105588)" % v)
    except Exception, e:
        inner = None
        try: inner = e.clsException.InnerException
        except: pass
        say("failed: %s" % (inner.Message if inner else e))

txt = "\n".join(lines)
try:
    f = open(_out_path(), "w"); f.write(txt); f.close()
    UI.Message("report: " + _out_path())
except:
    try: UI.ShowTextInEditor(txt)
    except: pass
