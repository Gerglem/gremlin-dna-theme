# Build a PYB from our own board identity and read the real flash layout.
#
# Run: Device Monitor -> Diagnostics -> Advanced -> Run Script.
#
# ---------------------------------------------------------------------------
# THE CHAIN, NOW FULLY RESOLVED (kb/16)
#
#   XElement("<DESabertooth Device='109' Version='1'/>")  -> GGQ   ctor(XElement)
#   UWB.FE(ggq)                                           -> DWB   static factory
#   dwb.JSL(None, ggq, None)                              -> PYB
#   pyb.PE()                                              -> LogicalLayout
#
# probe_dwb3.py found the two pieces that were missing:
#   * UWB.FE(GGQ) -> DWB, static - the dispatcher. Hand it the board identity
#     and it returns the right subclass, so none of the 25 has to be
#     identified by hand.
#   * DWB.DSL(GGQ) -> Boolean - "do I handle this board?", which this script
#     uses as an independent cross-check on what FE returns.
#
# Device 109 version 1 is what every .ecig of ours carries as its root element
# and what EScribe's log calls "device code 109.1, Evolv DNA 100 Color".
#
# ---------------------------------------------------------------------------
# SAFETY - this is the first probe that exercises the upload-path objects
#
# It constructs a GGQ, asks for a DWB, builds a PYB and reads its layout.
# That is real work inside EScribe's own code, and more than the earlier
# probes did. What it still does NOT do:
#
#   * no link is opened to the mod - no FE(port,...), no Stream, no Initialize
#   * no Programmer is built (PYB.UE is NOT called)
#   * nothing is uploaded, written, erased or sent, not even a dry run
#   * PE() is a getter for the layout; it reads a map, it does not apply one
#
# **The mod is not involved at all.** It need not even be plugged in. The
# worst realistic outcome remains an EScribe restart (kb/07 #28).
#
# Every step is wrapped, and the script stops at the first one that fails -
# reporting how far it got, which is the useful part either way.
# ---------------------------------------------------------------------------

DEVICE  = 109
VERSION = 1

lines = []
def say(s):
    try: lines.append(str(s))
    except: lines.append("<unprintable>")

def _out_path():
    try: return Directories.Documents.Path + "\\layout-probe.txt"
    except Exception: return "layout-probe.txt"

def _write():
    txt = "\n".join(lines)
    try:
        f = open(_out_path(), "w"); f.write(txt); f.close()
        UI.Message("report: " + _out_path())
    except:
        try: UI.ShowTextInEditor(txt)
        except: pass

import clr
from System import AppDomain, Array, Object, Activator
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
        if t.Name in ("GGQ", "UWB", "DWB", "PYB") and t.Name not in T:
            T[t.Name] = t
say("=== types ===")
for n in ("GGQ", "UWB", "DWB", "PYB"):
    say("  %-4s %s" % (n, "found" if n in T else "MISSING"))

# ---- 1. the board identity, from our own .ecig root element ----
say("")
say("=== 1. GGQ from an .ecig root element ===")
ggq = None
try:
    clr.AddReference("System.Xml.Linq")
    from System.Xml.Linq import XElement
    xml = "<DESabertooth Device=\"%d\" Version=\"%d\" />" % (DEVICE, VERSION)
    el = XElement.Parse(xml)
    say("  parsed: %s" % xml)
    ctor = None
    for c in T["GGQ"].GetConstructors(FLAGS):
        ps = c.GetParameters()
        if len(ps) == 1 and ps[0].ParameterType.Name == "XElement":
            ctor = c
    if ctor is None:
        say("  no ctor(XElement) - stopping"); _write(); raise SystemExit
    ggq = ctor.Invoke(Array[Object]([el]))
    say("  GGQ built -> %r" % ggq)
except Exception, e:
    say("  FAILED: %s" % e); _write(); raise SystemExit

# ---- 2. the dispatcher ----
say("")
say("=== 2. UWB.FE(ggq) -> DWB ===")
dwb = None
try:
    m = None
    for c in T["UWB"].GetMethods(FLAGS):
        if c.Name == "FE" and c.IsStatic:
            ps = c.GetParameters()
            if len(ps) == 1 and ps[0].ParameterType.Name == "GGQ": m = c
    if m is None:
        say("  UWB.FE(GGQ) not found")
    else:
        dwb = m.Invoke(None, Array[Object]([ggq]))
        say("  -> %s" % (dwb.GetType().FullName if dwb is not None else "None"))
except Exception, e:
    say("  FAILED: %s" % e)

# ---- 3. cross-check with DSL on every concrete subclass ----
say("")
say("=== 3. cross-check: which subclasses say DSL(ggq) == True ===")
try:
    agree = []
    for a in AppDomain.CurrentDomain.GetAssemblies():
        for t in types_of(a):
            try:
                if t.IsAbstract or not t.IsSubclassOf(T["DWB"]): continue
            except: continue
            try:
                o = Activator.CreateInstance(t)
                d = t.GetMethod("DSL", FLAGS)
                if d is None: continue
                if d.Invoke(o, Array[Object]([ggq])):
                    agree.append(t.Name)
            except: continue
    say("  DSL true for: %s" % (", ".join(agree) if agree else "NONE"))
    if dwb is not None:
        say("  dispatcher gave: %s   agreement=%s"
            % (dwb.GetType().Name, dwb.GetType().Name in agree))
except Exception, e:
    say("  FAILED: %s" % e)

# ---- 4. build the PYB ----
say("")
say("=== 4. dwb.JSL(None, ggq, None) -> PYB ===")
pyb = None
if dwb is None:
    say("  no DWB - skipped")
else:
    try:
        j = dwb.GetType().GetMethod("JSL", FLAGS)
        pyb = j.Invoke(dwb, Array[Object]([None, ggq, None]))
        say("  -> %s" % (pyb.GetType().FullName if pyb is not None else "None"))
    except Exception, e:
        say("  FAILED: %s" % e)
        try: say("  inner: %s" % e.clsException.InnerException)
        except: pass

# ---- 5. THE PRIZE: the real flash layout ----
say("")
say("=== 5. pyb.PE() -> LogicalLayout ===")
if pyb is None:
    say("  no PYB - skipped")
else:
    try:
        layout = pyb.GetType().GetMethod("PE", FLAGS).Invoke(pyb, Array[Object]([]))
        if layout is None:
            say("  null layout - the PYB may need the document argument JSL was given as None")
        else:
            say("  PCSize=%s  PCSizeUsed=%s" % (layout.PCSize, layout.PCSizeUsed))
            i = 0
            for r in layout.Regions:
                say("   [%2d] size %7d  dev 0x%06X  pc 0x%06X  ro=%-5s hashWhole=%-5s chunk=%-6s tag=%s"
                    % (i, r.Size, r.DeviceOffset, r.PCOffset, r.ReadOnly,
                       r.HashWholeRegion, r.HashChunkSize, r.Tag))
                i += 1
            say("  regions: %d" % i)
    except Exception, e:
        say("  FAILED: %s" % e)
        try: say("  inner: %s" % e.clsException.InnerException)
        except: pass

_write()
