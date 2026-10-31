"""Replay several captured frame files back to back in ONE HID session.

WHY. Replaying a write group on its own does nothing: the device sends no
reply at all (kb/09, 2026-10-31). In every captured upload EScribe performs
the full 207-exchange connect-and-download FIRST and only then writes. This
tool tests whether that handshake is a replayable prefix, by sending it and
the write group without closing the handle in between.

    python tools/replay-session.py tools/samples/handshake.hex \
                                   tools/samples/replay-420.hex --send

Each file is one phase. The summary reports, per phase, how many frames were
sent and how many replies came back, so the three outcomes registered in
kb/09 are distinguishable at a glance:

    handshake replies ~207, group ACKed      -> A, replayable prefix
    handshake replies ~207, group silent     -> B, stateful/challenge
    handshake silent                         -> C, even reads need state

SAFETY. Writes settings to the device. Nothing transmits without --send.
EScribe holds the HID handle EXCLUSIVELY and must be closed first.
"""

import argparse
import sys
import time

try:
    import hid
except ImportError:
    sys.exit("hidapi is not installed.  pip install hidapi")

VID, PID = 0x268B, 0x0433
REPORT_LEN = 64
ACK = "03621800086871"


def load(path):
    out = []
    for line in open(path):
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(bytes.fromhex(line))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("phases", nargs="+", help="hex files, replayed in order in one session")
    ap.add_argument("--send", action="store_true", help="actually transmit (default: dry run)")
    ap.add_argument("--gap", type=float, default=0.004, help="seconds between frames")
    ap.add_argument("--reply-wait", type=float, default=0.06,
                    help="seconds to wait for a reply after each frame")
    ap.add_argument("--settle", type=float, default=0.75,
                    help="seconds to pause between phases")
    args = ap.parse_args()

    phases = [(p, load(p)) for p in args.phases]
    for name, frames in phases:
        print("%-44s %4d frames" % (name, len(frames)))

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

    results = []
    try:
        for name, frames in phases:
            sent = 0
            replies = []
            for rpt in frames:
                buf = bytes(rpt) + b"\x00" * (REPORT_LEN - len(rpt))
                dev.write(buf)
                sent += 1
                deadline = time.time() + args.reply_wait
                while time.time() < deadline:
                    r = dev.read(REPORT_LEN)
                    if r:
                        b = bytes(r)
                        if len(b) > 4 and b[0] == 0x01 and b[1] == 0xDE:
                            replies.append(b)
                        break
                    time.sleep(0.001)
                time.sleep(args.gap)
            results.append((name, sent, replies))
            print("  %-42s sent %4d   replies %4d" % (name, sent, len(replies)))
            time.sleep(args.settle)
    finally:
        dev.close()

    print("\n--- summary ---")
    for name, sent, replies in results:
        acked = any(r[5:5 + 7].hex() == ACK for r in replies)
        print("%-44s sent %4d  replies %4d  %s"
              % (name, sent, len(replies), "GROUP ACK SEEN" if acked else ""))
        for r in replies[:3]:
            print("      first replies: %s" % r[5:5 + r[2]].hex()[:48])
            break
    return 0


if __name__ == "__main__":
    sys.exit(main())
