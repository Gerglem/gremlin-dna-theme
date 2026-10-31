# Find a LIVE PYB inside EScribe - walking only objects that already exist.
#
# Run: Device Monitor -> Diagnostics -> Advanced -> Run Script.
# **Open a config in EScribe first**, so there is a document to find.
#
# ---------------------------------------------------------------------------
# WHY THIS REPLACES probe_pyb2.py
#
# probe_pyb2.py hung EScribe. It seeded its walk by reading **every static
# field of every type** in the DEScribe assemblies - and reading a static field
# forces that type's **static constructor** to run. That is hundreds of pieces
# of arbitrary code, some of which block. Probe 2 deliberately avoided property
# getters for exactly that reason and then triggered the same thing through
# type initializers.
#
# This probe never touches a type it has not already been handed an instance
# of. It starts from Application.OpenForms - objects that are alive and whose
# types are therefore already initialized - and walks instance fields from
# there. No static constructor can fire as a result.
#
# It is also interruptible: it sets Script.WillStopIfAsked and checks
# Script.ShouldStop, so Device Monitor's Stop button works, and it gives up on
# its own after TIME_BUDGET seconds. Probe 2 did neither, which is why Stop did
# not help.
#
# INERT: reads fields, calls only get_DE() and PE(), both of which are reads.
# Opens no link. Sends nothing to the mod. The only write is the report.
# ---------------------------------------------------------------------------

TIME_BUDGET = 20          # seconds, then stop and report whatever was found
MAX_NODES   = 20000
MAX_DEPTH   = 8
WANTED      = ("PYB", "FWB")

lines = []
def say(s):
    try: lines.append(str(s))
    except: lines.append("<unprintable>")

def _out_path():
    try: return Directories.Documents.Path + "\\pyb-probe3.txt"
    except Exception: return "pyb-probe3.txt"

def _write():
    txt = "\n".join(lines)
    try:
        f = open(_out_path(), "w"); f.write(txt); f.close()
        UI.Message("report: " + _out_path())
    except:
        try: UI.ShowTextInEditor(txt)
        except: pass

import clr
from System import DateTime, Array, Object
from System.Reflection import BindingFlags

INST = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance

try:
    Script.WillStopIfAsked = True
except:
    pass

def asked_to_stop():
    try: return Script.ShouldStop
    except: return False

started = DateTime.Now
def out_of_time():
    try: return (DateTime.Now - started).TotalSeconds > TIME_BUDGET
    except: return False

# ---- roots: live objects only ----
roots = []
say("=== roots ===")
try:
    from System.Windows.Forms import Application
    for f in Application.OpenForms:
        try: nm = "%s(%r)" % (f.GetType().Name, f.Text)
        except: nm = f.GetType().Name
        say("  form " + nm)
        roots.append((nm, f))
except Exception, e:
    say("  could not enumerate forms: %s" % e)

for extra in ("ECig", "Device", "Directories", "UI", "Script"):
    try:
        v = eval(extra)
        if v is not None:
            say("  global " + extra)
            roots.append((extra, v))
    except:
        pass

if not roots:
    say("  NONE - nothing to walk from")

SKIP = ("String", "Int32", "Int64", "Double", "Single", "Boolean", "Byte",
        "Char", "Decimal", "DateTime", "Guid", "IntPtr", "Color", "Font",
        "Bitmap", "Image", "Type", "RuntimeType")

seen  = set()
hits  = []
queue = [(p, v, 0) for p, v in roots]
nodes = 0
stopped = None

while queue:
    if nodes >= MAX_NODES:  stopped = "node cap"; break
    if out_of_time():       stopped = "time budget"; break
    if asked_to_stop():     stopped = "Stop pressed"; break

    path, obj, depth = queue.pop(0)
    nodes += 1
    try: tn = obj.GetType().Name
    except: continue

    if tn in WANTED:
        hits.append((path, obj))
        continue
    if depth >= MAX_DEPTH or tn in SKIP:
        continue
    try: key = id(obj)
    except: continue
    if key in seen: continue
    seen.add(key)

    # instance fields of an object that already exists - no type init can fire
    try: flds = obj.GetType().GetFields(INST)
    except: continue
    for fl in flds:
        if fl.FieldType.Name in SKIP: continue
        try: v = fl.GetValue(obj)
        except: continue
        if v is None: continue
        queue.append(("%s.%s" % (path, fl.Name), v, depth + 1))

say("")
say("objects visited: %d   depth cap %d   %s"
    % (nodes, MAX_DEPTH,
       ("finished the graph" if stopped is None else "STOPPED EARLY: " + stopped)))
say("=== live PYB / FWB found: %d ===" % len(hits))
for path, obj in hits:
    say("  %s -> %s" % (path, obj.GetType().Name))

def dump_layout(layout, label):
    say("")
    say("=== %s ===" % label)
    if layout is None:
        say("   null"); return
    try:
        say("   PCSize=%s  PCSizeUsed=%s" % (layout.PCSize, layout.PCSizeUsed))
        i = 0
        for r in layout.Regions:
            say("   [%2d] size %7d  dev 0x%06X  pc 0x%06X  ro=%-5s hashWhole=%-5s chunk=%-6s tag=%s"
                % (i, r.Size, r.DeviceOffset, r.PCOffset, r.ReadOnly,
                   r.HashWholeRegion, r.HashChunkSize, r.Tag))
            i += 1
    except Exception, e:
        say("   failed to read: %s" % e)

for path, obj in hits:
    pyb = obj
    if obj.GetType().Name == "FWB":
        try:
            pyb = obj.GetType().GetMethod("get_DE", INST).Invoke(obj, Array[Object]([]))
            say("")
            say("FWB.get_DE() -> %r   (from %s)" % (pyb, path))
        except Exception, e:
            say("FWB.get_DE() failed on %s: %s" % (path, e)); continue
    if pyb is None: continue
    try:
        layout = pyb.GetType().GetMethod("PE", INST).Invoke(pyb, Array[Object]([]))
        dump_layout(layout, "layout from %s" % path)
    except Exception, e:
        say("PE() failed on %s: %s" % (path, e))

_write()
