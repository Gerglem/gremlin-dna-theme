# Can we BUILD a PYB instead of finding one?
#
# Run: Device Monitor -> Diagnostics -> Advanced -> Run Script.
#
# ---------------------------------------------------------------------------
# WHY THIS, AND NOT MORE HUNTING
#
# Three probes have now looked for a live PYB inside EScribe and found none.
# The third one explains why: with WinForms loaded, Application.OpenForms
# contains exactly **one** form - Device Monitor's own window. The main EScribe
# window, and therefore the open document, is not reachable from the script
# host at all. Hunting harder will not fix that.
#
# So stop hunting and build one. kb/16 mapped the chain:
#
#     .ecig root -> GGQ -> DWB.JSL(?, ggq, null) -> PYB -> PYB.UE(f, i) -> OCC
#
# and found it blocked because **DWB is abstract**, so JSL cannot be called
# without a concrete subclass. Nobody has yet looked for one. If a concrete
# subclass exists, a PYB can be constructed from one of our own .ecig files and
# the live document stops mattering.
#
# ---------------------------------------------------------------------------
# SAFETY
#
# This reads **metadata only**: BaseType, IsAbstract, GetConstructors,
# GetParameters. It never reads a field or property value and never invokes
# anything, so no static constructor can fire - which is what froze EScribe on
# probe 2 (kb/07 #28). Nothing touches the mod.
#
# It also prints no window titles: EScribe puts the device serial in them
# (kb/12).
# ---------------------------------------------------------------------------

lines = []
def say(s):
    try: lines.append(str(s))
    except: lines.append("<unprintable>")

def _out_path():
    try: return Directories.Documents.Path + "\\dwb-probe.txt"
    except Exception: return "dwb-probe.txt"

import clr
from System import AppDomain
from System.Reflection import BindingFlags
from System.Diagnostics import Process

FLAGS = (BindingFlags.Public | BindingFlags.NonPublic |
         BindingFlags.Static | BindingFlags.Instance)

def types_of(a):
    try: return a.GetTypes()
    except Exception, e:
        try: return [t for t in e.clsException.Types if t is not None]
        except: return []

# ---- 1. where are we actually running? ----
say("=== host ===")
try:
    pr = Process.GetCurrentProcess()
    say("  process: %s   pid %s" % (pr.ProcessName, pr.Id))
except Exception, e:
    say("  process: unknown (%s)" % e)

asms = {}
for a in AppDomain.CurrentDomain.GetAssemblies():
    try: asms[a.GetName().Name] = a
    except: pass
say("  DEScribe assemblies loaded:")
for n in sorted(asms):
    if n.startswith("DEScribe") or n.startswith("Dimension"):
        say("    " + n)
say("  DEScribe.UI present: %s   <- if False, the main window is out of reach"
    % ("DEScribe.UI" in asms))

# ---- 2. the types the chain needs ----
say("")
say("=== chain types ===")
want = ("DWB", "PYB", "GGQ", "FWB", "OCC", "LogicalLayout")
found = {}
for n, a in asms.items():
    for t in types_of(a):
        if t.Name in want and t.Name not in found:
            found[t.Name] = t
for n in want:
    t = found.get(n)
    if t is None:
        say("  %-14s NOT FOUND" % n); continue
    say("  %-14s %s   abstract=%s  sealed=%s  base=%s"
        % (n, t.Assembly.GetName().Name, t.IsAbstract, t.IsSealed,
           t.BaseType.Name if t.BaseType is not None else "-"))

# ---- 3. THE QUESTION: is there a concrete DWB? ----
say("")
say("=== concrete subclasses of DWB ===")
DWB = found.get("DWB")
if DWB is None:
    say("  DWB not found at all")
else:
    n = 0
    for an, a in asms.items():
        for t in types_of(a):
            try:
                if t is DWB or not t.IsSubclassOf(DWB): continue
            except: continue
            n += 1
            say("  %s.%s   abstract=%s" % (an, t.Name, t.IsAbstract))
            if t.IsAbstract: continue
            try:
                for c in t.GetConstructors(FLAGS):
                    ps = ", ".join("%s %s" % (p.ParameterType.Name, p.Name)
                                   for p in c.GetParameters())
                    say("      ctor(%s)" % ps)
            except Exception, e:
                say("      ctor list failed: %s" % e)
    say("  total subclasses: %d" % n)
    if n == 0:
        say("  NONE - DWB has no subclass in the loaded assemblies. Either the")
        say("  concrete one lives in an assembly not loaded here, or JSL is")
        say("  reached some other way.")

# ---- 4. the signatures we would be calling ----
say("")
say("=== signatures ===")
for tn, mn in (("DWB", "JSL"), ("PYB", "UE"), ("PYB", "PE"), ("FWB", "get_DE")):
    t = found.get(tn)
    if t is None: continue
    try:
        got = False
        for m in t.GetMethods(FLAGS):
            if m.Name != mn: continue
            ps = ", ".join("%s %s" % (p.ParameterType.Name, p.Name)
                           for p in m.GetParameters())
            say("  %s.%s(%s) -> %s   static=%s"
                % (tn, mn, ps, m.ReturnType.Name, m.IsStatic))
            got = True
        if not got: say("  %s.%s  not found" % (tn, mn))
    except Exception, e:
        say("  %s.%s  failed: %s" % (tn, mn, e))

GGQ = found.get("GGQ")
if GGQ is not None:
    say("")
    say("=== GGQ constructors (the board identity, built from an .ecig root) ===")
    try:
        for c in GGQ.GetConstructors(FLAGS):
            ps = ", ".join("%s %s" % (p.ParameterType.Name, p.Name)
                           for p in c.GetParameters())
            say("  ctor(%s)" % ps)
    except Exception, e:
        say("  failed: %s" % e)

txt = "\n".join(lines)
try:
    f = open(_out_path(), "w"); f.write(txt); f.close()
    UI.Message("report: " + _out_path())
except:
    try: UI.ShowTextInEditor(txt)
    except: pass
