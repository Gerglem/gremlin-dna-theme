# Gremlin Project: Knowledge Base (for Claude)

Human-facing instructions for this workflow are in `../AI-GUIDE.md`. Load all files in this folder at the start of a session. Together they contain everything needed to reproduce, maintain, or extend this project: the DNA100C chip swap, the Divine Tribe temperature-control setup, and the custom Evolv DNA theme **"Gremlin."**

## Files
| File | Contents |
|---|---|
| `01-hardware-and-chip-swap.md` | Devices, why the chip swap, parts, procedure, soldering, screen, bezel, power-up, battery settings |
| `02-temperature-control-and-calibration.md` | TCR, swab test, per-heater settings, cleaning, material CSVs, cup health history |
| `03-escribe-files-and-formats.md` | EScribe workflow, firmware editions, `.ecig` / `.ecigprofile` / CSV material formats, Mod settings |
| `04-theme-file-format.md` | Reverse-engineered `.ecigtheme` format: XML, base64 screens, fonts, images, actions, conditions, operators |
| `05-field-id-dictionary.md` | Numeric field IDs → meaning, with confidence level |
| `06-gremlin-design-spec.md` | Gremlin v1.0: every screen, coordinates, behavior, design decisions, version history |
| `07-gotchas-and-lessons.md` | Firmware and tool quirks discovered the hard way. **Read before changing the theme.** |
| `08-build-pipeline.md` | How the theme is generated in code (build kit), and how to make changes |
| `09-open-items.md` | Known limitations and untested items |

Release artifacts are in `../release/`: the theme, profiles, and materials. Photos are in `../images/`.

## Project conventions
- **Versioning:** theme builds are `Gremlin-v0.N.ecigtheme`. v1.0 is the stable release. Next changes → v1.1.
- Theme Author field stays blank.
- Puff statistics and Replay are deliberately left out of the theme.
- **Vaping profiles ship a 60s session length** (Divine Tribe's guidance). Cleaning profiles follow Divine Tribe's burn-off durations instead.

## Device facts at a glance
- **Mod:** Lost Vape Thelema Solo shell, **Evolv DNA100C** (international firmware SP55.1 INT), named **"Gremlin."** Battery: Molicel P42A 21700.
- **Heaters:** Divine Tribe **V5 XL** cups (TCR 200, ~36W) and **Lightning Quest** (TCR 125, 25W).
- **Fresh V5 XL cup cold resistance:** Divine Tribe spec 0.44–0.49Ω.
- TCR values from other mods (e.g., a Pico Plus) do **not** transfer to the DNA. Recalibrate with the swab test.
