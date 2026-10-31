"""Move the low-battery warning off the battery meter and onto its own control.

The Color Themes battery bar carries a default meter, six theme-tinted meters
and then the red low-battery `Picture` as **child 8 of 8** - on both the home
and session screens. In `v1.0` that warning was child 2 of 2; the six tints
pushed it onto the inferred ceiling (`kb/07` #26, `kb/09` audit). It has to be
last to beat a tint, and last is where truncation happens, so it is alive only
if the ceiling is exactly 8 - which nobody has measured.

This splits it per `kb/18` principle 1: the tints stay where they are, and the
red `Picture` moves to a new control over the same rectangle, immediately after
it, behind a default `<Hidden/>`. Two children, **no new images**, and the
largest control in the theme drops from 8 to 7.

The new control is placed **both** next in file order and next in `ZOrder`
(renumbering the rest of that screen), because which of the two the firmware
actually uses is only a hypothesis (`kb/10`: *"Draw order (newer EScribe).
Without it, file order applies"*, rated H). Agreeing with both costs nothing.

    python split-low-battery-warning.py in.ecigtheme out.ecigtheme
    python split-low-battery-warning.py in.ecig out.ecig

Idempotent: a file that has already been split is reported and copied through.
"""

import base64
import re
import shutil
import sys
import xml.etree.ElementTree as ET

BATTERY_LOC = "(0, 0)"
LEVEL_FIELD = "65537"


def is_low_battery(child):
    c = child.find("Compare")
    return c is not None and c.get("Operator") == "3" and c.get("Field") == LEVEL_FIELD


def split(screen):
    """Return True if this screen was changed."""
    controls = screen.findall("Control")
    for idx, ctl in enumerate(controls):
        if ctl.get("Location") != BATTERY_LOC:
            continue
        kids = list(ctl)
        # > 2 skips both a control already split (Hidden + the warning, which
        # shares this Location) and v1.0's two-child meter, which needs nothing.
        if len(kids) <= 2 or not is_low_battery(kids[-1]):
            continue

        warning = kids[-1]
        ctl.remove(warning)

        overlay = ET.Element("Control", dict(ctl.attrib))
        overlay.append(ET.Element("Hidden"))
        overlay.append(warning)

        # file order: immediately after the meter it covers
        pos = list(screen).index(ctl) + 1
        screen.insert(pos, overlay)

        # ZOrder: only if this screen uses it at all, and then keep it dense
        if ctl.get("ZOrder") is not None:
            base = int(ctl.get("ZOrder"))
            for other in screen.findall("Control"):
                z = other.get("ZOrder")
                if other is not overlay and z is not None and int(z) > base:
                    other.set("ZOrder", str(int(z) + 1))
            overlay.set("ZOrder", str(base + 1))
        else:
            overlay.attrib.pop("ZOrder", None)
        return True
    return False


def main():
    src, dest = sys.argv[1], sys.argv[2]
    with __import__("zipfile").ZipFile(src) as z:
        entry = next(n for n in z.namelist() if n.lower().endswith(".xml"))
        raw = z.read(entry).decode("utf-8-sig")

    changed = 0
    if "<ECigTheme" in raw[:200]:
        for m in list(re.finditer(r'(<UIDesign\b[^>]*\bData=")([A-Za-z0-9+/=]+)(")', raw)):
            screen = ET.fromstring(base64.b64decode(m.group(2)).decode("utf-8-sig"))
            if split(screen):
                new = base64.b64encode(ET.tostring(screen, encoding="utf-8")).decode()
                raw = raw.replace(m.group(2), new)
                changed += 1
    else:
        for m in list(re.finditer(r'(<Feature Name="EvolvUIDesign" Index="\d+">)(.*?)(</Feature>)', raw, re.S)):
            body = (m.group(2).replace("&lt;", "<").replace("&gt;", ">")
                    .replace("&quot;", '"').replace("&amp;", "&"))
            screen = ET.fromstring(body)
            if split(screen):
                out = ET.tostring(screen, encoding="unicode")
                esc = out.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                raw = raw.replace(m.group(2), esc)
                changed += 1

    if not changed:
        print(f"no battery control needed splitting in {src} - copying through")
        shutil.copy(src, dest)
        return 0

    ET.fromstring(raw)                                   # the whole document must still parse
    with __import__("zipfile").ZipFile(dest, "w", __import__("zipfile").ZIP_DEFLATED) as z:
        z.writestr(entry, "﻿".encode() + raw.encode("utf-8"))
    print(f"wrote {dest}  ({changed} screen(s) split)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
