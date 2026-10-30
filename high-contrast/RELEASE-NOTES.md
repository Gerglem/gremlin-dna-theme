# Release Notes — Gremlin High Contrast: Large Text

This theme is a major departure from the original Gremlin interface — larger text, fewer things on each screen, built for low vision — so it is named for itself and versioned on its own track:

- `files/gremlin_high_contrast_<version>_theme.ecigtheme` — the theme on its own
- `files/gremlin_high_contrast_<version>.ecig` — the theme plus four ready-made profiles

The current release is **v1.2**. The color theme has its own notes in [`../release/RELEASE-NOTES.md`](../release/RELEASE-NOTES.md).

---

## v1.2

**An ohms screen, reached from the menu.** Until now this theme had no resistance control or readout anywhere, so checking or locking a cup meant going back to EScribe. The menu's fourth row is now **Ω**, and it opens a screen showing the heater's locked resistance in large digits, with the lock toggle and a MEASURE action beside it.

The symbol rather than the word: **Ω** is what is printed on cups and quoted in specs, and it reads at a glance where "OHMS" does not.

Fitting it meant repacking the menu: the divider is gone and the five rows run edge to edge. At this text size 160 pixels holds exactly five rows and no more, which is why the ohm controls went to a screen of their own rather than taking a sixth.

**A LOCK toggle on the new-coil screen too.** Answering **YES** to **NEW COIL?** stores the new cold resistance but leaves the lock off, and the prompt only appears while the lock is off — so without this you would be asked again on every swap. Unlock, swap the heater, let it measure, lock again.

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
