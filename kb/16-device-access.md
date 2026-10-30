# 16 – Driving the mod programmatically

**Goal:** read and write the device from a command line, without EScribe's GUI in the loop — so a change can be uploaded and checked in seconds instead of by hand.

Confirmed in Windows device enumeration, 2026-10-30:

| InstanceId | What |
|---|---|
| `USB\VID_268B&PID_0433\<serial>` | USB Composite Device. **The instance ID is the board serial** - never paste one into this repo (`12`) |
| `...&MI_00` | **HID-compliant vendor-defined device** |
| `...&MI_01` | USB Serial Device (COM4) |

`268B` is Evolv, `0433` this board. Two interfaces, exposed at once as a USB composite device (`13`):

| | Interface | Status |
|---|---|---|
| **Primary** | **HID** (`MI_00`) — what EScribe uses for settings transfer | **SOLVED for read and control, 2026-10-30.** See below |
| Backup | **CDC serial** (`MI_01`, a COM port) — what the Serial Terminal talks to | Unexplored; command set unknown |

HID is the goal because it is demonstrably capable of the whole job: it is how every config this project has ever shipped reached the mod. The serial port is the fallback precisely because we do not yet know what it can do.

---

## SOLVED 2026-10-30: the HID channel is open, and it is the text protocol

`tools/dna-hid.py` reads and drives the board over HID with **no EScribe, no COM port and no driver
install** - only `pip install hidapi`. Verified against the serial baseline on the same board, same
minute:

    E=GET PRODUCT  ->  E=DNA 100 Color      R=GET COLD  ->  R=0.464OHM
    E=GET VERSION  ->  E=311105588          T=GET SP    ->  T=385.00F
                                            S=GET PUFFS ->  S=186

**Evolv's 2015 claim is literally true**: HID is serial tunneled over HID, so every command in `17`
works here unchanged.

### The framing

    report id 0x01 | magic 0xDE | length | payload | zero pad to 63 bytes

The payload is the plain-text line including its `
`, and `length` counts it: `0x0A` for
`B=4.122V
`. Reports are 63 bytes in and out with no feature reports, which matches what EScribe's
own debug log prints on every open.

Two things cost time and are worth knowing:

- **The report ID is `0x01`, not `0x00`.** A write with `0x00` is rejected by Windows and hidapi
  returns `-1` with no further explanation.
- **The board streams unsolicited reports** in the same framing - battery volts, power, temperature,
  on a loop. A read can easily return a line nobody asked for, so always match on the expected prefix.

### It also works where serial does not

`13` notes the CDC port is unusable on macOS, because the composite device needs an Interface
Association Descriptor that macOS does not support. HID has no such problem, so this is the portable
path as well as the fast one.

### Passive observation, which is the way in to the upload protocol

Windows delivers HID input reports to **every open handle**. Opening our own handle while Device
Monitor polls shows Device Monitor's replies arriving live - `W=` clock lines, `U=` USB volts and
watts, `B=-1.659A`, `C=96%`, `X=` flags. So **EScribe's session can be watched without USBPcap**, at
least in the device-to-PC direction.

That is the lever on the one unsolved piece. During an upload the device's side of the conversation is
visible for free; only the PC-to-device direction needs a real capture. Combined with a settings image
we already hold, that may be enough.

**Caveat, learned immediately:** with Device Monitor running, replies interleave and a prefix match can
grab someone else's line - a `S=GET ENERGY` came back `S=291.87F`, a temperature. **Close Device
Monitor for clean reads.**

## What is and is not reachable - settled by Evolv, 2015

From Evolv staff on the Researcher Forum, and it bounds this whole document:

- **All operation and monitoring is reachable** over the plain-text interface. "Anything you can do in
  Device Monitor is a wrapper for command line commands." That part is done, in `17`.
- **Settings and themes are not.** "Loading firmware is encrypted, and the settings bake to a binary
  file for upload." So a `.ecig` cannot be pushed to the mod by any text command - uploading a theme
  needs EScribe, or the HID path below, and the binary format is not published.
- **The HID interface is serial tunneled over HID**, and "that is totally standard". So a CLI over HID
  would speak the *same plain-text commands*, not a separate binary protocol. That is a far smaller
  job than the obfuscated-assembly route suggested, and it is the portable one: on macOS the CDC port
  does not work at all (the composite device needs an Interface Association Descriptor, which macOS
  does not support), while HID-tunneled serial works everywhere.

**So the goal splits in two.** Reading and driving the device: solved, see `17`. Uploading a config:
still requires EScribe or a reverse-engineered binary format, and no amount of serial work changes
that.

