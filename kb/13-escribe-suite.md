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
| `EScribe.pdf` | The manual | Not yet mined |
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

## Connecting to the mod

From EScribe's debug log, which is worth knowing if a connection ever misbehaves:

- The mod is a **USB HID** device, **vendor ID 9867, product ID 1075**, reporting as `Evolv DNA 100 Color`, device code `109.1`. The `109` matches `Device="109"` in the root of every `.ecig` (`03`).
- Report lengths are 63 bytes in and out.
- An upload or download opens the HID device several times, sends `get version`, then transfers between `*** START ***` and `*** END ***` markers.
- EScribe logs every message box it shows, including errors. **A malformed theme is reported only as `Failed to open file.`** with no detail — see `07` #23, which is exactly how that bug presented.

The log also carries the device **serial number**. Keep logs out of this repo (`12`).

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
