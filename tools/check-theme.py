"""Structural checks a Gremlin theme must pass before it ships.

Both bugs this project has had were invisible on inspection and cost a day
each, so they are checked mechanically here rather than remembered:

  * a control holds at most ~8 children and **drops the rest silently**
    (`kb/07` #26) - which is how the replace warning failed;
  * a warning has to be the *last* matching variant to beat a theme tint, so
    putting both on one control parks the warning on that ceiling
    (`kb/09` audit, `kb/18` principle 1) - which is how the low-battery red
    ended up at child 8 of 8.

Works on a `.ecigtheme` (screens are base64 in `UIDesign@Data`) or a `.ecig`
(screens are escaped XML in `Feature Name="EvolvUIDesign"`).

    python check-theme.py ../release/gremlin_v2.3.00_theme.ecigtheme
    python check-theme.py ../release/*.ecig          # exit 1 if anything fails

Point it at the build you are about to ship. Run over the whole `release/`
folder it will also fail **superseded** builds that are kept for their links -
`v2.2.05` carries exactly the defect this tool exists to catch - and that is
the right answer, not a false positive.
"""

import base64
import sys
import zipfile
import xml.etree.ElementTree as ET

# The six Color Theme User Toggles (`kb/09`). A variant gated on one of these
# with Operator="1" against 0 is cosmetic: at most one can match at a time.
TINT_FIELDS = {"10", "266", "778", "1034", "1290", "1546"}

CEILING = 8       # inferred, not measured (`kb/07` #26)
HEADROOM = 7      # a control above this has no room for another theme


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


def kind(child):
    """'default', 'tint' or 'functional'."""
    cmp_ = child.find("Compare")
    if cmp_ is None:
        return "default"
    if (cmp_.get("Operator") == "1" and cmp_.get("Field") in TINT_FIELDS
            and cmp_.get("RefValue") == "0" and not list(cmp_)):
        return "tint"
    return "functional"


def check(path):
    errors, warnings = [], []
    for did, screen in screens(path):
        for ctl in screen.iter("Control"):
            kids = list(ctl)
            kinds = [kind(k) for k in kids]
            where = f"design {did} control at {ctl.get('Location')}"

            if len(kids) > CEILING:
                errors.append(f"{where}: {len(kids)} children, over the ceiling of {CEILING} "
                              f"- the last {len(kids) - CEILING} are dropped silently (kb/07 #26)")

            if "tint" in kinds and "functional" in kinds:
                pos = [i + 1 for i, k in enumerate(kinds) if k == "functional"]
                errors.append(f"{where}: mixes theme tints with conditions at child {pos} of "
                              f"{len(kids)} - split them by ZOrder (kb/18 principle 1)")

            for i, k in enumerate(kinds):
                if k == "functional" and i + 1 > HEADROOM:
                    errors.append(f"{where}: a condition sits at child {i + 1} of {len(kids)}, "
                                  f"one theme away from being dropped")

            if len(kids) > HEADROOM and not errors[-1:] or len(kids) == CEILING:
                if len(kids) >= CEILING:
                    warnings.append(f"{where}: {len(kids)} children, no headroom left")
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