## The promising route: call Evolv's own code

EScribe is **.NET**, and its assemblies load and reflect fine from the local install (`%APPDATA%\Evolv\EScribe Suite`). That means the transfer logic can potentially be *called* rather than reimplemented — no protocol reverse engineering, and correctness comes free because it is the vendor's own implementation.

> **Load from the local install, not a copy on a mapped drive.** .NET refuses assemblies from a network location with `0x80131515`; a Google Drive letter counts as remote. This cost a confusing failure before the local path was tried.

### What has been found

`DEScribe.Upload.dll` → `DEScribe.Upload.Programmer`, with two static factories:

```
OCC CreateForDNA(NHW sha1l96Cache)
OCC CreateForDNAColor(NHW sha1Cache)        <- our board family
```

The returned object carries the device link. Most of the assembly is obfuscated (types named `A.OCC`, `A.TOC`), but the members that matter kept their names:

| Member | Reading |
|---|---|
| `Initialize()` | Bring the link up |
| `UserModeVersion` | Matches the `User mode version is …` line in EScribe's debug log, which is how we know this object really is the device connection |
| `Stream` | The underlying device stream |
| `UpdateBegin(bool writable)` / `UpdateCommit()` / `UpdateEnd(bool writable)` | A transaction around a settings change. The `writable` flag is the read/write switch |
| `PrepareUpload(DoUploadPrepareCallback)` → context | Builds an upload |
| `PerformUpload(context, IProgressMonitor, bool dontUpload)` | Executes it — **note the `dontUpload` dry-run flag** |
| `AX(IProgressMonitor, bool[])` → `TOC` | Unidentified; the shape suggests the download/read side |

### Resolved 2026-10-30 by reflection - three of the four

Still inert: nothing below has been executed, only enumerated.

**1. `NHW` is an interface, so we supply it.** `A.NHW` in `DimensionEngineering.Common.dll` has a null
base type and no constructors, and exactly two members:

    byte[] AE(byte[], Nullable<T>)
    void   FE(byte[], int, int, out byte[])

That is a SHA-1 cache contract - the uploader hashes each region so it can skip chunks that have not
changed. We do not need to find an instance: implement the interface, or try `null`. The parameter is
even named `sha1Cache` in `CreateForDNAColor`, which is the one name the obfuscator left alone.

**2. The device link is `OCC.Stream`, type `A.POT`, and it is settable** (`CanWrite = True`). So the
programmer does not have to discover the device - we can open one and assign it.

**3. The opener is `A.BGQ.FE(String, Int32, Int32, Int32, CSH, Int32, IGI) -> POT`** in
`DimensionEngineering.Common.dll`. A string path followed by VID/PID-shaped integers: a HID open by
device path. The path is the one Windows reports, `HID\VID_268B&PID_0433&MI_00\...`.

**4. Reading is `AX(IProgressMonitor, bool[]) -> TOC`,** and `TOC` takes `ctor(byte[])` / `ctor(int)`,
so it wraps a settings image. `OX(int)` and `WX(int, int)` also return `byte[]` and look like
region/range reads.

**Still unknown:** whether any of it runs outside EScribe's process and licensing. That is now the
single open question, and the read path answers it without risking a write.

### The memory model, which came out unobfuscated

`DEScribe.Upload` has exactly four public, unobfuscated types - the intended API:

| Type | Shape |
|---|---|
| `Programmer` | The two factories |
| `Layout.LogicalLayout(IEnumerable<LogicalRegion>)` | `Regions`, **`PCSize`**, **`PCSizeUsed`** |
| `Layout.LogicalRegion(method, size, deviceOffset, pcOffset, noCache, hashWholeRegion, hashChunkSize, tag, readOnly)` | One flash region |
| `Layout.PagingMethod(isPaged, pageSize, minipageSize, sectorSize)` | With named presets: `ReadOnly`, `EEPROM`, `AtmelSAMD21`, **`NuvotonM480`**, `STM32F3`, `STM32H5` |

Two things fall out of this.

**`PCSize` / `PCSizeUsed` is what the Space Used dialog reports** - the memory percentage every release
is checked against (`00`). If the read path works, that number becomes a scriptable check instead of a
dialog someone has to open.

**The board is a Nuvoton M480 family part**, on the evidence of the preset list and the DNA Color
generation - worth confirming, not yet confirmed.

And the design is a **differential uploader**: regions are hashed, and only changed chunks go over the
wire. That explains the SHA-1 cache, and it means an upload is not a blind whole-image write.

