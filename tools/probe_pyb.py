# Find a LIVE PYB inside EScribe and read the real flash layout from it.
#
# Run: Device Monitor -> Diagnostics -> Advanced -> Run Script.
#
# COMPLETELY INERT. It walks EScribe's own objects and reads properties.
# It opens no link, calls no Initialize, no AX, no PerformUpload. Nothing
# is sent to the mod and nothing is written anywhere except the report.

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
from System import AppDomain, Array, Object
from System.Reflection import BindingFlags
ALL = (BindingFlags.Public | BindingFlags.NonPublic |
       BindingFlags.Static | BindingFlags.Instance)

def types(a):
    try: return a.GetTypes()
    except Exception, e:
        try: return [t for t in e.clsException.Types if t is not None]
        except: return []

core = None
for a in AppDomain.CurrentDomain.GetAssemblies():
    try:
        if a.GetName().Name == "DEScribe.Core": core = a
    except: pass

say("=== hunting a live PYB ===")
ct = types(core)
PYB = None
for t in ct:
    if t.Name == "PYB": PYB = t
say("PYB type found: %s" % (PYB is not None))

# FWB.get_DE() returns a PYB - look for a static route to an FWB first.
found = []
for t in ct:
    for p in t.GetProperties(ALL):
        if p.PropertyType.Name in ("PYB", "FWB"):
            g = p.GetGetMethod(True)
            if g is not None and g.IsStatic:
                try:
                    v = p.GetValue(None, None)
                    say("  static %s.%s -> %r" % (t.Name, p.Name, v))
                    if v is not None: found.append(v)
                except Exception, e:
                    pass
    for f in t.GetFields(ALL):
        if f.IsStatic and f.FieldType.Name in ("PYB", "FWB"):
            try:
                v = f.GetValue(None)
                say("  static field %s.%s -> %r" % (t.Name, f.Name, v))
                if v is not None: found.append(v)
            except: pass

say("")
say("live candidates: %d" % len(found))

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

for obj in found:
    tn = obj.GetType().Name
    pyb = obj
    if tn == "FWB":
        try:
            pyb = obj.GetType().GetMethod("get_DE", ALL).Invoke(obj, Array[Object]([]))
            say("FWB.get_DE() -> %r" % pyb)
        except Exception, e:
            say("FWB.get_DE() failed: %s" % e); continue
    if pyb is None: continue
    try:
        layout = pyb.GetType().GetMethod("PE", ALL).Invoke(pyb, Array[Object]([]))
        dump_layout(layout, "layout from a live %s" % tn)
    except Exception, e:
        say("PE() failed: %s" % e)

txt = "\n".join(lines)
try:
    f = open(_out_path(), "w"); f.write(txt); f.close()
    UI.Message("report: " + _out_path())
except:
    try: UI.ShowTextInEditor(txt)
    except: pass
