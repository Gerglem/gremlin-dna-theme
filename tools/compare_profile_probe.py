"""Compare two clean-profile-probe runs and say what they imply.

tools/probe_clean_profile.py writes one CSV per run. Run it once on a Clean
profile and once on a vaping profile, keep both files, then:

    python tools/compare_profile_probe.py <clean.csv> <vaping.csv>

The question (kb/09) is whether a Clean profile is actually in temperature
control, or whether the theme draws temperature controls that are not
conditioned on TC. The discriminator is simple: in temperature control the
reported Temperature MOVES while firing. In wattage mode it does not.

This only reads what the device reported. What the theme DRAWS still has to
come off a photograph - Device Monitor exposes no screen state (kb/14).
"""

import csv
import sys


def load(path):
    rows = []
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            rows.append(row)
    return rows


def num(row, key):
    raw = (row.get(key) or "").strip()
    for suffix in ("F", "C", "W", "V", "A", "OHM", "ohm"):
        if raw.upper().endswith(suffix.upper()):
            raw = raw[: -len(suffix)].strip()
    try:
        return float(raw)
    except ValueError:
        return None


def series(rows, phase, key):
    out = []
    for r in rows:
        if r.get("phase") == phase:
            v = num(r, key)
            if v is not None:
                out.append(v)
    return out


def describe(label, rows):
    print("=" * 66)
    print(label)
    print("=" * 66)

    idle_t = series(rows, "idle", "Temperature")
    fire_t = series(rows, "firing", "Temperature")
    idle_set = series(rows, "idle", "Temperature Set")
    idle_cold = series(rows, "idle", "Cold Ohms")
    idle_live = series(rows, "idle", "Live Ohms")
    fire_live = series(rows, "firing", "Live Ohms")

    def rng(vals):
        if not vals:
            return "no data"
        return "%.2f .. %.2f (spread %.2f)" % (min(vals), max(vals), max(vals) - min(vals))

    print("  Temperature, idle    : %s" % rng(idle_t))
    print("  Temperature, firing  : %s" % rng(fire_t))
    print("  Temperature Set      : %s" % rng(idle_set))
    print("  Cold Ohms, idle      : %s" % rng(idle_cold))
    print("  Live Ohms, idle      : %s" % rng(idle_live))
    print("  Live Ohms, firing    : %s" % rng(fire_live))

    verdict = None
    if fire_t:
        spread = max(fire_t) - min(fire_t)
        if spread >= 5.0:
            verdict = "SENSING - Temperature moved %.1f deg while firing" % spread
        elif idle_set and abs(sum(fire_t) / len(fire_t) - idle_set[0]) < 1.0:
            verdict = "NOT SENSING - Temperature just mirrors Temperature Set"
        else:
            verdict = "FLAT - Temperature did not move (%.1f deg spread)" % spread
    print("  -> %s" % (verdict or "no firing samples"))
    print()
    return verdict


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    clean = describe("CLEAN PROFILE   %s" % argv[1], load(argv[1]))
    vaping = describe("VAPING PROFILE  %s" % argv[2], load(argv[2]))

    print("=" * 66)
    print("WHAT THIS IMPLIES")
    print("=" * 66)
    if clean and vaping and clean.startswith("SENSING") and vaping.startswith("SENSING"):
        print("  Both profiles sense temperature. The Clean profile IS in TC, so")
        print("  the temperature controls are legitimate and only the live row's")
        print("  condition is wrong. Small theme fix: fix that one condition.")
    elif clean and vaping and not clean.startswith("SENSING") and vaping.startswith("SENSING"):
        print("  The vaping profile senses and the Clean profile does not. The")
        print("  Clean profile is in wattage mode, so the temperature controls")
        print("  are not conditioned on the profile being in TC. Larger fix:")
        print("  condition the controls, do not just fix the live row.")
    elif clean and vaping and not vaping.startswith("SENSING"):
        print("  NEITHER profile showed movement. Before concluding anything,")
        print("  check the puff actually fired - look at Power and Current in")
        print("  the CSV. A 0 W firing phase means the script fired nothing.")
    else:
        print("  Inconclusive. Check both CSVs have a 'firing' phase with data.")
    print()
    print("  Either way, confirm against the screen photographs. This shows")
    print("  what the DEVICE reported, not what the theme drew (kb/14).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
