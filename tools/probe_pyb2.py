# Find a LIVE PYB inside EScribe - breadth-first from every static root.
#
# Run: Device Monitor -> Diagnostics -> Advanced -> Run Script.
# **Open a config in EScribe first.** With no document loaded there may be no
# PYB to find, which is the most likely reason the first probe came back empty.
#
# COMPLETELY INERT, and more carefully so than probe_pyb.py:
#   * it reads FIELDS ONLY, never properties. A property getter can run
#     arbitrary code; a field read cannot. The first probe read static
#     properties, which was a risk worth removing now that the walk is wide.
#   * it opens no link, calls no Initialize, no AX, no PerformUpload.
#   * it is bounded: MAX_NODES, MAX_DEPTH and a visited set, so it cannot hang
#     EScribe or loop on a cyclic object graph.
# Nothing is sent to the mod. The only write is the report.
#
# Why this probe and not the first one: probe_pyb.py searched static fields and
# properties of type PYB/FWB in DEScribe.Core only, and found none. That rules
# out a *static route*, not a live object - FWB is the document holder, and a
# document is far more likely to hang off a form or view-model as an instance
# field. This walks from the static roots into instance fields, across every
# DEScribe assembly.

MAX_NODES = 40000
MAX_DEPTH = 6
WANTED = ("PYB", "FWB")

lines = []
def say(s):
    try: lines.append(str(s))
    except: lines.append("<unprintable>")

def _out_path():
    try: return Directories.Documents.Path + "\\pyb-probe2.txt"
    except Exception: return "pyb-probe2.txt"

import clr
from System import AppDomain, Array, Object, String
from System.Reflection import BindingFlags

FLAGS = (BindingFlags.Public | BindingFlags.NonPublic |
         BindingFlags.Static | BindingFlags.Instance)

def types_of(a):
    try: return a.GetTypes()
    except Exception, e:
        try: return [t for t in e.clsException.Types if t is not None]
        except: return []

asms = []
for a in AppDomain.CurrentDomain.GetAssemblies():
    try:
        n = a.GetName().Name
        if n.startswith("DEScribe") or n.startswith("DimensionEngineering"):
            asms.append((n, a))
    except: pass
say("=== assemblies searched ===")
for n, a in asms: say("  " + n)

# ---- is a document even open? ----
say("")
say("=== context ===")
try:
    from System.Windows.Forms import Application
    forms = [f for f in Application.OpenForms]
    say("open forms: %d" % len(forms))
    for f in forms:
        try: say("   %s  title=%r" % (f.GetType().Name, f.Text))
        except: say("   <form>")
except Exception, e:
    say("could not enumerate forms: %s" % e)

# ---- seed the walk with every static field on every DEScribe type ----
roots = []
for n, a in asms:
    for t in types_of(a):
        try: fields = t.GetFields(FLAGS)
        except: continue
        for f in fields:
            if not f.IsStatic: continue
            try: v = f.GetValue(None)
            except: continue
            if v is None: continue
            roots.append(("%s.%s.%s" % (n, t.Name, f.Name), v))
say("")
say("static roots: %d" % len(roots))

SKIP = ("String", "Int32", "Int64", "Double", "Single", "Boolean", "Byte",
        "Char", "Decimal", "DateTime", "Guid", "IntPtr", "Type", "RuntimeType")

seen = set()
hits = []
queue = [(p, v, 0) for p, v in roots]
nodes = 0

while queue and nodes < MAX_NODES:
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
    try: flds = obj.GetType().GetFields(FLAGS)
    except: continue
    for f in flds:
        ftn = f.FieldType.Name
        if ftn in SKIP: continue
        try: v = f.GetValue(obj)
        except: continue
        if v is None: continue
        queue.append(("%s.%s" % (path, f.Name), v, depth + 1))

say("objects visited: %d  (cap %d, %s)" % (nodes, MAX_NODES,
    "exhausted the graph" if not queue else "CAP HIT - raise MAX_NODES"))
say("")
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
    tn = obj.GetType().Name
    pyb = obj
    if tn == "FWB":
        try:
            pyb = obj.GetType().GetMethod("get_DE", FLAGS).Invoke(obj, Array[Object]([]))
            say("")
            say("FWB.get_DE() -> %r   (from %s)" % (pyb, path))
        except Exception, e:
            say("FWB.get_DE() failed on %s: %s" % (path, e)); continue
    if pyb is None: continue
    try:
        layout = pyb.GetType().GetMethod("PE", FLAGS).Invoke(pyb, Array[Object]([]))
        dump_layout(layout, "layout from %s" % path)
    except Exception, e:
        say("PE() failed on %s: %s" % (path, e))

txt = "\n".join(lines)
try:
    f = open(_out_path(), "w"); f.write(txt); f.close()
    UI.Message("report: " + _out_path())
except:
    try: UI.ShowTextInEditor(txt)
    except: pass
