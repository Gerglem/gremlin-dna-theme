# Identify the DNA100C's DWB subclass - properties, and the dispatcher.
#
# Run: Device Monitor -> Diagnostics -> Advanced -> Run Script.
#
# ---------------------------------------------------------------------------
# WHERE THIS SITS
#
# probe_dwb2.py constructed all 25 concrete DWB subclasses - every one
# succeeded, so the constructors are inert in fact and not just in theory - and
# found that **none of them has a single simple instance field**. They are
# stateless. So the board identity is not stored on the DWB, and there are
# exactly two places left for it:
#
#   A. a **property** returning a constant. That is the natural idiom for a
#      stateless descriptor - `override int SomeCode { get { return 109; } }` -
#      and is checked here first.
#   B. nowhere on the DWB at all, because a **dispatcher** elsewhere maps a
#      device code or a GGQ to the right subclass. Part 2 looks for it by
#      metadata: any method that returns a DWB/XWB, or takes a GGQ.
#
# If B is the answer, the subclass may not need identifying by hand at all -
# we would call the dispatcher and be handed the right one.
#
# ---------------------------------------------------------------------------
# SAFETY
#
# Part 1 **calls property getters** on the 25 instances. That is one step
# further than probe_dwb2 and is the hazard this project already knows about
# (kb/07 #28): a getter can run arbitrary code. Bounded by:
#   * instances only, so no type initializer can fire;
#   * parameterless getters returning simple types only - int/string/bool;
#   * **skips any getter whose name suggests work** (Create/Open/Connect/
#     Upload/Download/Read/Write/Start/Begin/Execute/Perform/Load/Save);
#   * each call wrapped individually, with a wall-clock budget and Stop.
# Part 2 is metadata only.
#
# **Nothing here touches the mod.** No link, no Programmer, no JSL.
# ---------------------------------------------------------------------------

TIME_BUDGET = 30
TARGET      = 109

lines = []
def say(s):
    try: lines.append(str(s))
    except: lines.append("<unprintable>")

def _out_path():
    try: return Directories.Documents.Path + "\\dwb3-probe.txt"
    except Exception: return "dwb3-probe.txt"

import clr
from System import AppDomain, DateTime, Activator
from System.Reflection import BindingFlags

INST  = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance
FLAGS = INST | BindingFlags.Static

try: Script.WillStopIfAsked = True
except: pass
def stop_asked():
    try: return Script.ShouldStop
    except: return False
started = DateTime.Now
def out_of_time():
    try: return (DateTime.Now - started).TotalSeconds > TIME_BUDGET
    except: return False

def types_of(a):
    try: return a.GetTypes()
    except Exception, e:
        try: return [t for t in e.clsException.Types if t is not None]
        except: return []

asms = {}
for a in AppDomain.CurrentDomain.GetAssemblies():
    try: asms[a.GetName().Name] = a
    except: pass

DWB = XWB = None
for n, a in asms.items():
    for t in types_of(a):
        if t.Name == "DWB": DWB = t
        if t.Name == "XWB": XWB = t

SIMPLE  = ("Int32", "Int16", "Byte", "UInt32", "String", "Boolean", "Double", "Single")
DANGER  = ("create", "open", "connect", "upload", "download", "read", "write",
           "start", "begin", "execute", "perform", "load", "save", "send",
           "flash", "erase", "program", "reset", "dispose")

# ---------- part 1: properties on each concrete subclass ----------
say("=== part 1: constant-ish properties on each concrete DWB ===")
say("target device code: %d" % TARGET)
say("")
hits = []
if DWB is None:
    say("  DWB not found")
else:
    cands = []
    for n, a in asms.items():
        for t in types_of(a):
            try:
                if t is DWB or t.IsAbstract or not t.IsSubclassOf(DWB): continue
            except: continue
            cands.append(t)

    for t in cands:
        if out_of_time(): say("  ... TIME BUDGET reached"); break
        if stop_asked():  say("  ... Stop pressed"); break
        try: obj = Activator.CreateInstance(t)
        except Exception, e:
            say("%-6s ctor failed: %s" % (t.Name, e)); continue

        vals = []
        interesting = False
        try: props = obj.GetType().GetProperties(INST)
        except: props = []
        for pr in props:
            try:
                if pr.PropertyType.Name not in SIMPLE: continue
                if len(pr.GetIndexParameters()) != 0: continue
                g = pr.GetGetMethod(True)
                if g is None: continue
                low = pr.Name.lower()
                if any(d in low for d in DANGER): continue
            except: continue
            try: v = pr.GetValue(obj, None)
            except: continue
            if v is None: continue
            sv = str(v)
            if not sv.strip(): continue
            vals.append("%s=%r" % (pr.Name, sv))
            if sv == str(TARGET) or ("100" in sv and "olor" in sv): interesting = True

        mark = "   <<<<< %d" % TARGET if interesting else ""
        say("%-6s %s%s" % (t.Name, (", ".join(vals[:14]) or "(no simple properties either)"), mark))
        if interesting: hits.append(t.Name)

say("")
say("part 1 candidates: %s" % (", ".join(hits) if hits else "NONE"))

# ---------- part 2: who hands out a DWB? ----------
say("")
say("=== part 2: methods that return a DWB/XWB, or take a GGQ ===")
n_found = 0
for an, a in asms.items():
    if not (an.startswith("DEScribe") or an.startswith("Dimension")): continue
    for t in types_of(a):
        try: ms = t.GetMethods(FLAGS)
        except: continue
        for m in ms:
            try:
                rt = m.ReturnType.Name
                ps = m.GetParameters()
                takes_ggq = any(p.ParameterType.Name == "GGQ" for p in ps)
                gives_dwb = rt in ("DWB", "XWB")
                if not (takes_ggq or gives_dwb): continue
                if m.Name == "JSL" and t.Name == "DWB": continue   # already known
                sig = ", ".join("%s %s" % (p.ParameterType.Name, p.Name) for p in ps)
                say("  %-26s %s.%s(%s) -> %s   static=%s"
                    % (an, t.Name, m.Name, sig, rt, m.IsStatic))
                n_found += 1
            except: continue
say("  total: %d" % n_found)
if n_found == 0:
    say("  nothing hands out a DWB and nothing else takes a GGQ - so the")
    say("  subclass is chosen some other way, and trying JSL on each with our")
    say("  own GGQ is the remaining option.")

txt = "\n".join(lines)
try:
    f = open(_out_path(), "w"); f.write(txt); f.close()
    UI.Message("report: " + _out_path())
except:
    try: UI.ShowTextInEditor(txt)
    except: pass
