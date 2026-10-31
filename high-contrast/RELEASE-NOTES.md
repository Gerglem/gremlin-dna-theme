# Release Notes — Gremlin High Contrast: Large Text

This theme is a major departure from the original Gremlin interface — larger text, fewer things on each screen, built for low vision — so it is named for itself and versioned on its own track:

- `files/gremlin_high_contrast_<version>_theme.ecigtheme` — the theme on its own
- `files/gremlin_high_contrast_<version>.ecig` — the theme plus four ready-made profiles

The current release is **v1.2.08**. The color theme has its own notes in [`../release/RELEASE-NOTES.md`](../release/RELEASE-NOTES.md).

---

## v1.2.08

Profile settings only — the screens are identical to v1.2.07.

Profile settings only — the theme is byte-identical to v1.2.07.

Same four profiles as the Color Themes release: **385°F** and **120 s** on DTv5XL and Quest, 38 W /
120 s and 35 W / 45 s on the two cleaning profiles, and the QuestCup profiles renamed **Quest** and
**Quest-Clean**. The Lightning Quest keeps the swab-verified **TCR 120** rather than the published
125. Cold resistance ships cleared and unlocked, as always.

---

## v1.2.07

**The worn-cup warning on the home screen now works.** v1.2.06 put it there — the profile name turns
red once the fitted cup's resistance passes its replace limit — but on the one profile the warning is
meant to leave alone, the name disappeared instead. The name sits on a white highlight band, and the
rule that kept it its normal color was painting it white, on white.

That rule is gone. The warning now simply states the two cases it cares about, so nothing but red is
ever applied and every other profile keeps the name exactly as it has always looked. Behavior is
otherwise unchanged: red above **0.60Ω** on a V5 XL, above **0.41Ω** on a QuestCup, nothing on either
cleaning profile unless the cup is genuinely past its limit.

Nothing else in the theme changed — the OHMS page, the new-coil prompt, and every other screen are
identical to v1.2.06.

Tested on a DNA100C across all four profiles with the menu item highlighted — the case that caused the
v1.2.06 bug — and the name reads normally on both V5 XL profiles and red on both QuestCup profiles at
the resistances that should trigger it.

**Also confirmed in testing:** **MEASURE** on the Ω OHMS page re-reads the resistance. It has been on
that screen since v1.2 and had never actually been pressed.

---

## v1.2

**An ohms screen, reached from the menu.** Until now this theme had no resistance control or readout anywhere, so checking or locking a cup meant going back to EScribe. The menu's fourth row is now **Ω OHMS**, and it opens a screen showing the heater's locked resistance in large digits, with the lock toggle and a MEASURE action beside it.

The symbol *and* the word: **Ω** is what is printed on cups and quoted in specs and reads at a glance, and the word is there for anyone who does not recognize it. Both fit the row at full text size.

Fitting it meant repacking the menu: the divider is gone and the five rows run edge to edge. At this text size 160 pixels holds exactly five rows and no more, which is why the ohm controls went to a screen of their own rather than taking a sixth.

**The resistance turns red when a cup is worn out.** Above **0.60 ohms** on the XL profile and **0.41 ohms** on the QUEST profile, on both the new-coil screen and the ohms screen — the same proportional rise over each cup's measured fresh value. The cup still fires; it means order another.

**The new-coil screen shows the measured resistance.** The number the mod just read is now under the question, at full text size with its Ω unit, so you can see what you are accepting. It is also the main warning you get before a cup fails: a cup on its way out reads higher than it used to — one V5 XL went from 0.43 to 0.61 ohms in a fortnight. A fresh V5 XL reads 0.44 to 0.49.

MEASURE came off that screen to make room. It had no visible effect there anyway, because nothing on the screen displayed the value it changed; it is still on the ohms screen, beside the stored number.

**A LOCK? toggle on the new-coil screen too.** Answering **YES** to **NEW COIL?** stores the new cold resistance but leaves the lock off, and the prompt only appears while the lock is off — so without this you would be asked again on every swap. Unlock, swap the heater, let it measure, lock again. **Answer the prompt first.** The **LOCK?** row appears once the mod has a resistance stored for the heater, so on a new setup it is not there until you answer YES. The lock holds the stored resistance, so there is deliberately nothing to lock before that — it is no longer possible to lock an empty 0. If the screen closes when you answer, lock it from **MENU → Ω OHMS**.

**Both vaping profiles now start at 380°F.** XL was 420°F and QUEST was 385°F. Both now open at the bottom of the usable range so you work up to your own setting rather than down from someone else's.

The padlock art is the color theme's, scaled up and recolored white, so nothing new was added to the mod's image memory.

**If you are upgrading,** reload the profiles (or the full setup) to pick up 380°F. Loading the theme alone changes the screens, not the temperatures.

---

## v1.1

The lock screen now tells you how to unlock the mod instead of only saying **LOCKED**. The full setup ships with auto-lock off, so the mod does not lock itself while you are using it. LED sequences removed.

---

## v1.0

First release. Large-text home screen with the profile name, live temperature and set temperature; a firing takeover that shows only the temperature and **FIRING**; a simplified menu; a lock screen; and a new-coil screen with **NO** selected by default for safety.

---

Installation, screen-by-screen descriptions and the button map: [`README.md`](README.md).
