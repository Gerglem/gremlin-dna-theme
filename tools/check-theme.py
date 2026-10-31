"""Structural check a Gremlin theme must pass before it ships.

The one defect this catches is the one that cost a day: **a control holds a
limited number of children and drops the rest silently** (`kb/07` #26). The
ohms readout had 11 - a default, six theme tints and four threshold variants -
and its last three were never evaluated, so the replace warning failed under
every operator anyone tried.

**8 children is confirmed working on hardware** (2026-10-30): the LOW BATTERY
banner is the 8th child of the battery meter, and it renders and persists. So
the cutoff is somewhere in 9..10. A control at 8 is safe but has no room left,
which matters - adding a seventh color theme would push 27 controls to 8 and
the two already at 8 to 9.

Works on a `.ecigtheme` (screens are base64 in `UIDesign@Data`) or a `.ecig`
(screens are escaped XML in `Feature Name="EvolvUIDesign"`).

    python check-theme.py ../release/gremlin_v2.2.05_theme.ecigtheme
    python check-theme.py ../release/*.ecig          # exit 1 if anything fails

Point it at the build you are about to ship.

**What this deliberately does NOT flag:** a control carrying both theme tints
and a conditional variant. An earlier version failed that combination, on the
theory that a warning belongs on its own control at a higher `ZOrder`. Hardware
disagreed twice. The overlay draws once and is then painted over, because the
control beneath is bound to a live value and repaints while the static overlay
above it is never re-dirtied. Mixing is the **correct** construction for a live
readout - a repainting control re-evaluates its whole variant list and re-picks
its winning child every frame - and the only real rule is the child count.
"""

import base64
import sys
import zipfile
import xml.etree.ElementTree as ET

# The six Color Theme User Toggles (`kb/09`), kept only to label the report.
TINT_FIELDS = {"10", "266", "778", "1034", "1290", "1546"}

CEILING = 8       # confirmed working on hardware; 11 is known to truncate
HEADROOM = 7      # above this, one more theme breaks the control


def screens(path):
    """Yield (design_id, UIDesign element) from either container format."""
    with zipfile.ZipFile(path) as z:
        name = next(n for n in z.namelist() if n.lower().endswith(".xml"))
        raw = z.read(name).decode("utf-8-sig")
    root = ET.fromstring(raw)                      # catches a bare < or > too (`kb/07` #23)
    if root.tag == "ECigTheme":
        for d in root.iter("UIDesign"):
            yield d.get("ID"), ET.fromstring(base64.b64decode(d.get("Data")).decode("utf-8-sig"))
    else:
        for f in root.iter("Feature"):
            if f.get("Name") == "EvolvUIDesign":
                yield str(int(f.get("Index")) + 1), ET.fromstring(f.text)


WHITE = "(1, 1, 1, 1)"


def is_pale(color):
    """True only for pure white.

    A wider rule was tried on 2026-10-30 and withdrawn the same hour. It
    flagged anything with all channels >= 0.55, which fired on
    `(0.62, 0.62, 0.62, 1)` - the menu-row value grey used since `v1.0` on 18
    controls that have worked in service the whole time. One over-exposed
    photograph of a highlighted setpoint is not evidence against a year of
    use, and a check that reports 18 false positives gets ignored, which is
    worse than not having it. Pure white is the only case actually proven
    invisible (High Contrast `v1.2.06`, `kb/07`).
    """
    return color == WHITE


def is_selectable(ctl):
    """A control the firmware can highlight.

    Selectable controls are drawn on a **white highlight band**, so explicit
    white text on one is invisible (`kb/07`). What makes a control selectable
    is an **editable** Setting - one without `ReadOnly="1"` - or an `Action`.
    That is how the High Contrast home screen lost its profile name in
    `v1.2.06`: the name is the profile selector, which is editable, and the
    replace warning's cancel layer painted it white on white.
    """
    if ctl.find(".//Action") is not None:
        return True
    return any(st.get("ReadOnly") is None for st in ctl.iter("Setting"))


def is_tint(child):
    c = child.find("Compare")
    return (c is not None and c.get("Operator") == "1" and c.get("Field") in TINT_FIELDS
            and c.get("RefValue") == "0" and not list(c))


def check(path):
    errors, warnings = [], []
    for did, screen in screens(path):
        for ctl in screen.iter("Control"):
            kids = list(ctl)
            where = f"design {did} control at {ctl.get('Location')}"
            if is_selectable(ctl):
                for i, k in enumerate(kids, 1):
                    col = k.get("Color")
                    if is_pale(col):
                        errors.append(f"{where}: child {i} paints pure white on a selectable "
                                      f"control, which is drawn on a white highlight - it will be "
                                      f"invisible (kb/07). Omit the color so the firmware inverts "
                                      f"it against the highlight, or state the condition so the "
                                      f"default is never overridden")
            if len(kids) > CEILING:
                errors.append(f"{where}: {len(kids)} children, over the ceiling of {CEILING} "
                              f"- the last {len(kids) - CEILING} are dropped silently (kb/07 #26)")
            elif len(kids) > HEADROOM:
                tints = sum(1 for k in kids if is_tint(k))
                warnings.append(f"{where}: {len(kids)} children ({tints} theme tints), at the "
                                f"ceiling - a seventh theme would break this control")
    return errors, warnings


def main():
    paths = sys.argv[1:]
    if not paths:
        print(__doc__)
        return 2
    failed = False
    for p in paths:
        try:
            errors, warnings = check(p)
        except Exception as exc:                       # malformed container or XML
            print(f"FAIL  {p}\n        cannot parse: {exc}")
            failed = True
            continue
        tag = "FAIL" if errors else ("warn" if warnings else "ok  ")
        print(f"{tag}  {p}")
        for e in errors:
            print(f"        ERROR  {e}")
        for w in dict.fromkeys(warnings):
            print(f"        warn   {w}")
        failed = failed or bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
