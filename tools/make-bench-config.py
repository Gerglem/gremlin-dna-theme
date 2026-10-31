"""Build a bench .ecig that pre-locks a chosen resistance on each profile.

Why this exists: the replace warning compares the *locked* cold ohms, and the
published configs ship it at 0 (`kb/12`), so the warning cannot be exercised
from a normal config at all. This writes a throwaway config that locks a known
resistance on every profile, which makes a single upload test every branch of
the chain. That is how the warning was finally proven (`kb/09`).

    python make-bench-config.py ../release/gremlin_v2.2.05.ecig out.ecig
    python make-bench-config.py in.ecig out.ecig --ohms 0.45 0.46 0.65 0.31

**These are bench configs.** They lock a resistance that will not match the cup
in the deck, so do not fire on one, and reload the real config afterwards.
Never commit one: published configs ship cold ohms 0.
"""

import argparse
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

# Profile N lives at index 255 + N.  Defaults are the two measured baselines
# plus two values chosen to sit either side of the thresholds (kb/02, kb/09).
FIRST_PROFILE_INDEX = 256
DEFAULT_OHMS = ["0.4637451171875",   # profile 1  XL     - under its 0.6 limit
                "0.450439453125",    # profile 2  Quest  - over its 0.41 limit
                "0.6500244140625",   # profile 3  XL cln - over 0.6
                "0.3140869140625"]   # profile 4  Q cln  - under 0.41


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="a released .ecig to base the bench config on")
    ap.add_argument("dest", help="where to write the bench config")
    ap.add_argument("--ohms", nargs="*", default=DEFAULT_OHMS,
                    help="resistance to lock on each profile, in order")
    args = ap.parse_args()

    zin = zipfile.ZipFile(args.source)
    doc = zin.read("DEScribe.xml").decode("utf-8-sig")

    for n, ohms in enumerate(args.ohms):
        idx = FIRST_PROFILE_INDEX + n
        doc, a = re.subn(r'(<Feature Name="EvolvWDColdOhms" Index="%d">)[^<]*(</Feature>)' % idx,
                         r"\g<1>%s\g<2>" % ohms, doc)
        doc, b = re.subn(r'(<Feature Name="EvolvWDOhmLock" Index="%d">)[^<]*(</Feature>)' % idx,
                         r"\g<1>1\g<2>", doc)
        if a != 1 or b != 1:
            sys.exit("profile %d (index %d): matched %d ohms / %d lock fields, expected 1 each"
                     % (n + 1, idx, a, b))

    # A malformed document gives EScribe's useless "Failed to open file" (kb/07 #23).
    ET.fromstring(doc)

    zout = zipfile.ZipFile(args.dest, "w", zipfile.ZIP_DEFLATED)
    for item in zin.infolist():
        zout.writestr(item, doc.encode("utf-8-sig") if item.filename == "DEScribe.xml"
                      else zin.read(item.filename))
    zout.close()

    names = dict(re.findall(r'<Feature Name="EvolvATFriendlyName" Index="(\d)">([^<]*)</Feature>', doc))
    import base64
    print("wrote %s" % args.dest)
    for n, ohms in enumerate(args.ohms):
        label = names.get(str(n), "?")
        try:
            label = base64.b64decode(label).decode("utf-8")
        except Exception:
            pass
        print("   profile %d  %-16s locked at %s" % (n + 1, label, ohms))
    print("\nDo not fire on this. Reload the real config when finished.")


if __name__ == "__main__":
    main()