### Tested 2026-10-30, in and out of process

Device plugged in and confirmed `Present: True` on all four interfaces; serial baseline
`DNA 100 Color`, cold ohms 0.464, setpoint 385F, 186 puffs.

**`CreateForDNAColor(null)` works.** The SHA-1 cache may be null, so question 1 is closed twice over.
It returns an **`A.ECC`** - so `OCC` is the base and `ECC` the DNA Color implementation - with
`Stream = null` and `UserModeVersion = null`, waiting for a link.

**`HLF.XK()` is not a device list.** It returns an `A.QMQ` holding two empty byte arrays and
`XE = 256`, and `HLF.GK()` also returns 256. That is the hash chunk size, and `QMQ` is the SHA-1 chunk
cache itself - i.e. **`CreateForDNAColor(HLF.XK())` is the intended call**, and `GK()` is not a device
count as its shape suggested.

**`HLF.AS` is null even inside Device Monitor**, with the mod connected and live. So the static
current-device slot is not what Device Monitor's own connection uses, and finding the live link means
looking at the script host's `ECig` object instead.

**Out of process the device layer is simply not initialized** - `HLF.AS` throws. Nothing here works
from a standalone script without reconstructing EScribe's startup through obfuscated code.

### `BVF` is the board registry

`A.BVF` is a sealed class with **16 static instances** - against 17 firmware folders in the install
(`13`), so very nearly one per supported board. Each carries two fields:

| Field | Type | What |
|---|---|---|
| `IE` | `A.CSH` | wraps `Dictionary<A.WSH, object>` from **HidSharp** - that is HidSharp's `OpenConfiguration` / `OpenOption` pair |
| `KE` | `A.VLF` | an enum board code. Values seen: `3`, `131`, `195`, `259`, `1027`, `2051`, `2179` - every one with low byte `0x03` |

Which instance is the DNA 100 Color is not yet known; they are distinguishable only by that code.

### EScribe's HID transport is HidSharp, and that changes the shape of the problem

`HidSharp, Version=2.6.4.0` ships in the install (`HidSharp.dll`, plus `HidSharp.Net.dll` and
`HidSharp.NordicDfu.dll` for the Bluetooth boards). It is **open source**, so although Evolv obfuscated
their copy in place, the library itself is public and documented.

That means `A.BGQ.FE(String, Int32, Int32, Int32, CSH, Int32, IGI) -> POT` is a thin wrapper over
"open this HID device path with these options", and **we never need Evolv's transport code**. A
standalone client can open `MI_00` with stock HidSharp from NuGet, or Python `hid` / `pywinusb`.

What is *not* solved by that is the **protocol** carried over the HID reports. Evolv's 2015 statement
says HID is serial tunneled over HID, which would mean the same `LETTER=ACTION` text we already drive
on COM4 (`17`) - and that gives us nothing new, because text cannot carry a settings image. EScribe
plainly moves binary settings across the same link, so either the tunnel carries more than text or the
upload uses its own report. **That question is now the crux, and it is the one thing reflection cannot
answer.** It needs a capture.

### The next experiment: read, not write

The read path exercises the entire chain - open HID, attach the stream, `Initialize()`, pull an
image - with nothing written to the device. Order:

1. `BGQ.FE(hidPath, ...)` -> `POT`
2. `Programmer.CreateForDNAColor(sha1Cache)` -> `OCC`
3. assign `OCC.Stream`
4. `OCC.Initialize()`, then read `UserModeVersion` - if it matches the `User mode version is ...` line
   in EScribe's debug log, the link is genuinely up
5. `OCC.AX(progress, flags)` -> `TOC`, and compare its bytes against a `.ecig` downloaded by EScribe

A successful read answers the licensing question, proves the HID path, and costs nothing if it fails.
Only then is `PerformUpload(ctx, progress, dontUpload: true)` worth trying.

**The device must be plugged in.** Checked 2026-10-30: all four Evolv interfaces read `Present: False`
with the mod unplugged, so step 1 has nothing to open.

---

## Risk boundary

Enumerating types and reading properties is inert. **Calling the upload path is not.** This is the component that writes firmware and settings to a battery-powered device; a wrong call could leave the mod unbootable.

So:

- **Reading is fair game** — `Initialize()`, `UserModeVersion`, enumeration, and anything that only observes.
- **Writing needs a deliberate decision each time**, and `PerformUpload`'s `dontUpload` flag should be exercised first. Treat a successful dry run as the gate for a real one.
- **Have a recovery path open before the first write.** EScribe's automatic backups (`13`) hold a config from before every upload, and firmware images for this board sit in `Firmware/DNA 100 Color/`.

