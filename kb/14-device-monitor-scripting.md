# 14 – Device Monitor Python Scripting

EScribe's **Device Monitor** embeds an IronPython interpreter that can read and write the mod's live state over USB. For this project it is the fastest way to test a theme condition and the only practical way to gather data on how a cup ages.

Sources: EScribe's own help, `%APPDATA%\Evolv\EScribe Suite\Help\dm_*.html`, and **`EScribe.pdf`
in the install root**, which documents the same API with Evolv's own worked examples. See `13` for
the rest of the install tree.

> **The PDF is old - treat its variable list as a floor, not a ceiling (noted 2026-10-31).** It
> identifies itself as the **"EScribe 1.2 SP5 Manual"**, which predates this install
> (build 2026-05-14) by roughly a decade. The API it documents is still correct as far as it goes -
> `ECig.Puff()`, the indexer, `Recorder`, `Serial.Open` all match - but **the list of variables
> cannot be assumed complete.**
>
> This matters for one tracked item specifically. `09` records the board over-temperature warning
> as blocked because `Board Temperature` is not a Device Monitor variable, so firing and reading
> board temperature cannot happen at once (EScribe holds the HID handle exclusively, `16`). That
> conclusion rests on this decade-old list. **Check the live UI before accepting it:** Device
> Monitor's graph has a checkbox per available variable, and that list is authoritative for the
> build actually installed. If `Board Temperature` is there now, the item is not blocked at all.
>
> The firmware changelog (`13`) shows the exposed set did grow - SP9 added "Expose Board and Room
> Temperature in terms of Celsius" for DNA 60 and DNA 250 - so the old list is demonstrably
> incomplete for later devices.

---

## Running a script

**Diagnostics → Advanced → Run Script.**

Set **Options → User Interface → Researcher** (or Manufacturer) and `Run Script` moves onto the Diagnostics menu directly, without the warning prompt each time. Worth doing on the first run.

**The script runs on a background thread while Device Monitor is running** (Evolv, 2016), so the window stays live and a long loop does not freeze the UI — which is what makes a polling or logging script practical.

The API has been **stable for about nine years**: the function list Evolv posted in March 2016 matches the shipped help in the 2026 build almost exactly. Worth knowing before treating any of it as likely to change.

The interpreter is **IronPython 2** — Evolv's own examples use `xrange` and `.format()`, not f-strings.

---

## The `ECig` object

### Variables

`ECig['Name']` reads, and `ECig['Name'] = value` **writes**. That it is a setter is the important part: it means device state can be driven from the keyboard rather than by rebuilding a theme or swapping hardware.

| | | |
|---|---|---|
| `Power` | `Power Set` | `Current` |
| `Temperature` | `Temperature Set` | `Voltage` |
| `Cold Ohms` | `Live Ohms` | `Puffs` |
| `Last Puff Energy` | `Last Puff Power` | `Last Puff Time` |
| `Last Puff Temperature` | `Last Puff Peak Temperature` | |
| `Battery Charge` | `Battery Pack` | `Battery Cell 1` … `Cell 3` |
| `USB Power` | `USB Current` | `USB Voltage` |

These are Device Monitor's names, **not** the numeric field IDs a theme uses (`05`). They overlap but are not the same list — a theme can show far more.

### Methods

| Call | Does |
|---|---|
| `ECig.Puff(seconds)` | Fires the device |
| `ECig.Track(state)` | Adds a variable to the graph. **Tracked variables update faster**, so track anything you intend to poll |
| `ECig.IsTracked(state)` / `ECig.StopTracking(state)` / `ECig.ClearTracking()` | Manage the graph |

---

## Recording

| Call | Does |
|---|---|
| `Recorder.Record(filename)` | Starts a CSV of the graphed variables. **The graph can't be changed while recording** — call `Track()` first |
| `Recorder.StopRecording()` | Stops |
| `Recorder.IsRecording` | Bool |

For a file you control the shape of, write it yourself:

```python
csv = CSV.Create(path)
csv.WriteHeader(['when', 'profile', 'cold ohms'])
csv.Write([stamp, profile, ohms])
csv.Close()
```

---

## Script control, prompts and storage

| Call | Does |
|---|---|
| `Script.Sleep(seconds)`, `Script.RunTime` | Timing |
| `Script.ShouldStop`, `Script.WillStopIfAsked` | Set `WillStopIfAsked = True` if your loop honors `ShouldStop`, so Stop works cleanly |
| `Script.SetStatus(text)`, `Script.Exit()` | Status line, early exit |
| `Script.CreateVector2(x, y)`, `Script.CreateBox2(...)` | Geometry objects, used by the camera API |
| `UI.Message(text[, title])` | Message box |
| `UI.Input`, `UI.InputInteger`, `UI.InputNumber`, `UI.InputChoice`, `UI.InputBox2` | Prompts; each returns `None` on Cancel |
| `UI.GetSaveFilename(ext)` | Save dialog |
| `UI.ShowTextInEditor(text or lines)` | Opens in Notepad |
| `Settings.GetString/GetInteger/GetBox2(key[, default])`, `Settings.SetString/SetInteger/SetBox2(key, value)` | Settings that persist between runs |
| `Directories.Desktop.Path`, `Directories.Documents.Path` | Use these instead of hard-coding a user path |
| `Random.GetNumber(min, max)` | Random in `[min, max]` |

