# Release Notes — Gremlin - Color Themes

Files are named for their version, in the original v1.0 format:

- `gremlin_v<version>_theme.ecigtheme` — the theme on its own
- `gremlin_v<version>.ecig` — the theme plus the four Divine Tribe profiles and their materials

The current release is **v2.3.03**. (v2.3 is not final: the new-atomizer screen is still being verified — see the knowledge base.) (A v2.3.00 was published and withdrawn the same day — see below.) Older versions stay in this folder, so a link to a specific version keeps working.

The High Contrast theme is a separate build on its own version track — see [`../high-contrast/RELEASE-NOTES.md`](../high-contrast/RELEASE-NOTES.md).

---

## Which file do I want?

- **`gremlin_v2.3.03.ecig`** — the theme plus the four profiles. This is the one to load.
- **`gremlin_v2.3.03_theme.ecigtheme`** — the screens only, if you already have the profiles you want
  and do not want them touched.

`v2.2.05` is kept as the last build before the v2.3 work, in case you want to go back. The
intermediate v2.3.00, .01 and .02 builds were steps along the way and are not here — .00 was
withdrawn the day it was published, and the other two are superseded by .03, which is the same
screens plus one fix.

---

## v2.3.03

**Tested on a DNA100C, all four profiles plus the new-coil prompt.**

**The set temperature is readable again.** On the home screen the `SET` value sits on the white
selection bar permanently, and it was being drawn in a light grey — which on white is nothing at
all. It now takes whatever colour contrasts with the bar, the way every other adjustable value on
that screen already did. This was not new in v2.3; it has been that way for a while.

**Locking a brand-new setup:** when you first load a config the mod has no resistance stored, so the
**NEW COIL?** prompt appears without a **LOCK?** row — there is nothing to lock yet, and the row is
hidden deliberately so it can never latch an empty 0. Answering **YES, NEW** stores the reading and
closes the prompt, so lock it from **MENU → PROFILE** that first time. On later swaps the mod already
has a resistance stored, the **LOCK?** row is there on the prompt, and you can do it without leaving
the screen.

Nothing else changed.

---

## v2.3.02

Profile settings only — the theme is byte-identical to v2.3.01.

The four profiles now match the ones actually in daily use:

| | Name | Watts | Temperature | Session |
|---|---|---|---|---|
| 1 | DTv5XL | 36 W | **385°F** | **120 s** |
| 2 | **Quest** | 25 W | **385°F** | **120 s** |
| 3 | DTv5XL-Clean | 38 W | power only | 120 s |
| 4 | **Quest-Clean** | 35 W | power only | 45 s |

**This reverses the 380°F starting temperature introduced in v2.2.** That change was made on the
reasoning that you should work *up* to your own sweet spot rather than down from someone else's —
but 385°F is the setting that has actually been in use, so the config now says so. It is a starting
point either way, not a recommendation.

Session time on the two vaping profiles goes 60 s → 120 s, and the QuestCup profiles are renamed to
**Quest** and **Quest-Clean** so they fit the screen better.

**The Lightning Quest stays at TCR 120, deliberately.** The source profile this came from carries
TCR 125, which is what Divine Tribe publish, but 125 was swab-tested on this chip and came back tan
at 470°F where 120 gives the light gold that means the chip and the cup agree. 125 reads about 5%
hot on a DNA. Keeping the measured value rather than the published one — confirmed as the intended
setting. Note the loose `Quest.ecigprofile` on disk still carries 125; the config is the correct one.

Cold resistance still ships cleared to 0 and unlocked on all eight slots, as every release does, so
the mod measures your own coil the first time you fire it.

---

## v2.3

Tested on a DNA100C across all four profiles: the resistance reads in the active theme's
color on both V5 XL profiles and red on both QuestCup profiles at resistances past their limits.

**The resistance on the home screen keeps your theme's color again.** v2.2 had to give that up. The
worn-cup warning needs a different limit per cup, and the only way to express that at the time was a
stack of rules that cancelled each other out — the cancelling rule had to paint a color, so the
resistance read plain white whenever a V5 XL was in its normal range, whichever theme you were on.

The warning is now written as what it actually means — *red if the resistance is past 0.60Ω, or past
0.41Ω on either QuestCup profile* — in a single rule rather than five. One rule leaves room for the
theme colors to come back, so the number reads cyan on Retro, sand on Desert, and so on, right up
until the cup is genuinely worn, and then it goes red.

Nothing else changes. Same thresholds, same cups, same behavior on every other screen, and the
profiles and materials in the `.ecig` are identical to v2.2 — no reload needed if you are upgrading.

**v2.3.00 never existed in practice.** It was published and withdrawn the same day: it rearranged the
low-battery warning to protect it from a display limit, testing showed the rearrangement broke it,
and further testing showed the limit was never reaching it. **v2.3.01 is the real v2.3** and shares
none of that change.

---

## v2.2

**The new-coil screen now has a LOCK toggle.** Swap a heater with the resistance lock off and the mod asks **NEW COIL?**. Answering **YES, NEW** stores the new cold resistance but leaves the lock *off*, which is easy to miss — and because the prompt only appears while the lock is off, leaving it off means you get asked again on every swap. The toggle is now on that screen, labeled **LOCK?** so it reads as part of the prompt, and you can lock it without walking back through the menu. **Answer the prompt first.** The **LOCK?** row appears once the mod has a resistance stored for the heater, so on a new setup it is not there until you answer YES. The lock holds the stored resistance, so there is deliberately nothing to lock before that — it is no longer possible to lock an empty 0. If the screen closes when you answer, lock it from **MENU → PROFILE**.

The usual sequence with a locked coil: unlock, swap the heater, let it measure, lock again.

**Both vaping profiles now start at 380°F.** DTv5XL was 392°F and QuestCup was 385°F; both now open at the bottom of the usable range so you work *up* to your own sweet spot instead of down from someone else's. The temperature in a profile is a starting point, never a recommendation.

**Lightning Quest runs TCR 120, not 125.** Swab-tested on a DNA100C at 470°F for 10 seconds: TCR 125 scorched the swab tan, TCR 120 left the light gold that means the chip and the cup agree. Divine Tribe publishes 125, which is right for their own board — on a DNA it reads about 5% hot. `materials/questcup-tcr120.csv` replaces the old TCR 125 curve.

**The resistance turns red when a cup is worn out.** Cold resistance on the home screen, and the reading on the new-coil prompt, go red above **0.60Ω** on the V5 XL profile and **0.41Ω** on the QuestCup profile — the same proportional rise over each cup's measured fresh value. A cup's cold resistance creeping up is the main warning before it fails: the one we lost went from 0.43 to 0.61Ω in two weeks. One side effect worth knowing: on the home screen the resistance now reads plain white rather than taking the active theme's color while a V5 XL is in its normal range. That is the cost of having a different limit per cup, and it was judged the better trade. The cup still fires while the number is red; it just means order another.

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
