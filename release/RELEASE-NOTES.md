# Release Notes — Gremlin - Color Themes

Files are named for their version, in the original v1.0 format:

- `gremlin_v<version>_theme.ecigtheme` — the theme on its own
- `gremlin_v<version>.ecig` — the theme plus the four Divine Tribe profiles and their materials

The current release is **v2.2**. Older versions stay in this folder, so a link to a specific version keeps working.

The High Contrast theme is a separate build on its own version track — see [`../high-contrast/RELEASE-NOTES.md`](../high-contrast/RELEASE-NOTES.md).

---

## v2.2

**The new-coil screen now has a LOCK toggle.** Swap a heater with the resistance lock off and the mod asks **NEW COIL?**. Answering **YES, NEW** stores the new cold resistance but leaves the lock *off*, which is easy to miss — and because the prompt only appears while the lock is off, leaving it off means you get asked again on every swap. The toggle is now on that screen, labelled **LOCK?** so it reads as part of the prompt, and you can lock it without walking back through the menu. **Answer the prompt first.** The **LOCK?** row appears once the mod has a resistance stored for the heater, so on a new setup it is not there until you answer YES. The lock holds the stored resistance, so there is deliberately nothing to lock before that — it is no longer possible to lock an empty 0. If the screen closes when you answer, lock it from **MENU → PROFILE**.

The usual sequence with a locked coil: unlock, swap the heater, let it measure, lock again.

**Both vaping profiles now start at 380°F.** DTv5XL was 392°F and QuestCup was 385°F; both now open at the bottom of the usable range so you work *up* to your own sweet spot instead of down from someone else's. The temperature in a profile is a starting point, never a recommendation.

**Lightning Quest runs TCR 120, not 125.** Swab-tested on a DNA100C at 470°F for 10 seconds: TCR 125 scorched the swab tan, TCR 120 left the light gold that means the chip and the cup agree. Divine Tribe publishes 125, which is right for their own board — on a DNA it reads about 5% hot. `materials/questcup-tcr120.csv` replaces the old TCR 125 curve.

**The resistance turns red when a cup is worn out.** Cold resistance on the home screen, and the reading on the new-coil prompt, go red above **0.60Ω** on the V5 XL profile and **0.41Ω** on the QuestCup profile — the same proportional rise over each cup's measured fresh value. A cup's cold resistance creeping up is the main warning before it fails: the one we lost went from 0.43 to 0.61Ω in a fortnight. The cup still fires while the number is red; it just means order another.

Unchanged: all seven looks, every other screen, and the memory footprint — the padlock art is the one already on the home screen, so nothing new went into off-board memory. Cold resistance still ships cleared to 0 and unlocked on all eight slots, so the mod measures your own coil the first time you fire it.

**If you are upgrading,** reload the two vaping profiles (or the full setup) to pick up 380°F and the new Quest curve. Loading the theme alone changes the screens, not the temperatures.

---

## v2.1

Six switchable color themes — Retro, Synth, Toxic, Ice, Desert and Terminal — plus Classic, under **MENU → THEMES**. Turn on one at a time; all off is Classic. Menu titles follow the active theme. LED sequences removed. Theme retitled "Gremlin - Color Themes".

Tested on a DNA100C. On a DNA75C, the tightest color chip, this build uses 93.6% of off-board and 56.0% of on-board memory, so it fits but leaves little room.

---

## v1.0

The original single-look Gremlin theme: main, lock and new-coil screens, session-mode layout, chip status line, red battery under 15%. Still here as `gremlin_v1.0_theme.ecigtheme` and `gremlin_v1.0.ecig`.

Versions v1.1 through v2.0 were development iterations and were never published on their own.

---

## Also here

- `profiles/` — the four profiles individually: `DTv5XL-Profile`, `QuestCup`, and the two cleaning profiles
- `materials/` — the TCR curves, `dtv5xl-tcr200.csv` and `questcup-tcr120.csv`

Setup, calibration and the swab test: [`guides/setup-gremlin-theme-profiles-calibration.md`](../guides/setup-gremlin-theme-profiles-calibration.md).
