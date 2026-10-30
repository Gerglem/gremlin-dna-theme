# Gremlin Project: Knowledge Base (start here)

**New AI session?** Read this file first, then every other file in `kb/`. Together they hold everything needed to maintain or extend this project: the DNA100C chip swap, Divine Tribe temperature control, and two custom Evolv DNA themes. Human-facing instructions are in `../AI-GUIDE.md`.

## Current state (keep this section current)
| Item | Version | Where |
|---|---|---|
| **Gremlin - Color Themes** (main theme) | **v2.2** | `../release/Gremlin-Color-Themes.ecigtheme`, full setup `../release/Gremlin-Color-Themes-Full-Setup.ecig` (version-free names; history in `../release/RELEASE-NOTES.md`) |
| **Gremlin High Contrast - Large Text** (low vision) | **v1.1** | `../high-contrast/` (landing page `README.md`, files in `files/`) |
| Gremlin v1.0 (legacy) | v1.0 | `../release/gremlin_v1.0_theme.ecigtheme`, `gremlin_v1.0.ecig` |
| Guides | current | `../guides/chip-swap-thelema-solo-dna100c.md`, `../guides/setup-gremlin-theme-profiles-calibration.md` (old `../reddit/` paths are pointer files kept for a live Reddit link; don't delete) |

Both themes are released and tested on a DNA100C. Memory on the DNA75C (the tightest chip): Color Themes v2.2 uses off-board 93.6% and on-board 56.0% (v2.2 is the v2.1 build with new metadata, so the figures carry over).

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

## How work gets done
- **Builds:** a theme change produces a new versioned file (e.g. `Gremlin-Color-Themes-v2.3-beta1.ecigtheme`). The maintainer loads it in EScribe, tests on the mod, and sends photos. Iterate, then publish under the version-free name and add a `RELEASE-NOTES.md` entry.
- **Memory check:** before any release, the maintainer runs Theme Designer → **Space Used** with the **DNA75C** selected. Both pools must be under 100%. See `07` for what uses which pool.
- **Publishing:** done through Claude Code on the maintainer's machine, which commits with a no-reply identity. The assistant writes the files and a Claude Code prompt; see `12`.
- **Privacy:** nothing that identifies the maintainer goes in the repo. Run the checks in `12` on every change.

## Project conventions
- **File names describe the file, not the version:** `Gremlin-Color-Themes.ecigtheme`, `Gremlin-Color-Themes-Full-Setup.ecig`, `High-Contrast-Profile-<Heater>.ecigprofile`. Published Color Themes files carry no version, so links in the guides and on Reddit survive a release; the version lives in the theme's own description and in `../release/RELEASE-NOTES.md`. Test builds add `-vX.Y-betaN`. High Contrast still versions its filenames — it is released on its own track.
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
