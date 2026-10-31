"""Put Jake's own profile settings on the shipped configs.

Taken from his `gremlin_v2.1.ecig`, which is what he actually runs. The whole
config was diffed feature by feature; only these differ in a way that is a
*profile setting* rather than theme content or device state:

    profiles 1 and 2   start temperature   380 -> 385 F
    profiles 1 and 2   session time         60 -> 120 s
    profiles 2 and 4   name        QuestCup -> Quest, QuestCup-Clean -> Quest-Clean

Watts, materials, TCR curves and both cleaning profiles already match.

**Deliberately NOT copied: his locked cold ohms.** `v2.1` carries real readings
on slots 1, 2 and 7 with the lock set. Published configs ship
`EvolvWDColdOhms = 0` and unlocked (`kb/12`), and a baked-in lock is wrong for
anyone else's cup and goes stale the moment a cup is swapped. The mod measures
and he locks once, which is the documented workflow.

Note the two index bases in one file: `EvolvPSTemperature` and `EvolvWMTime`
are **0-based** per profile, while `EvolvWDMaterial` and `EvolvWDColdOhms` are
**256-based**. Easy to conflate.
"""
import base64
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

# feature name -> {index: value}; indices exactly as they appear in the file
CHANGES = {
    "EvolvPSTemperature":  {"0": "385", "1": "385"},
    "EvolvWMTime":         {"0": "120", "1": "120"},
    "EvolvATFriendlyName": {"1": base64.b64encode(b"Quest").decode(),
                            "3": base64.b64encode(b"Quest-Clean").decode()},
}


def apply(src, dest):
    with zipfile.ZipFile(src) as z:
        entry = next(n for n in z.namelist() if n.lower().endswith(".xml"))
        raw = z.read(entry).decode("utf-8-sig")

    applied = 0
    for name, byindex in CHANGES.items():
        for idx, value in byindex.items():
            pat = re.compile(
                rf'(<Feature Name="{name}" Index="{idx}">)(.*?)(</Feature>)', re.S)
            m = pat.search(raw)
            if m is None:
                raise SystemExit(f"{src}: {name}[{idx}] not found")
            if m.group(2) != value:
                raw = raw[:m.start(2)] + value + raw[m.end(2):]
                applied += 1

    # the published rule, asserted rather than assumed
    root = ET.fromstring(raw)
    for f in root.iter("Feature"):
        if f.get("Name") in ("EvolvWDColdOhms", "EvolvWDOhmLock") and f.text != "0":
            raise SystemExit(f"{src}: {f.get('Name')}[{f.get('Index')}] = {f.text}, must ship 0 (kb/12)")

    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(entry, "﻿".encode() + raw.encode("utf-8"))
    print(f"wrote {dest}  ({applied} values changed)")


if __name__ == "__main__":
    apply(sys.argv[1], sys.argv[2])
