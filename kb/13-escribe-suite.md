# 13 – The EScribe Suite Install

EScribe is Evolv's configuration tool. Its install directory holds firmware for every DNA board, the help system, and — the part worth knowing about — **an automatic backup of your device's configuration before and after every upload**. Those backups are the richest source of real examples in this format outside the repo itself.

Default location on Windows: `%APPDATA%\Evolv\EScribe Suite`.

The copy this document was written from: **EScribe INT, build 2026-05-14** (`Edition.txt` reads `INT`, `BuildDate.txt` has the date). The **INT** edition is the one that matters here — Session Mode needs international firmware (`07` #14), and a US-edition install will not offer it.

---

## What's in the tree

| Path | What it is | Useful? |
|---|---|---|
| `Backups/{GUID}/` | **Automatic config snapshots**, one per upload or download | **Yes — see below** |
| `Help/*.html` | The full help system, 18 real pages | Yes — `14` is written from it |
| `Firmware/<board>/*.sw-service` | Firmware images per board | Yes, for reflashing |
| `EScribe.pdf` | **The Device Monitor scripting manual**, with samples — not a general manual. Shipped with EScribe since 1.2 SP5 | Partly, via `14` |
| `Resources/EScribe.ThemeDesigner/Defaults/*.ecigthemex` | Theme Designer's starting themes | **No — encrypted**, not readable |
| `Resources/`, `Translations/`, `Sounds/`, `Pictures/` | App resources, skins, localization | No |
| `Drivers/USB Serial/` | The USB driver | Only if the mod won't connect |
| `*.dll`, `*.exe` | The application | No |

### Firmware

`Firmware/DNA 100 Color/` holds `SP45`, `SP45_1`, `SP46` and `SP55_1`, all `_INT`. **SP55.1 INT** is the one this build runs and the one Session Mode needs. Every other board has its own folder, so this is also where to look if a different DNA is ever in scope.

### The backups are the real find

Filenames are `YYYY-MM-DD HH_MM - X - <board>.ecig`, where `X` is `U` (before an upload), `D` (after a download) or `A` (automatic). They are **complete device configs in our format**, so they can be opened, diffed and read exactly like anything in `release/`.

Two things they are good for:

- **Recovering a known-good state.** If an upload leaves the mod wrong, the `U` snapshot from just before it is the way back.
- **Reading other people's work.** Any theme that has ever been on the device is preserved in full.

---

## What the backups showed

The snapshots on this machine are from October 2026 and contain four distinct themes: our own **Gremlin**, **Gremlin High Contrast**, **Gremlin - Color Themes**, Evolv's **Default Theme**, and a third-party theme, **Copyman's Gothic DNA250C expanded**.

### Evolv's Default Theme uses no conditions at all

Not one `<Compare>` in any of its screens. So the stock theme is **no guide whatsoever** to what the condition system can do — every variant trick this project uses came from reverse engineering, and nothing in Evolv's own work corroborates it.

### Copyman's theme is the best available reference

It is a full-featured third-party theme, built for a DNA250C and running on this DNA100C, with **19 menu screens** against our 7:

> Battery · LastPuff · Clock · Atomizer · RecordFields · MyStats · SettingsMenu · InfoMenu · System Status · Power Bank · Replay · Recordings · LivePuff · LockConfig · About · ConfirmResetStats · Preheat

Worth reading before building any new screen — it is the only example at hand of someone pushing this format hard. It is also where several condition operators show up in practice (`10`), and it uses field IDs not yet in our dictionary: `1179649`, `85458946`, `393223`, `196609`, `458753`.

**This matters for attribution.** Operators `65` (OR, with nested children), `130` and `131` appear in *Copyman's* screens — not Evolv's. That is real evidence they work on hardware, since the theme runs, but it is a third party's reverse engineering, not vendor documentation. Treat it as a strong hint, not an authority.

### Uploading a theme may not clear the screens above it

One snapshot holds a mix: slots 0–2 are Gremlin's screens, slots 3–21 are Copyman's, under the title "Gremlin". The simplest explanation is that uploading a theme overwrites the slots it uses and **leaves higher slots as they were**.

If that is right it has consequences — stale screens would still occupy memory, and might still be reachable by a `ChildScreen` link. **Unverified**, and logged in `09`. Our published configs are clean either way: the files carry `NullFeature` for every unused slot, so a fresh upload of a full config writes all of them.

---

## There is a Linux build, and it ships the SAME assemblies (2026-10-31)

Evolv publishes a Linux build of the suite - `SetupEScribe2_SP77_INT.run`, announced by James
(Evolv) on the forum in 2017 and maintained since. It runs on **Mono + GTK**.

**The assemblies are byte-identical to the Windows install.** Verified by SHA-256 on the three
that matter:

| Assembly | Bytes | Linux vs Windows |
|---|---|---|
| `DimensionEngineering.dll` | 192,016 | **identical** |
| `Evolv.DNA.dll` | 55,664 | **identical** |
| `DEScribe.Upload.dll` | 76,872 | **identical** |

**Why this matters.** Everything in `16` about the protocol layer - `A.ICT` (CRC-16/CCITT-FALSE)
and `A.DQT` (the framed `Stream`) - is pure managed code with no Windows-specific half. It can be
loaded and driven from **any** .NET or Mono host, headless, including a Raspberry Pi (the
installer ships `aarch64` and `armhf` platform binaries alongside x86-64).

That is the natural home for the `v4.0` Bluetooth bridge: a small Linux host running Mono can
drive Evolv's own transport directly, instead of reimplementing the framing and the CRC.

### Getting the assemblies without installing

The `.run` is a **Makeself 2.3.1** archive wrapping **MojoSetup**. The payload is a plain
(uncompressed) tar appended after the shell header, so it extracts without executing anything:

    TOTAL=$(stat -c%s SetupEScribe2_SP77_INT.run)     # 48,940,445
    tail -c 48926720 SetupEScribe2_SP77_INT.run > payload.tar
    tar xf payload.tar ./common/data/escribe-suite.zip
    unzip escribe-suite.zip

`filesizes=` in the header gives the payload length; the offset is total minus that. The app is
`common/data/escribe-suite.zip`; `ecigstats.zip` and the two launcher zips sit beside it.

### Running it, from the forum thread

| | |
|---|---|
| Dependencies | `mono-complete`, `ca-certificates-mono`, `libgtk-3-0` (Debian/Ubuntu names) |
| Installs to | `~/.local/opt/evolv/escribe-suite`, launcher `launch-escribe-suite` |
| **Do not use sudo** | it creates a root-owned `~/.local/opt` and the installer then fails for the real user. Later versions error out if run under sudo |
| Device permissions | Linux does not know what a DNA is, so only root may open it by default |

The udev rule, all on one line, as `/etc/udev/rules.d/10-local.rules`:

    SUBSYSTEMS=="usb", ATTRS{idVendor}=="268b", MODE:="0666"

Newer builds offer to create this themselves when they cannot reach the device. Note the rule
keys on **vendor 268b**, the same VID this repo uses throughout.

Without the certificate store the suite still runs, but Get Information, Restore Defaults and
ECigStats sync - anything reaching Evolv's servers - will not work. That is fine for protocol
work, which needs none of it.

### The platform split is visible in the install itself

The Windows install already ships all three platform layers side by side:

    DimensionEngineering.Common.Windows.dll     320 KB
    DimensionEngineering.Common.MacOS.dll       258 KB
    DimensionEngineering.Common.UnixGtk.dll     256 KB
    DimensionEngineering.Common.Platform.dll     35 KB   <- the abstraction

So the OS-specific code is isolated in `DimensionEngineering.Common.<Platform>.dll`, and
everything above it - including the protocol layer in `16` - is shared. The byte-identical Linux
assemblies confirm this from the other direction.

**There is a macOS build too** (`SetupEScribe2_SP77_INT.pkg`). It is a **xar** archive: a
gzipped XML table of contents after a 28-byte header, then a heap holding one gzipped **cpio**
payload per component (`EScribe Suite.pkg` and `ECigStats.pkg`). The offsets in the TOC are
relative to the end of the TOC. Its assemblies were **not** hash-compared - the Linux result and
the platform split above already establish the point, so it was not worth the parser.



## The Production Utility - a second way onto the device

`Production Utility - Evolv DNA 100 Color` is a separate application in the suite, not a mode of
EScribe. It exists for factory bring-up: program a device, test it, log the result, repeat.

**Why it matters here.** It writes **firmware and a settings file** to the device in a single
`Program & Test` action, driven entirely by a saved job rather than by clicking through EScribe's
tabs. That makes it the most promising candidate for a scriptable write path - worth grabbing the
functionality from (Jake, 2026-10-31).

What its Setup tab exposes:

| Field | Note |
|---|---|
| Model Name | free text |
| **Firmware File** | Browse / Save. "Select the latest firmware to have it loaded onto the device." |
| **Settings File** | Browse / Save. "Select your mod's default settings file. It can be reloaded by clicking Restore Defaults." |
| Manufacturing Notes | free text |
| Production stage | dropdown, observed value `after assembly` |

Functional tests it can run, with the values seen on this install:

| Test | Parameters |
|---|---|
| **Fire Test** - device fires and reads ohms. Needs a resistor or non-temperature coil | Fire Time 5 s, Fire Power 50 W, Expected Cold Resistance 0.9 - 1.1 ohm, optional Maximum Cell Voltage Drop 0.5 V |
| **Battery Test** - cells have reasonable voltages | Minimum Cell Voltage 3.65 V |
| **Final Configuration** | Fire Power 20 W |

`File` has New / Open / Save, so a job is a file - the shape of that file is **unknown and not yet
examined**. Tabs are Setup, Production and Log.

**Nothing here is captured yet.** Whether `Program & Test` uses the same `F8 2A` frame protocol as
EScribe (`16`) is untested. It is the obvious next capture target after the settings block is
understood, because a tool whose whole job is driven from a saved file is far easier to automate
than a GUI.

### The Fire Test is a programmatic firing gateway (Jake, 2026-10-31)

The functional tests are the most valuable part of this tool, and not for testing.

**The Fire Test fires the device on command, with parameters**, from a saved job: fire time in
seconds, fire power in watts, and an expected cold-resistance window. Nothing else in the suite
does this. EScribe can read live values while *you* hold the button, but it cannot make the
device fire, and it cannot fire it for a specified duration at a specified power.

That matters for two tracked items that are otherwise stuck:

- **Clean-profile temperature** (`09`). The open question is what a Clean profile reports while
  firing, versus a vaping profile. Answering it by hand means holding the button and reading the
  screen, which is exactly the measurement that is hardest to do accurately. A 5-second fire at a
  set wattage, repeatable, with a HID capture running, turns it into a clean experiment.
- **Board over-temperature warning** (`09`). A threshold cannot be chosen without knowing how
  field `6` actually behaves under sustained load. That needs controlled, repeatable firing.

It would also give the project something it has never had: a way to exercise the device without a
human holding a button, which is what any real test of a theme's live readouts requires.

**Unknown and worth capturing early:** whether the Fire Test drives firing over the same `F8 2A`
frame protocol (`16`), or through a production-only command set. If it is the former, firing may
be reachable directly from `tools/dna-hid.py` without the Production Utility at all.

#### It supports scripting officially, since SP66

From Evolv's changelog thread (`Early Firmware and EScribe Suite`), **SP66, 2025-05-30**:

> Production Utility has been upgraded to support scripting and higher throughput operation.

**This install is build 2026-05-14, so it is well past SP66.**

**But read `14` first.** Device Monitor has had documented IronPython scripting for years,
including `ECig.Puff(seconds)` and a settable `ECig['Power Set']`. Controlled firing is already
available and already written up; an earlier version of this section implied it was the thing
Production Utility would unlock, which was wrong.

What Production Utility scripting may still be worth having is **firing without Device Monitor
holding the HID handle**. EScribe holds that handle exclusively (`16`), so anything driven
through Device Monitor cannot run alongside `tools/dna-hid.py`, which is the only thing that
reads board temperature. A job-driven utility might sidestep that. Confirm it does before
investing in it.

Where to look: the `File` New/Open/Save job format, the `Production` tab, and whatever CLI or
script hook SP66 added. Device Monitor's Python scripting (`14`) is the closest existing analogue
and may share the mechanism.

### Other items from the changelog worth knowing

The same thread answers several questions this repo has asked elsewhere:

| Version | Note |
|---|---|
| **SP2** | "Upload Settings turns on the screen like it should" - this is exactly the behaviour seen on 2026-10-31 when a replayed write was applied, and confirms the screen waking is the *success* signal, not a glitch |
| **1.0.34** | "for programmers, the ability to control the buttons via serial commands" - button control over the serial interface (`17`), predating Device Monitor scripting |
| **1.0.39** | Device Monitor gains "Simulate Button Presses" and Python scripting "for scientific study and automation" |
| **SP45** | Introduced device firmware **1.1 SP55.1** with Session Mode - the firmware this mod runs. Also: "on-device trace recording only works for the first 64 seconds of a puff", which bounds any firing study |
| **SP25** | DNA 100 Color first supported (2021-05-07) |
| **SP53.8 / SP55** | DNA 60 Color and DNA 80 Color added |

Note the pattern across the whole thread: **Windows ships first, Mac and Linux follow**, sometimes
by weeks. The Linux beta thread is the canonical source for Linux builds, not this one.



**Caution:** it loads *firmware*, which EScribe's normal upload path does not. Do not run
`Program & Test` casually to see what happens - capture a run only with a known-good firmware
file selected, or with the firmware field deliberately left empty if that is permitted. The fire
and battery tests appear to be independently checkable, so the first capture should try to
exercise a test **without** a firmware file loaded.

## Connecting to the mod

From EScribe's debug log, which is worth knowing if a connection ever misbehaves:

- The mod is a **USB HID** device, **vendor ID 9867, product ID 1075**, reporting as `Evolv DNA 100 Color`, device code `109.1`. The `109` matches `Device="109"` in the root of every `.ecig` (`03`).
- Report lengths are 63 bytes in and out.
- An upload or download opens the HID device several times, sends `get version`, then transfers between `*** START ***` and `*** END ***` markers.
- EScribe logs every message box it shows, including errors. **A malformed theme is reported only as `Failed to open file.`** with no detail — see `07` #23, which is exactly how that bug presented.

The log also carries the device **serial number**. Keep logs out of this repo (`12`).

### It is a composite device, and the serial port is a second way in

Windows enumerates the mod as **two** interfaces under `USB\VID_268B&PID_0433`:

- **`MI_00`** — the HID interface. This is what EScribe uses for settings transfer, the one the debug log opens. Vendor `0x268B` = 9867 and product `0x0433` = 1075, the decimal values the log prints.
- **`MI_01`** — a **USB CDC serial port**, driven by Microsoft's stock `usbser`. It appears as an ordinary COM port (COM4 on this machine), 9600 8-N-1, no flow control. EScribe's **Serial Terminal** (Tools menu, with its own Scripting menu) connects to this.

The second interface is the interesting one. It is a standard serial port, so it is reachable by **anything** — PuTTY, `pyserial`, or Device Monitor's own `Serial.Open('COM4')` (`14`). Whatever command set it speaks is undocumented: the install's help never mentions the Serial Terminal, and the only trace of it in the files is the UI string in `Translations/en.po`. **Unexplored.** The obvious first move is to open the terminal and try `help` or `?`.

---

## Reading these files

They are ordinary `.ecig` zips (`03`), so the tooling in this repo works on them directly. To see what a theme contains:

```python
import zipfile, re, base64
z = zipfile.ZipFile(path)
t = z.read(z.infolist()[0].filename).decode('utf-8-sig')
title = base64.b64decode(re.search(
    r'<Feature Name="EvolvThemeTitle" Index="0">([^<]*)</Feature>', t).group(1))
designs = re.findall(
    r'<Feature Name="EvolvUIDesign" Index="(\d+)">([^<]*)</Feature>', t)
```

Screen XML inside a `.ecig` is **XML-escaped plain text**, not base64 — unlike a `.ecigtheme`, where it is base64 (`03`). Unescape `&lt;` `&gt;` `&quot;` `&amp;` and it reads normally.
