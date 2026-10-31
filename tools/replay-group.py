"""Replay a captured settings-write group back to the device.

PURPOSE. Everything about the write path is now understood except whether the
trailing bytes of each frame are a checksum the device actually validates
(kb/09 -> "The checksum is now the gate on writing"). This answers that for
one replay, before any effort goes into deriving the algorithm:

  1. Send a captured group back VERBATIM. If the device accepts it, the
     transport and framing are reproducible from Python.
  2. Send it again with ONE payload byte flipped. If that is rejected, the
     trailing bytes are validated and deriving them is required. If it is
     accepted, they are not a gate at all and writing is already within reach.

SAFETY. This writes settings to the device.

  - The shipped group (replay-420.hex) was captured while the device was
    already at 40 W / 420 F, so a faithful replay sets what is already set.
  - --flip defaults to an offset inside a 0x7f padding run (erased flash),
    not a live field, so a corrupt write lands on padding.
  - Nothing is transmitted without --send. The default is a dry run.
  - EScribe must be CLOSED. It holds the HID handle and will contend.

Usage:
    python tools/replay-group.py <group.hex>                  dry run
    python tools/replay-group.py <group.hex> --send           replay verbatim
    python tools/replay-group.py <group.hex> --send --flip    replay corrupted
"""

import argparse
import sys
import time

try:
    import hid
except ImportError:
    sys.exit("hidapi is not installed.  pip install hidapi")

VID, PID = 0x268B, 0x0433
REPORT_LEN = 64          # what dna-hid.py writes: 63-byte report + 1 pad
ACK = "03621800086871"   # payload head of the group ACK, from every capture

# Frame 4 carries a 13-byte 0x7f run at report offsets 10..22 - erased flash
# (0xFF under the 7-bit encoding), not a live field. Offset 14 sits inside it.
FLIP_FRAME, FLIP_OFFSET = 4, 14


def load(path):
    out = []
    for line in open(path):
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(bytearray.fromhex(line))
    return out


FRAMES = []


def describe(i, rpt):
    inner = rpt[2]
    op = rpt[3:5].hex()
    kind = "prologue " if i == 0 else ("terminator" if i == len(FRAMES) - 1 else "write     ")
    return "%2d  %s op=%s inner_len=0x%02x  %s" % (i, kind, op, inner, rpt[5:28].hex())


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("group", help="hex file, one full 63-byte report per line")
    ap.add_argument("--send", action="store_true", help="actually transmit (default: dry run)")
    ap.add_argument("--flip", action="store_true", help="corrupt one padding byte first")
    ap.add_argument("--timeout", type=float, default=1.5)
    args = ap.parse_args()

    frames = load(args.group)
    FRAMES[:] = frames
    print("loaded %d request frames from %s\n" % (len(frames), args.group))

    if args.flip:
        if FLIP_FRAME >= len(frames):
            sys.exit("group too short to flip frame %d" % FLIP_FRAME)
        f = frames[FLIP_FRAME]
        before = f[FLIP_OFFSET]
        if before != 0x7F:
            print("REFUSING to flip: frame %d offset %d is 0x%02x, not 0x7f padding."
                  % (FLIP_FRAME, FLIP_OFFSET, before))
            print("Pick an offset inside a 0x7f run so a corrupt write lands on erased flash.")
            return 2
        f[FLIP_OFFSET] = 0x7E
        print("FLIPPED frame %d offset %d: 0x%02x -> 0x%02x (inside a padding run)\n"
              % (FLIP_FRAME, FLIP_OFFSET, before, f[FLIP_OFFSET]))

    for i, rpt in enumerate(frames):
        print(describe(i, rpt))

    if not args.send:
        print("\nDRY RUN - nothing transmitted. Add --send to replay.")
        return 0

    print("\nopening %04x:%04x ..." % (VID, PID))
    dev = hid.device()
    try:
        dev.open(VID, PID)
    except Exception as exc:
        sys.exit("could not open the device (%s).  Is EScribe still running?" % exc)
    dev.set_nonblocking(1)

    replies = []
    try:
        for i, rpt in enumerate(frames):
            buf = bytes(rpt) + b"\x00" * (REPORT_LEN - len(rpt))
            n = dev.write(buf)
            print("sent frame %d (%d bytes written)" % (i, n))
            deadline = time.time() + args.timeout
            while time.time() < deadline:
                r = dev.read(REPORT_LEN)
                if r:
                    b = bytes(r)
                    if len(b) > 4 and b[0] == 0x01 and b[1] == 0xDE:
                        replies.append((i, b))
                        print("   reply after frame %d: %s" % (i, b[5:5 + b[2]].hex()[:40]))
                    break
                time.sleep(0.004)
    finally:
        dev.close()

    print("\n%d replies seen" % len(replies))
    acked = [r for _, r in replies if r[5:5 + 7].hex() == ACK]
    if acked:
        print("GROUP ACK SEEN (%s) - the device accepted the group." % ACK)
    else:
        print("NO GROUP ACK (expected payload head %s)." % ACK)
        for i, r in replies:
            print("   after frame %d: %s" % (i, r[5:5 + r[2]].hex()[:40]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
