# Stop calling the transfer directly. Find what EScribe calls around it.
#
# Run: Device Monitor -> Diagnostics -> Advanced -> Run Script.
# Device-free - metadata only. Nothing is opened, nothing is written.
#
# ---------------------------------------------------------------------------
# EVERY THEORY IS NOW DEAD, INCLUDING CONTENTION
#
#   UE's address            solved - bit 7 must be set
#   JSL's document          dead - returns null when given one
#   AX's Boolean[]          dead - full and empty both time out
#   UserModeVersion         dead - genuinely set, still times out
#   The layout              dead - A.OCC.IE holds it
#   A second HID handle     dead - borrowed Device Monitor's own POT
#                                  (ECig.GE.EQ.EE), single handle, still timed out
#   AX's progress monitor   dead - a real A.FMQ changed nothing
#
# So the Programmer is correct in every respect we can inspect, holds the only
# link in the process, and the board still does not answer. That is not an
# argument problem. **We are calling the wrong thing.**
#
# kb/16 said this early and it was not followed up: `DEScribe.Core` is the
# orchestrator. It takes the backup, resolves the device identity, sends
# `get version`, brackets the transfer with the
# `*** START UPLOADING SETTINGS ***` markers - and only then moves bytes. The
# board very likely has to be *told* a transfer is starting before it will
# answer one; the HID channel is otherwise busy streaming telemetry in a
# plain-text protocol (kb/17), and the settings frames use their own `F8 2B`
# opcode (kb/16).
#
# Calling AX by itself skips all of that.
#
# This looks for the layer above: anything in DEScribe.* that takes a
# Programmer, or an IProgressMonitor, or has a name suggesting it drives a
# transfer. `VYB.PerformUpload(Object context, IProgressMonitor progress,
# Boolean dontUpload)` is the one such name already known - a *download*
# counterpart is what we want.
#
# SAFETY: metadata only. No instances created, no values read, nothing
# invoked, no link. Cannot touch the mod.
# ---------------------------------------------------------------------------

lines = []
def say(s):
    try: lines.append(str(s))
    except: lines.append("<unprintable>")

def _out_path():
    try: return Directories.Documents.Path + "\\orchestrator-probe.txt"
    except Exception: return "orchestrator-probe.txt"

import clr
from System import AppDomain
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
        if n.startswith("DEScribe") or n.startswith("Dimension"): asms.append((n, a))
    except: pass

# what counts as "Programmer-ish"
PROG = ("OCC", "ECC", "YCC", "TCC", "VYB")

say("=== 1. methods that take a Programmer ===")
n1 = 0
for an, a in asms:
    for t in types_of(a):
        try: ms = t.GetMethods(FLAGS)
        except: continue
        for m in ms:
            try: ps = m.GetParameters()
            except: continue
            if not any(p.ParameterType.Name in PROG for p in ps): continue
            say("  %-22s %s.%s(%s) -> %s"
                % (an, t.Name, m.Name,
                   ", ".join("%s %s" % (p.ParameterType.Name, p.Name or "?") for p in ps),
                   m.ReturnType.Name))
            n1 += 1
say("  total: %d" % n1)

say("")
say("=== 2. methods taking an IProgressMonitor (the transfer layer) ===")
n2 = 0
for an, a in asms:
    for t in types_of(a):
        try: ms = t.GetMethods(FLAGS)
        except: continue
        for m in ms:
            try: ps = m.GetParameters()
            except: continue
            if not any("ProgressMonitor" in p.ParameterType.Name for p in ps): continue
            say("  %-22s %s.%s(%s) -> %s   static=%s"
                % (an, t.Name, m.Name,
                   ", ".join("%s %s" % (p.ParameterType.Name, p.Name or "?") for p in ps),
                   m.ReturnType.Name, m.IsStatic))
            n2 += 1
say("  total: %d" % n2)

say("")
say("=== 3. names that survived obfuscation and sound like transfers ===")
WORDS = ("upload", "download", "transfer", "perform", "settings", "read", "write",
         "begin", "commit", "sync", "connect", "handshake")
n3 = 0
for an, a in asms:
    for t in types_of(a):
        try: ms = t.GetMethods(FLAGS)
        except: continue
        for m in ms:
            nm = m.Name
            if len(nm) <= 3: continue                      # obfuscated stubs
            low = nm.lower()
            if not any(w in low for w in WORDS): continue
            if nm.startswith("get_") or nm.startswith("set_"): continue
            try: ps = m.GetParameters()
            except: continue
            say("  %-22s %s.%s(%s) -> %s   static=%s"
                % (an, t.Name, nm,
                   ", ".join("%s %s" % (p.ParameterType.Name, p.Name or "?") for p in ps),
                   m.ReturnType.Name, m.IsStatic))
            n3 += 1
say("  total: %d" % n3)

say("")
say("=== 4. VYB, the one Programmer subclass with readable names ===")
for an, a in asms:
    for t in types_of(a):
        if t.Name != "VYB": continue
        say("  %s.%s  base=%s  abstract=%s"
            % (an, t.Name, t.BaseType.Name if t.BaseType else "-", t.IsAbstract))
        try:
            for m in sorted(t.GetMethods(BindingFlags.Public | BindingFlags.NonPublic |
                                         BindingFlags.Instance | BindingFlags.DeclaredOnly),
                            key=lambda x: x.Name):
                say("    %s(%s) -> %s"
                    % (m.Name,
                       ", ".join("%s %s" % (p.ParameterType.Name, p.Name or "?")
                                 for p in m.GetParameters()),
                       m.ReturnType.Name))
        except Exception, e:
            say("    failed: %s" % e)
        try:
            for c in t.GetConstructors(FLAGS):
                say("    ctor(%s)" % ", ".join("%s %s" % (p.ParameterType.Name, p.Name or "?")
                                               for p in c.GetParameters()))
        except: pass

txt = "\n".join(lines)
try:
    f = open(_out_path(), "w"); f.write(txt); f.close()
    UI.Message("report: " + _out_path())
except:
    try: UI.ShowTextInEditor(txt)
    except: pass
