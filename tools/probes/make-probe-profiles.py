"""Build single-field probe profiles for protocol work.

probe-A and probe-B differ in EXACTLY ONE attribute (Temperature), so
uploading one and then the other isolates which bytes of the 341-byte write
block hold that field. Used on 2026-10-31 to establish that a single field
change moves five bytes, all in frame 3.

See kb/16 -> "Byte 3 is not an address" and "One field moves five bytes".

Run from anywhere:  python tools/probes/make-probe-profiles.py
"""

import difflib
import os
import re
import zipfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))

SRC = os.path.join(_ROOT, "release", "profiles", "DTv5XL-Profile.ecigprofile")
OUT = _HERE

# Both variants carry the SAME wattage so that an A -> B upload has only the
# temperature left to write. Changing two fields at once makes the capture
# uninterpretable - that mistake cost a round on 2026-10-31.
VARIANTS = [
    ("A", "40", "380"),
    ("B", "40", "420"),
]


def main():
    with zipfile.ZipFile(SRC) as z:
        xml = z.read("ECigProfile.xml").decode("utf-8-sig")

    base_w = re.search(r'<Power Watts="(\d+)"', xml).group(1)
    base_t = re.search(r'<Temperature Fahrenheit="(\d+)"', xml).group(1)
    print("source: Power=%s W, Temperature=%s F" % (base_w, base_t))

    for tag, watts, temp in VARIANTS:
        x = re.sub(r'<Power Watts="\d+"', '<Power Watts="%s"' % watts, xml)
        x = re.sub(r'<Temperature Fahrenheit="\d+"',
                   '<Temperature Fahrenheit="%s"' % temp, x)
        assert 'Watts="%s"' % watts in x and 'Fahrenheit="%s"' % temp in x

        path = os.path.join(OUT, "probe-%s.ecigprofile" % tag)
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            # EScribe writes ECigProfile.xml as UTF-8 WITH BOM (kb/03).
            zf.writestr("ECigProfile.xml", "﻿" + x)
        print("wrote probe-%s.ecigprofile  Power=%s W  Temperature=%s F  (%d bytes)"
              % (tag, watts, temp, os.path.getsize(path)))

    # Verify the round trip, and that A and B really differ in one attribute.
    read = {}
    for tag, watts, temp in VARIANTS:
        path = os.path.join(OUT, "probe-%s.ecigprofile" % tag)
        with zipfile.ZipFile(path) as z:
            got = z.read("ECigProfile.xml").decode("utf-8-sig")
        read[tag] = got
        w = re.search(r'Watts="(\d+)"', got).group(1)
        t = re.search(r'Fahrenheit="(\d+)"', got).group(1)
        print("verify %s: Watts=%s Fahrenheit=%s  %s"
              % (tag, w, t, "OK" if (w == watts and t == temp) else "MISMATCH"))

    diffs = [d for d in difflib.ndiff(read["A"].split("<"), read["B"].split("<"))
             if d[0] in "+-"]
    print("\nA vs B differing XML elements: %d" % len(diffs))
    for d in diffs:
        print("   ", d.strip()[:80])
    if len(diffs) != 2:
        print("\nWARNING: expected exactly one changed attribute (2 diff lines).")


if __name__ == "__main__":
    main()
