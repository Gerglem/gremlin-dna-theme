"""Build a temperature staircase for the 7-bit packing test.

Five profiles identical in every respect except Temperature, stepping
380 -> 390 -> 400 -> 410 -> 420 F. Loading and uploading them in order gives
four clean +10 F steps, so the offsets that hold temperature can be watched
moving by a known amount.

Registered test in kb/09: "is the settings block a 7-bit packed bitstream?"

Run from anywhere:  python tools/probes/make-step-profiles.py
"""

import os
import re
import zipfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))

SRC = os.path.join(_ROOT, "release", "profiles", "DTv5XL-Profile.ecigprofile")
OUT = _HERE

# Wattage is pinned across every step so temperature is the ONLY variable.
WATTS = "40"
STEPS = ["380", "390", "400", "410", "420"]


def main():
    with zipfile.ZipFile(SRC) as z:
        xml = z.read("ECigProfile.xml").decode("utf-8-sig")

    written = []
    for temp in STEPS:
        x = re.sub(r'<Power Watts="\d+"', '<Power Watts="%s"' % WATTS, xml)
        x = re.sub(r'<Temperature Fahrenheit="\d+"',
                   '<Temperature Fahrenheit="%s"' % temp, x)
        assert 'Watts="%s"' % WATTS in x and 'Fahrenheit="%s"' % temp in x

        path = os.path.join(OUT, "step-%s.ecigprofile" % temp)
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("ECigProfile.xml", "﻿" + x)   # UTF-8 with BOM, kb/03
        written.append(path)
        print("wrote step-%s.ecigprofile  Power=%s W  Temperature=%s F" % (temp, WATTS, temp))

    # Every pair of consecutive files must differ in exactly one attribute.
    print()
    prev = None
    for temp in STEPS:
        with zipfile.ZipFile(os.path.join(OUT, "step-%s.ecigprofile" % temp)) as z:
            cur = z.read("ECigProfile.xml").decode("utf-8-sig")
        w = re.search(r'Watts="(\d+)"', cur).group(1)
        t = re.search(r'Fahrenheit="(\d+)"', cur).group(1)
        ok = (w == WATTS and t == temp)
        if prev is not None:
            differing = sum(1 for a, b in zip(prev.split("<"), cur.split("<")) if a != b)
            print("verify %s F: Watts=%s  elements differing from previous step: %d  %s"
                  % (t, w, differing, "OK" if ok and differing == 1 else "CHECK"))
        else:
            print("verify %s F: Watts=%s  (first step)  %s" % (t, w, "OK" if ok else "CHECK"))
        prev = cur


if __name__ == "__main__":
    main()
