# 19 – Objectives

What this project is trying to achieve, and where each goal stands. Written 2026-10-31, because
the goals had been carried in conversation rather than in the repo.

Status lines here are summaries. The detail lives in `09` (open items), `16` (device access) and
`13`/`14` (the EScribe suite and its scripting).

---

## The standing goal

**Jake, stated at the outset and unchanged:** *"The goal has always been for you to directly
interface with it. I don't want to use EScribe anymore."*

Everything below serves that. EScribe remains the reference implementation and the thing to learn
from, not the thing to keep using.

---

## v3.0 — direct device editing from Claude

**Reading: solved.** `tools/dna-hid.py` reads the full live state over vendor HID with no EScribe
running (`17` for the command set).

**Writing: solved for replay, blocked for composition.**

| Capability | Status |
|---|---|
| Send a captured settings write and have the device apply it | **Done.** Verified 2026-10-31, 36 W / 385 F -> 40 W / 420 F with EScribe closed, read back to confirm |
| Understand the frame format | **Done.** `F8 2A` for both directions, fixed 341-byte block, 7-bit packed |
| Decode field encodings | **Partly.** Power and temperature are LE16 x 32 in the unpacked stream. The rest of the block is unmapped |
| Compose a block with arbitrary values | **Blocked.** The frame tail is a validated CRC-16/CCITT-FALSE whose covered region is unknown |

**The one blocker:** which bytes the CRC covers. A region search found no match. The algorithm is
known and callable (`A.ICT` in `DimensionEngineering.dll`).

**The preferred route around it:** `A.DQT` is a `Stream` subclass that frames *and* CRCs on the
way out. Driving Evolv's own transport makes deriving the region unnecessary. The assemblies are
pure managed code, byte-identical across Windows and Linux, so this works headless on any
Mono/.NET host.

**Why it matters that a bad write is silent:** it is ACKed, the commit phase runs, and the profile
is left at defaults. Nothing reports an error. Any composed-write work must verify by reading the
value back.

---

## v4.0 — Bluetooth bridge

**Not started, and deliberately last.** An ESP32-S3 or nRF52840 acting as USB host plus BLE
peripheral, so the mod is reachable without a cable.

What 2026-10-31 changed: the natural host is now a small Linux board running Mono with Evolv's own
assemblies, rather than a reimplementation of the protocol on a microcontroller. The installer
ships `aarch64` and `armhf` binaries, so a Raspberry Pi is a supported target (`13`).

---

## Theme work

The themes are the product; the protocol work exists to make editing them tolerable.

| Item | Status |
|---|---|
| `v2.3.03` (Color) and `v1.2.08` (High Contrast) | Shipping. Both pass `tools/check-theme.py` with ceiling warnings only |
| Clean-profile temperature controls | **Open.** Registered test in `09`; first run void, see the checklist there |
| Board over-temperature warning | **Open, unblocked.** `Board Temp` is a Device Monitor variable, so the measurement is scriptable. Needs a threshold, a location and its own control |
| New-coil `LOCK?` row on Color Themes | Untested; needs a cup swap |
| `Profiles\Quest.ecigprofile` regeneration | Optional, from the shipped TCR 120 curve |

**The 8-child ceiling is the standing design constraint.** The home-screen controls at `(0, 0)` on
designs 1 and 2 are already at 8, so anything new needs its own control. `check-theme.py` warns.

---

## Standing constraints

These are not negotiable and apply to every piece of work here.

- **No real name or personal email anywhere.** Commit as
  `Gerglem <91816923+Gerglem@users.noreply.github.com>`.
- **The device serial never enters the repo.** It appears in EScribe window titles, in USB
  enumeration, and in the string descriptors of any raw `.pcapng`. Raw captures stay in
  `Downloads`; only stripped payload extracts are committed. Scan ASCII **and** UTF-16.
- **Published configs ship `EvolvWDColdOhms = 0` and unlocked** (`12`). Bench configs are never
  committed.
- **Leave `EvolvXPassword` and `EvolvPowerLockPassword`** at the Evolv defaults.
- **Brick risk is accepted at vendor-equivalent level** - Jake: *"I understand that I can brick the
  device and all that. I could with their software."* That is not licence to be careless; it means
  a considered experiment does not need re-authorising.
- **Register expected outcomes before running a test**, and never record a verdict that has not
  been waited out.
- **US spelling**, and commands handed to Jake run in **PowerShell 5.1** (`&&` is a parser error).

---

## What is explicitly NOT a goal

- Replacing EScribe's GUI. The aim is programmatic access, not a rival application.
- Firmware modification. Nothing here writes firmware; the Production Utility can, which is why
  `13` carries a caution against running it casually.
- Supporting other DNA boards. This is a DNA100C chip-swapped Thelema Solo. Other boards appear
  only as reference material.
