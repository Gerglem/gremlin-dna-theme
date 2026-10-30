# Release Notes — Gremlin - Color Themes

The download filenames never change:

- `Gremlin-Color-Themes.ecigtheme` — the theme on its own
- `Gremlin-Color-Themes-Full-Setup.ecig` — the theme plus the four Divine Tribe profiles and their materials

A link you save today keeps working after the next release. To check which version you have, open the file in EScribe and read the theme description — it starts with the version number.

---

## v2.2

**Both vaping profiles now start at 380°F.** DTv5XL was 392°F and QuestCup was 385°F; both now open at the bottom of the usable range so you work *up* to your own sweet spot instead of down from someone else's. The temperature in a profile is a starting point, never a recommendation.

**Lightning Quest runs TCR 120, not 125.** Swab-tested on a DNA100C at 470°F for 10 seconds: TCR 125 scorched the swab tan, TCR 120 left the light gold that means the chip and the cup agree. Divine Tribe publishes 125, which is right for their own board — on a DNA it reads about 5% hot. `materials/questcup-tcr120.csv` replaces the old TCR 125 curve.

**Filenames no longer carry the version.** They used to (`...-v2.1.ecigtheme`), which broke every saved link and every guide on each release. The version now lives in the theme description and in this file.

Unchanged: all seven looks, every screen, and the memory footprint. Cold resistance still ships cleared to 0 and unlocked on all eight slots, so the mod measures your own coil the first time you fire it.

**If you are upgrading,** reload the two vaping profiles (or the full setup) to pick up 380°F and the new Quest curve. Loading the theme alone changes nothing about temperature.

---

## v2.1

Six switchable color themes — Retro, Synth, Toxic, Ice, Desert and Terminal — plus Classic, under **MENU → THEMES**. Turn on one at a time; all off is Classic. Menu titles follow the active theme. LED sequences removed. Theme retitled "Gremlin - Color Themes".

Tested on a DNA100C. On a DNA75C, the tightest color chip, this build uses 93.6% of off-board and 56.0% of on-board memory, so it fits but leaves little room.

---

## v1.0

The original single-look Gremlin theme: main, lock and new-coil screens, session-mode layout, chip status line, red battery under 15%. Kept in `release/` as `gremlin_v1.0_theme.ecigtheme` and `gremlin_v1.0.ecig` — those two keep their version in the name because they are an archive, not the current download.

Versions v1.1 through v2.0 were development iterations and were never published on their own.

---

## Also here

- `profiles/` — the four profiles individually: `DTv5XL-Profile`, `QuestCup`, and the two cleaning profiles
- `materials/` — the TCR curves, `dtv5xl-tcr200.csv` and `questcup-tcr120.csv`

Setup, calibration and the swab test: [`guides/setup-gremlin-theme-profiles-calibration.md`](../guides/setup-gremlin-theme-profiles-calibration.md).