---

## Talking to other hardware

Not needed for this project, but it explains what Device Monitor is really for — it is a bench-test rig for a manufacturer, and we are using a corner of it.

- **Serial** — `Serial.Open(port[, baud])` (default 9600) returns a .NET `System.IO.Stream`.
- **Modbus TCP** — `Modbus.OpenTCP(ip)`, then `Read`/`ReadUInt16`/`ReadMultiple`/`Write`/`WriteUInt16`/`WriteMultiple`, `UseExtendedAddressing()`. Evolv's stated use is automating smoking machines.
- **Power supplies** — Agilent, BK Precision 1688B, Siglent SPD1168X over TCP or serial. Objects expose `Output`, `Current`, `CurrentLimit`, `Voltage`, `VoltageLimit`, `Power`, `PowerLimit`, and mode switches (independent/parallel/series, two- and four-wire, CC/CV load). Not all supplies support everything.
- **Camera** — `Camera.Open(saveKey[, options])`; reads QR and CODE128 barcodes (`GetBarcode`, `GetBarcodes`, and `…Result` variants that also give QR corner positions), and `GetAverageColor(box)` over a `Box2` region. A save key is any string; Device Monitor remembers which camera it meant.
- **NFC** — `NFC.OpenScanner()`, `Scan()`, `GetAllTags()` / `GetAddedTags()` / `GetRemovedTags()`. Tags expose `Text`, `URL`, records, raw NDEF bytes and a unique ID. Evolv suggests it for tracking different atomizers, which is exactly the problem we have with cup identity.
- **ZPL printing** — `Printing.SelectPrinter()`, `ZPL.PrintBarcodes(array, options)` with QR formats `QR-L/M/Q/H`, plus `ZPL.EscapeHex(text)`.
- **Production Utility** — `Production.FirmwareFilename`, `.SettingsFilename` and their display variants.

---

## Evolv's examples

Power sweep with CSV recording (their Example 1, with the hard-coded path replaced):

```python
import time
ECig.ClearTracking()
ECig.Track('Current')
ECig.Track('Voltage')
ECig.Track('Power')
Recorder.Record(Directories.Documents.Path + r'\Test.csv')
time.sleep(1)
for p in xrange(5, 35, 5):
    ECig['Power Set'] = p
    ECig.Puff(3)
    time.sleep(6)
Recorder.StopRecording()
```

Their Example 2 drives a Sabertooth motor controller over serial around a puff, then reads `Last Puff Energy` back — the pattern to copy if a test ever needs external hardware in the loop.

> **That example does not run as written.** It calls `motor.WriteLine(...)`, and the object `Serial.Open()` returns has **no `WriteLine`** — only `Write`, which wants a .NET `Array[Byte]` rather than a string (reported on Evolv's Researcher Forum, 2020, and never corrected in the shipped help). Build the byte array explicitly, or avoid the serial route entirely.

> And for the specific case that thread was chasing — **`ECig['USB Current'] = 0.0` disables charging** on boards with a built-in charger, with no serial port involved. A reminder that the `ECig` indexer writes as well as reads, and is usually the simpler path.

---

## What this is for here

### Testing a theme condition without hardware gymnastics

`Cold Ohms` is settable, so a threshold can be exercised directly:

```python
for ohms in [0.30, 0.45, 0.55, 0.65]:
    ECig['Cold Ohms'] = ohms
    Script.SetStatus('cold ohms = %s' % ohms)
    Script.Sleep(4)          # look at the screen
```

The replace-warning tests on 2026-10-30 (`09`) were run the hard way instead: building themes with deliberately wrong limits, pre-locking cups by editing `EvolvWDColdOhms` in the config, uploading, and photographing the screen. Each round was minutes. This is seconds, and it sweeps a range rather than testing one point.

**Confirm the write lands** before trusting a negative result — read the value back, and watch the screen rather than assuming. A theme reads cold ohms through field 17825794 (`05`); whether a scripted write updates that field the same way a real measurement does is **not yet verified**.

### Putting the replace thresholds on real evidence

They currently rest on a single observed failure, 0.43 → 0.61Ω on one V5 XL (`02`). A logging script turns that into data:

```python
import time
csv = CSV.Create(Directories.Documents.Path + r'\cold-ohms-log.csv')
csv.WriteHeader(['when', 'cold ohms', 'puffs'])
csv.Write([time.strftime('%Y-%m-%d %H:%M'),
           ECig['Cold Ohms'], ECig['Puffs']])
csv.Close()
```

Run it whenever a cup is locked and the thresholds stop being an extrapolation. Logging `Puffs` alongside matters more than the date — wear tracks use, not calendar time.

---

## Limits

- Device Monitor talks to the **live device over USB**. It reads and writes running state, not the stored config — it is not a way to edit a `.ecig`.
- It exposes no theme or screen state, so it cannot report which variant the firmware chose. It changes the inputs; you still read the answer off the screen.
- The variable list above is everything the **1.2 SP5 manual** offers, and that manual is a decade
  older than this install (see the note at the top). Verify against Device Monitor's own graph
  checkboxes before concluding a variable is unavailable. Anything genuinely absent has to be
  tested the slow way.
