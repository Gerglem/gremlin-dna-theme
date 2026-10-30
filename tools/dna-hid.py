"""Query an Evolv DNA board over its vendor HID interface.

This is the HID path kb/16 set out to find. It needs no EScribe, no COM port
and no driver install - just `pip install hidapi`. It also works where the CDC
serial port does not, notably macOS, because the composite device's Interface
Association Descriptor is not supported there.

Framing, verified on a DNA 100 Color 2026-10-30:

    report id 0x01 | magic 0xDE | length | payload | zero padding to 63 bytes

The payload is the same plain-text `LETTER=ACTION` protocol the serial console
speaks (kb/17), so every command in that table works here unchanged.

The board also *streams* unsolicited reports in the same framing - battery
volts, power, temperature - so a read can return someone else's line. Always
match on the expected prefix rather than taking the first report that arrives.

Read-only by default: it refuses anything that is not a GET, because the same
interface can fire the coil.

    python dna-hid.py
    python dna-hid.py R=GET COLD
    python dna-hid.py --listen 5
    python dna-hid.py --allow-writes "M=2"
"""

import argparse
import sys
import time

try:
    import hid
except ImportError:
    sys.exit("hidapi is not installed.  pip install hidapi")

VID, PID = 0x268B, 0x0433
OUT_LEN = 63
MAGIC = 0xDE

DEFAULT = [
    "E=GET PRODUCT", "E=GET VERSION",
    "M=GET",
    "R=GET COLD", "R=GET STATIC",
    "T=GET COLD", "T=GET SP", "T=GET BOARD",
    "P=GET SP",
    "B=GET", "C=GET%",
    "S=GET PUFFS", "S=GET TIME", "S=GET ENERGY",
]


def is_read_only(cmd):
    # A query is LETTER=GET.  Note C=GET% is one too, so do not demand
    # whitespace after GET.
    return len(cmd) > 2 and cmd[0].isupper() and cmd[1] == "=" and cmd[2:].startswith("GET")


def frame(text):
    payload = text.encode("ascii") + b"\r\n"
    if len(payload) > OUT_LEN - 2:
        raise ValueError("command too long for one report: %r" % text)
    body = bytes([0x01, MAGIC, len(payload)]) + payload
    return body + b"\x00" * (OUT_LEN + 1 - len(body))


def unframe(report):
    b = bytes(report)
    if len(b) < 3 or b[0] != 0x01 or b[1] != MAGIC:
        return None
    return b[3:3 + b[2]].decode("ascii", "replace").strip()


def collect(dev, seconds, prefix=None):
    """Drain reports for up to `seconds`, stopping early on `prefix`."""
    seen = []
    deadline = time.time() + seconds
    while time.time() < deadline:
        line = unframe(dev.read(64))
        if line:
            seen.append(line)
            if prefix and line.startswith(prefix):
                break
        else:
            time.sleep(0.005)
    return seen


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", nargs="*", help="commands to send; default is a standard read-out")
    ap.add_argument("--listen", type=float, metavar="SECONDS",
                    help="listen only, sending nothing, and print what the board streams")
    ap.add_argument("--timeout", type=float, default=1.2, help="reply wait per command")
    ap.add_argument("--allow-writes", action="store_true",
                    help="permit commands that are not GET queries")
    args = ap.parse_args()

    commands = args.command or DEFAULT

    if not args.listen and not args.allow_writes:
        bad = [c for c in commands if not is_read_only(c)]
        if bad:
            print("Refusing to send, these are not read-only queries:")
            for c in bad:
                print("  " + c)
            print("\nThis interface can fire the coil (F=#S) and change limits.")
            print("Pass --allow-writes if you mean it.")
            return 1

    dev = hid.device()
    try:
        dev.open(VID, PID)
    except (OSError, IOError) as exc:
        print("Could not open the DNA over HID: %s" % exc)
        print("Is the mod plugged in?  Check with: python dna-hid.py --listen 1")
        return 1

    try:
        dev.set_nonblocking(1)
        # Deliberately not printing the serial number - it identifies the board.
        print("%s (%s)" % (dev.get_product_string(), dev.get_manufacturer_string()))

        if args.listen:
            print("listening %gs, sending nothing" % args.listen)
            for line in collect(dev, args.listen):
                print("  " + line)
            return 0

        for cmd in commands:
            prefix = cmd[:2]
            dev.read(64)                       # discard anything already queued
            dev.write(frame(cmd))
            replies = collect(dev, args.timeout, prefix)
            match = [r for r in replies if r.startswith(prefix)]
            print("%-18s %s" % (cmd, match[0] if match else "(no reply - unsupported command)"))
    finally:
        dev.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
