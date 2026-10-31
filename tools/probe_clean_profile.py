# Device Monitor script - NOT a standalone Python script.
#
# Run it from Device Monitor: Diagnostics -> Advanced -> Run Script.
# (Options -> User Interface -> Researcher or Manufacturer puts Run Script on
# the Diagnostics menu directly, without the warning. See kb/14.)
#
# WHAT IT ANSWERS
# kb/09 "Tracked: Clean profiles show temperature, and the live row blanks
# while firing" asks whether a Clean profile is actually in temperature
# control, or whether the theme is drawing temperature controls that are not
# conditioned on the profile being in TC.
#
# The photos from 2026-10-30 show the live temperature row present at idle and
# ABSENT while firing, with SET 450F shown in both. Two explanations fit, and
# they need different fixes:
#   1. The profile is in wattage mode, there is no regulated temperature, and
#      the controls simply are not conditioned on TC.
#   2. The profile IS sensing temperature, and only the live row's condition
#      is wrong.
# The idle cold-to-live ohm rise (0.524 -> 0.874) is the evidence for (2), but
# it may just be a hot coil read moments after a fire.
#
# WHAT IT CANNOT ANSWER
# Device Monitor exposes no theme or screen state (kb/14 -> Limits). This
# tells you what the DEVICE reports, not what the theme draws. The blanking
# row still has to be read off the screen. Run this, then photograph the
# screen during a fire - the two together settle it.
#
# METHOD
# Run it ONCE PER PROFILE - a Clean profile and a normal vaping profile - and
# compare the CSVs. Profile is not in Device Monitor's variable list, so
# switch profiles on the device between runs.

import time

PUFF_SECONDS = 3
SETTLE = 4
SAMPLES_WHILE_FIRING = 6

FIELDS = ['Temperature', 'Temperature Set', 'Live Ohms', 'Cold Ohms',
          'Power', 'Power Set', 'Voltage', 'Current']


def snapshot():
    row = {}
    for f in FIELDS:
        try:
            row[f] = ECig[f]
        except Exception, exc:          # IronPython 2.x syntax
            row[f] = 'ERR:%s' % exc
    return row


def show(label, row):
    parts = []
    for f in FIELDS:
        parts.append('%s=%s' % (f, row[f]))
    Script.SetStatus('%s  %s' % (label, '  '.join(parts)))


UI.Message('Put the device on the profile you want to test, then click OK.\n\n'
           'Run this once for a Clean profile and once for a vaping profile.')

# Tracked variables update faster, so track everything we intend to poll.
ECig.ClearTracking()
for f in FIELDS:
    ECig.Track(f)
time.sleep(1)

path = Directories.Documents.Path + r'\clean-profile-probe.csv'
csv = CSV.Create(path)
csv.WriteHeader(['phase', 'elapsed'] + FIELDS)


def write(phase, t0, row):
    values = [phase, '%.2f' % (time.time() - t0)]
    for f in FIELDS:
        values.append(row[f])
    csv.Write(values)


t0 = time.time()

# --- idle -------------------------------------------------------------
for i in range(3):
    row = snapshot()
    show('IDLE', row)
    write('idle', t0, row)
    time.sleep(1)

idle = snapshot()

# --- firing -----------------------------------------------------------
# Puff() blocks for the duration, so start it, then sample. If your build
# blocks, the samples land immediately after instead - the CSV phase column
# still distinguishes them.
ECig.Puff(PUFF_SECONDS)
for i in range(SAMPLES_WHILE_FIRING):
    row = snapshot()
    show('FIRING', row)
    write('firing', t0, row)
    time.sleep(float(PUFF_SECONDS) / SAMPLES_WHILE_FIRING)

firing = snapshot()

# --- after ------------------------------------------------------------
time.sleep(SETTLE)
after = snapshot()
write('after', t0, after)

csv.Close()

# --- the comparison that matters --------------------------------------
summary = []
summary.append('Wrote %s' % path)
summary.append('')
summary.append('%-18s %12s %12s %12s' % ('', 'idle', 'firing', 'after'))
for f in FIELDS:
    summary.append('%-18s %12s %12s %12s' % (f, idle[f], firing[f], after[f]))
summary.append('')
summary.append('Read this against the screen:')
summary.append('  Temperature changing while firing -> the device IS sensing')
summary.append('    temperature, so only the row condition is wrong.')
summary.append('  Temperature flat or equal to Temperature Set -> the profile')
summary.append('    is not in TC and the controls are unconditioned.')
summary.append('')
summary.append('Now photograph the screen during a fire. Device Monitor')
summary.append('cannot see what the theme draws (kb/14).')

UI.Message('\n'.join(summary))
