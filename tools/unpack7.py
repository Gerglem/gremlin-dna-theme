"""Unpack the DNA100C 7-bit packed settings block.

The settings block that EScribe writes over vendor HID is a 7-bit packed
bitstream, not an array of bytes. Each payload byte carries 7 significant
bits; concatenating them and re-reading the stream in 8-bit groups recovers
the real byte layout. This is why a single field change disturbs several
NON-ADJACENT payload bytes and why no byte-aligned reading of the raw frame
ever produced a sensible number (kb/16).

Established 2026-10-31 by uploading a temperature staircase (380..420 F in
10 F steps) and diffing the resulting write groups. See
tools/probes/make-step-profiles.py.

KNOWN FIELDS, in the unpacked stream of write frame 3, little-endian 16-bit:

    offset 2    power        watts x 32
    offset 4    temperature  degrees F x 32

Both scale by 32. Verified exactly, with no rounding, on:
    37 W / 385 F,  40 W / 380 F,  40 W / 390 F,
    40 W / 400 F,  40 W / 410 F,  40 W / 420 F

The 385 F case is an independent check: it was read back from a capture taken
before the staircase, and matches what the EScribe UI displayed at the time.

NOT yet decoded: the trailing bytes (unpacked ~44-45) move on every change and
are almost certainly a checksum. Nothing composed locally can be uploaded
until that is understood - see kb/09.

Usage:
    python tools/unpack7.py <payload-hex>        unpack one frame payload
    python tools/unpack7.py --sample             run the built-in self-check
"""

import sys

# Bytes of the frame header that precede the packed stream.
HEADER = 5

# Scale factor shared by the power and temperature fields.
SCALE = 32

FIELDS = {
    2: ("power", "W"),
    4: ("temperature", "F"),
}


def unpack7(payload, skip=HEADER):
    """Expand a 7-bit packed payload into its real byte stream."""
    bits = "".join(format(b & 0x7F, "07b") for b in payload[skip:])
    return bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits) - 7, 8))


def le16(buf, off):
    return buf[off] | (buf[off + 1] << 8)


def read_fields(payload):
    """Return {name: value} for every field we can currently decode."""
    u = unpack7(payload)
    out = {}
    for off, (name, unit) in FIELDS.items():
        if off + 1 < len(u):
            out[name] = (le16(u, off) / float(SCALE), unit)
    return out


def _selfcheck():
    """Frame 3 payloads captured 2026-10-31, with their known settings."""
    cases = [
        ("36 5a 1e 70 02 05 66 00 00 2c 00 5e 3c 00 00 00 03 64 00 7c 10 00 01", 40, 380),
        ("36 5a 1e 70 02 05 66 00 00 2e 00 60 3c 00 00 00 03 64 02 60 10 00 01", 40, 390),
        ("36 5a 1e 70 02 05 66 00 00 28 00 64 3c 00 00 00 03 64 02 7c 10 00 01", 40, 400),
        ("36 5a 1e 70 02 05 66 00 00 2a 00 66 3c 00 00 00 03 64 02 16 10 00 01", 40, 410),
        ("36 5a 1e 70 02 05 66 00 00 2c 00 68 3c 00 00 00 03 64 01 22 10 00 01", 40, 420),
    ]
    ok = True
    for hexs, want_w, want_t in cases:
        p = bytes.fromhex(hexs.replace(" ", ""))
        f = read_fields(p)
        got_t = f.get("temperature", (None, ""))[0]
        good = (got_t == want_t)
        ok = ok and good
        print("  %-28s temperature %-8s expected %-5s %s"
              % (hexs[:26] + "...", got_t, want_t, "OK" if good else "MISMATCH"))
    print("\nself-check:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[1] == "--sample":
        return _selfcheck()

    payload = bytes.fromhex("".join(argv[1:]).replace(" ", ""))
    u = unpack7(payload)
    print("packed   %d bytes" % len(payload))
    print("unpacked %d bytes" % len(u))
    print("  " + " ".join("%02x" % b for b in u))
    print()
    for name, (value, unit) in sorted(read_fields(payload).items()):
        print("  %-12s %g %s" % (name, value, unit))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
