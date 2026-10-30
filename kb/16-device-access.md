# 16 – Driving the mod programmatically

**Goal:** read and write the device from a command line, without EScribe's GUI in the loop — so a change can be uploaded and checked in seconds instead of by hand.

Two interfaces, and the mod exposes both at once as a USB composite device (`13`):

| | Interface | Status |
|---|---|---|
| **Primary** | **HID** (`MI_00`) — what EScribe uses for settings transfer | In progress, see below |
| Backup | **CDC serial** (`MI_01`, a COM port) — what the Serial Terminal talks to | Unexplored; command set unknown |

HID is the goal because it is demonstrably capable of the whole job: it is how every config this project has ever shipped reached the mod. The serial port is the fallback precisely because we do not yet know what it can do.

---

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

### What is still unknown

- How to obtain the `NHW` cache the factories want.
- How the device stream is opened and handed over — presumably an enumeration API in `DEScribe.Core` or `DimensionEngineering.Common`, neither of which reflects cleanly yet.
- Which member reads settings *out*. `AX` is the candidate.
- Whether any of this works outside EScribe's own process and licensing.

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

### What to try next, in EScribe's own UI

Cheaper and safer than writing raw bytes: connect the Serial Terminal to **Gremlin** and use its
**Command** box. A bare `?` or `help` costs nothing and may print the command set outright. The window
also has its own **Scripting** menu, unmapped, which may already be the structured interface this whole
effort is looking for.

### What COM4 probably is

Given the *Wiring Information* link and that the DNA exposes UART pins, COM4 is more likely a path to
**external** serial hardware wired to the board than a console on the mod. Unconfirmed, but it would
explain the silence, and it downgrades the serial route from "backup plan" to "probably not the
thing at all".

## The serial fallback

COM4 is a standard CDC port (9600 8-N-1, Microsoft's `usbser`), so `System.IO.Ports.SerialPort` reaches it from PowerShell with no extra tooling — confirmed available on this machine. A listen-only probe is written and waiting on the mod being plugged in; it asserts DTR and RTS, which CDC devices often require before they say anything, and writes nothing.

If the port turns out to be a text console, it may be the shorter path to a working CLI regardless of the HID work. Its **Scripting** menu in the Serial Terminal hints that Evolv already exposes something structured over it.

---

## Other options, weighed

- **USB capture** (USBPcap/Wireshark) of EScribe doing a real transfer would reveal the HID protocol exactly, without fighting obfuscation. Heavier setup, but it is the method that cannot fail.
- **Reimplementing HID from scratch** in Python needs a package (`hidapi` or `pywinusb`); none is installed, and pip is available. Only worth it once the protocol is known.
- **Device Monitor's Python** (`14`) already gives live read *and write* of running values, but it is GUI-bound, so it does not reach the goal on its own.
