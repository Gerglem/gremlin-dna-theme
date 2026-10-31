# Gremlin Project: Knowledge Base (start here)

**New AI session?** Read this file first, then every other file in `kb/`. Together they hold everything needed to maintain or extend this project: the DNA100C chip swap, Divine Tribe temperature control, and two custom Evolv DNA themes. Human-facing instructions are in `../AI-GUIDE.md`.

## Current state (keep this section current)
| Item | Version | Where |
|---|---|---|
| **Gremlin - Color Themes** (main theme) | **v2.2.04** (internal) | `../release/gremlin_v2.2.04_theme.ecigtheme`, full setup `../release/gremlin_v2.2.04.ecig` |
| **Gremlin High Contrast - Large Text** (low vision) | **v1.2.04** (internal) | `../high-contrast/` (landing page `README.md`, files `files/gremlin_high_contrast_v1.2.04_theme.ecigtheme` and `files/gremlin_high_contrast_v1.2.04.ecig`) |
| Gremlin v1.0 (legacy) | v1.0 | `../release/gremlin_v1.0_theme.ecigtheme`, `gremlin_v1.0.ecig` |
| Guides | current | `../guides/chip-swap-thelema-solo-dna100c.md`, `../guides/setup-gremlin-theme-profiles-calibration.md` (old `../reddit/` paths are pointer files kept for a live Reddit link; don't delete) |

Both themes are released and tested on a DNA100C. Memory on the DNA75C (the tightest chip): Color Themes v2.2 uses off-board 93.6% and on-board 56.0% (measured at v2.1; v2.2 reuses the main screen's padlock art, so it adds no images).

## Files
| File | Contents |
|---|---|
| `01-hardware-and-chip-swap.md` | Devices, why the chip swap, parts, procedure, soldering, screen, bezel, power-up, battery settings |
| `02-temperature-control-and-calibration.md` | TCR, swab test, per-heater settings, cleaning, material CSVs, cup health |
| `03-escribe-files-and-formats.md` | EScribe workflow, firmware editions, `.ecig` / `.ecigprofile` / CSV formats, reference setups |
| `04-theme-file-format.md` | Reverse-engineered `.ecigtheme` format |
| `05-field-id-dictionary.md` | Numeric field IDs and their meanings, including User Toggles |
| `06-gremlin-design-spec.md` | Gremlin screens and design decisions: v1.0 spec plus the v2.x Color Themes section |
| `07-gotchas-and-lessons.md` | Firmware and tool quirks discovered the hard way. **Read before changing a theme.** |
| `08-build-pipeline.md` | How themes are generated in code, and how to rebuild without the private kit |
| `09-open-items.md` | Open work, known limitations, ideas |
| `10-xml-reference.md` | Field-by-field XML reference for every file type |
| `11-high-contrast-design-spec.md` | High Contrast theme: screens, fonts, layout rules |
| `12-release-and-privacy-checklist.md` | **How to publish safely**: naming, sanitizing `.ecig` exports, PII rules, commit identity |
| `13-escribe-suite.md` | What EScribe's install directory holds: firmware, the automatic config backups, third-party themes to learn from, how the mod connects |
| `17-serial-command-interface.md` | **The mod is a command console.** Plain-text commands over its USB serial port, verified table, no EScribe needed |
| `16-device-access.md` | **Driving the mod from a CLI**: the HID route via EScribe's own .NET assemblies, the serial fallback, and where the risk boundary is |
| `15-theme-designer-gui.md` | Theme Designer's interface mapped onto the XML, and the settings it exposes that we have no XML for |
| `14-device-monitor-scripting.md` | Device Monitor's Python API. **Cold ohms is settable**, so theme conditions can be tested in seconds instead of by rebuilding |

## How work gets done
- **Builds:** every internal build gets a **mini version** — a third number, `vX.Y.NN`, incremented on each change (`gremlin_v2.2.04_theme.ecigtheme`, then `.02`, `.03`). The maintainer loads it in EScribe, tests on the mod, and sends photos. **Bump the mini version on every build you hand over, even a one-line change:** several different `v1.2` builds were loaded on 2026-10-30 and could not be told apart, which cost a round of debugging. At release, drop the mini version (`v1.2.01` → `v1.2`) and add a `RELEASE-NOTES.md` entry.
- **Memory check:** before any release, the maintainer runs Theme Designer → **Space Used** with the **DNA75C** selected. Both pools must be under 100%. See `07` for what uses which pool.
- **Publishing:** done through Claude Code on the maintainer's machine, which commits with a no-reply identity. The assistant writes the files and a Claude Code prompt; see `12`.
- **Privacy:** nothing that identifies the maintainer goes in the repo. Run the checks in `12` on every change.

## Project conventions
- **File names carry the version, in the original v1.0 format:** `gremlin_vX.Y_theme.ecigtheme` (theme) and `gremlin_vX.Y.ecig` (full setup). High Contrast is a major departure from the original Gremlin UI, so it is named for itself and versioned on its own track: `gremlin_high_contrast_vX.Y_theme.ecigtheme`, `gremlin_high_contrast_vX.Y.ecig`. Profiles stay `High-Contrast-Profile-<Heater>.ecigprofile`. **Internal builds carry a mini version, `vX.Y.NN`**, which is dropped at release; the version is in the filename because that is what you read in EScribe's file dialog when choosing what to load.
- Theme Author field stays blank. No personal credit in theme descriptions.
- Vaping profiles ship with **60s sessions** (Divine Tribe guidance). Cleaning: V5 XL 38W/120s, Lightning Quest 35W/45s.
- Published full setups ship with **cold resistance cleared and unlocked** so users lock their own cup.
- High Contrast profiles use **short names** (XL, QUEST, XL CLEAN, Q CLEAN) so they fit large text.
- Puff statistics and Replay are deliberately left out of both themes.
- Write user-facing docs plainly. The High Contrast landing page must stay screen-reader friendly: real headings, numbered steps, descriptive link text, full alt text, no tables, nothing conveyed by color alone.

## Device facts at a glance
- **Mod:** Lost Vape Thelema Solo shell with an **Evolv DNA100C** (international firmware SP55.1 INT). Battery: Molicel P42A 21700.
- **Heaters:** Divine Tribe **V5 XL** cups (TCR 200, ~36W) and **Lightning Quest** (TCR 120, 25W).
- Fresh V5 XL cup cold resistance: Divine Tribe spec 0.44–0.49Ω.
- TCR values from other mods (e.g., a Pico Plus) do **not** transfer to the DNA. Recalibrate with the swab test.
- The chip numbers profiles from **1** (confirmed with the profile accent colors).