---

## The Serial Terminal talks to the mod, not to COM4

A correction to the assumption in `13`. The Serial Terminal's **Connect** dialog lists three devices:

- **Gremlin** - the mod itself, named for its loaded theme
- Communications Port (COM1)
- USB Serial Device (COM4)

So it is not only a COM-port terminal: it connects to the **DNA directly**, and that is what the window
titled *Serial Terminal - Gremlin* with "Connected." was attached to. Which also explains why a
listen-only probe of COM4 heard nothing - the mod's command channel is not that port.

The dialog also offers **Rename...** and **Identify**, plus a *Wiring Information* link. **Identify
toggles the mod's display on and off** - a device command with an unmistakable effect, issued from
EScribe over its own link.

That matters more than it looks. It is a **known command with an observable result**, which is the
ideal thing to hunt for when working out a protocol: trigger it repeatedly and whatever changes in the
traffic is the command. If the HID route needs a USB capture, Identify is the signal to capture.

### Tested 2026-10-30: the Gremlin connection answers nothing either

Serial Terminal connected to **Gremlin**, status "Connected." Sent `?`, `help`, `hello`, `dir`, `ls`,
`/`, `/help`, `/?` and an empty line. Every one appeared in the Data pane; **none produced a reply**.

**Resolved:** the View menu has **Local Echo** and it was **on**, so every one of those lines was
EScribe echoing. The mod sent nothing at all - not even an error - and that test said nothing about
the device.

**The display mode is worth knowing about.** View -> Display offers **Text, Decimal, Hexadecimal**
**and CSV**; when seen set to CSV the Send button reads "View CSV". That was the operator experimenting rather than the state during the test, so it does **not** explain the silence - but anything the mod
emits that is not plain text would still be invisible in Text mode. Before concluding this channel is
dead: **turn Local Echo off, set Display to Hexadecimal**, and watch while the mod is idle, while
buttons are pressed, and while it fires.

Either way the text-console idea is finished, for both COM4 and this connection. **The HID protocol is
the remaining road**, and `Identify` - which visibly toggles the mod's display - is the command to
trigger while capturing.

The Serial Terminal's **Scripting** menu is still unopened and is the last cheap thing in this corner.

### What to try next, in EScribe's own UI

Cheaper and safer than writing raw bytes: connect the Serial Terminal to **Gremlin** and use its
**Command** box. A bare `?` or `help` costs nothing and may print the command set outright. The window
also has its own **Scripting** menu, unmapped, which may already be the structured interface this whole
effort is looking for.

### SOLVED 2026-10-30: COM4 is the command console

**Everything in this section's earlier conclusions was wrong, and the error was ours.** COM4 returned
nothing to `?`, `help`, `dir` and friends, and that was read as a dead channel - possibly a path to
external serial hardware rather than to the mod.

It is the mod's command console. The commands are `LETTER=ACTION`, and **an unrecognised command draws
no reply at all**, so every probe looked like silence. With real syntax the board answers immediately:

```
R=GET COLD     ->  R=0.464OHM
E=GET PRODUCT  ->  E=DNA 100 Color
M=GET          ->  M=1
```

**This is the goal of this document, reached.** Full detail, the verified command table and the
`tools/dna-query.ps1` helper are in `17`. What follows below is kept for the record of how the HID
route was scoped, which is still the right path for *writing* a config - but for reading the device
and driving it, the serial console is the answer and needs no reverse engineering at all.

## The serial fallback

COM4 is a standard CDC port (9600 8-N-1, Microsoft's `usbser`), so `System.IO.Ports.SerialPort` reaches it from PowerShell with no extra tooling — confirmed available on this machine. A listen-only probe is written and waiting on the mod being plugged in; it asserts DTR and RTS, which CDC devices often require before they say anything, and writes nothing.

If the port turns out to be a text console, it may be the shorter path to a working CLI regardless of the HID work. Its **Scripting** menu in the Serial Terminal hints that Evolv already exposes something structured over it.

---

## Other options, weighed

- **USB capture** (USBPcap/Wireshark) of EScribe doing a real transfer would reveal the HID protocol exactly, without fighting obfuscation. Heavier setup, but it is the method that cannot fail.
- **Reimplementing HID from scratch** in Python needs a package (`hidapi` or `pywinusb`); none is installed, and pip is available. Only worth it once the protocol is known.
- **Device Monitor's Python** (`14`) already gives live read *and write* of running values, but it is GUI-bound, so it does not reach the goal on its own.
