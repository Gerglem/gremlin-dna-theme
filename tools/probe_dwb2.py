# Which concrete DWB subclass is the DNA 100 Color?
#
# Run: Device Monitor -> Diagnostics -> Advanced -> Run Script.
#
# ---------------------------------------------------------------------------
# WHERE THIS SITS
#
# probe_dwb.py found ~25 concrete subclasses of DWB, all in
# DEScribe.Branding.Evolv, all with a parameterless constructor - one per board
# model. DWB.JSL is the only constructor of a PYB and is an *instance* method,
# so the chain in kb/16 needs one of these. This identifies which.
#
# The target is device code **109.1** - what every .ecig root carries as
# <DESabertooth Device="109" Version="1"> and what EScribe's own log prints as
# "device code 109.1, device Evolv DNA 100 Color".
#
# ---------------------------------------------------------------------------
# SAFETY - read this before running, it is less inert than the earlier probes
#
# This **constructs** each concrete subclass. That is a real call into vendor
# code, which the previous four probes avoided. Judged proportionate because:
#
#   * they are branding descriptors with parameterless constructors, which is
#     about as inert as a constructor gets;
#   * each one is wrapped individually, so one failure does not stop the run;
#   * there is a wall-clock budget and Stop is honoured (kb/07 #28);
#   * **nothing here touches the mod.** No link is opened, no Programmer is
#     built, no upload path is entered. The worst realistic outcome is another
#     EScribe restart.
#
# It deliberately **does NOT call JSL**. Building a PYB is the next step and
# belongs in its own run, once the right class is known.
#
# Reads instance FIELDS only, never properties - the object exists by then, so
# a field read cannot trigger a type initializer.
# ---------------------------------------------------------------------------

TIME_BUDGET = 30
TARGET      = 109          # device code for the DNA 100 Color

lines = []
def say(s):
    try: lines.append(str(s))
    except: lines.append("<unprintable>")

def _out_path():
    try: return Directories.Documents.Path + "\\dwb2-probe.txt"
    except Exception: return "dwb2-probe.txt"

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

DWB = None
for n, a in asms.items():
    for t in types_of(a):
        if t.Name == "DWB": DWB = t; break
    if DWB is not None: break

if DWB is None:
    say("DWB not found - nothing to do")
else:
    cands = []
    for n, a in asms.items():
        for t in types_of(a):
            try:
                if t is DWB or t.IsAbstract or not t.IsSubclassOf(DWB): continue
            except: continue
            cands.append(t)
    say("=== %d concrete DWB subclasses ===" % len(cands))
    say("target device code: %d" % TARGET)
    say("")

    SIMPLE = ("Int32", "Int16", "Byte", "UInt32", "String", "Boolean", "Double", "Single")
    hits = []

    for t in cands:
        if out_of_time(): say("  ... TIME BUDGET reached, stopping"); break
        if stop_asked():  say("  ... Stop pressed"); break
        try:
            obj = Activator.CreateInstance(t)
        except Exception, e:
            say("%-28s ctor failed: %s" % (t.Name, e)); continue

        vals = []
        interesting = False
        try: flds = obj.GetType().GetFields(INST)
        except: flds = []
        for f in flds:
            if f.FieldType.Name not in SIMPLE: continue
            try: v = f.GetValue(obj)
            except: continue
            if v is None: continue
            # a device code, or anything naming the product
            if f.FieldType.Name == "String":
                sv = str(v)
                if not sv.strip(): continue
                vals.append("%s=%r" % (f.Name, sv))
                if "100" in sv and ("Color" in sv or "Colour" in sv): interesting = True
            else:
                try:
                    iv = int(v)
                except:
                    continue
                vals.append("%s=%s" % (f.Name, iv))
                if iv == TARGET: interesting = True

        mark = "   <<<<< MATCHES %d" % TARGET if interesting else ""
        say("%-28s %s%s" % (t.Name, (", ".join(vals[:12]) or "(no simple fields)"), mark))
        if interesting: hits.append(t.Name)

    say("")
    if hits:
        say("=== candidates for the DNA 100 Color: %s ===" % ", ".join(hits))
    else:
        say("=== no field held %d or a product string ===" % TARGET)
        say("The device code may live on a nested object rather than a simple field,")
        say("or be supplied entirely by the GGQ rather than the DWB - in which case")
        say("the subclass may not need identifying at all.")

txt = "\n".join(lines)
try:
    f = open(_out_path(), "w"); f.write(txt); f.close()
    UI.Message("report: " + _out_path())
except:
    try: UI.ShowTextInEditor(txt)
    except: pass
