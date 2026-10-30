# 06 – Gremlin v1.0 Design Spec

Render: `../images/20-gremlin-screens-render.png`. Release: `../release/gremlin_v1.0_theme.ecigtheme`.

## Global
- **Font:** Evolv default **Built SemiBold** bitmaps (Normal 18 / Big 24 / Small 13), from the default `.ecig`.
- **Background:** pure black (all three wallpapers solid black 80×160).
- **Text:** default white (explicit white colors stripped so the highlight can invert them). Secondary values are gray `(0.62,0.62,0.62)`.
- **ColorScheme:**
  - Highlight: text black, background white, opacity 100 (inverted selection)
  - HighlightDisabled: text 0xFF9F9FA4, background 0xFF333333
  - Selection (editing): text white, background 0xFF1E78FF (blue)
  - Error: 0xFFFF3C28 (red)
- **Icons:** hand-drawn 12×12 white pixel art with a **1px black outline**, so they stay visible on the white highlight. Labels use a 3×5 pixel font (INFO / LITE / SET).
- **Navigation:** up/down = RoundRobin. Only editable or action items are selectable. **Fire:** main screen fires (UsageFlags 128); every other screen has fire = back.
- **No help text:** all `Status="…"` attributes are stripped, because they popped up in the status line and got cut off.
- **Localization:** cleared (US date format M/d/yy).
- **Author:** blank. Title "Gremlin."
- **Description:** "Gremlin theme. For Evolv DNA color chips (DNA75C, DNA100C, DNA250C) with Session Mode firmware (international edition). Requires up, select and down buttons plus fire. Not for non-color DNA chips; DNA60C untested."

## Design IDs (Screen ref = ID−1)
| ID | Screen | Notes |
|---|---|---|
| 1 | Lock (Usage 1) | no Up/Down |
| 2 | Main (Usage 2, flag 128) | |
| 3 | New coil (Usage 3) | |
| 4 | MENU | from SET (Screen 3) |
| 5 | PROFILE | |
| 6 | PREHEAT | |
| 7 | DISPLAY | |
| 8 | LOCK (settings) | |
| 9 | INFO | from the INFO icon (Screen 8) and MENU |
| 10 | CLOCK | |

## Main screen (80×160), controls top to bottom
| Loc (x,y) | Size | Content |
|---|---|---|
| 0,0 | 80×7 | Battery Meter (65537, ReadOnly). Gradient fill red→yellow→purple→blue→green (OKLab interp), white 1px outline. Variant with **red outline when level < 15** (op 3, ref 15). |
| 0,8 | 80×15 | Profile name, Field 262151 Small, editable (switches profile) |
| 2,23 | 76×1 | gray divider |
| 0,24 | 80×26 | **Live temp:** Field 16778242 Big, ReadOnly, dec 0, UpdateLive |
| 0,50 / 38,50 | 36×14 / 42×14 | "SET" label (white, right-aligned) + set temp Field 16778242 Small gray, editable, **InitiallyHighlighted** |
| 2,65 | 76×1 | divider |
| 2,67 | 44×20 | Watts, Field 16843778 Normal, editable |
| 46,67 | 32×20 | Session time, Field 17498114 Small, editable (UpdateLive control) |
| 2,89 / 16,88 | 12×12 / 46×14 | Ω icon (static, not selectable) + cold ohms Field 17825794 dec 3 HideUnits ReadOnly |
| 2,105 / 16,104 | | pulse icon + live ohms Field 1048642 dec 3 ReadOnly UpdateLive |
| 63,94 | 14×14 | Ohm-lock Toggle 85196802 (locked = solid white padlock; unlocked = hollow gray, open shackle) |
| 3,119 | 74×19 | **Unconditional `<Status Color="(1, 0.45, 0.1, 1)" FontStyle="2">`.** Shows the chip's "Firing" (reddish amber) and "No Atomizer," etc. Blank at boot until the first fire. No boxes, no READY. |
| 2,140 / 29,140 / 56,140 | 22×19 | INFO (→Screen 8) / LITE brightness Meter (field 7, editable) / SET (→Screen 3) tiles |

## Lock screen
Battery bar (+ red variant), time (65551, Normal), date (15, Small, gray), **gremlin pixel art** (original design, 60×44: bat ears, green slit eyes, toothy grin) at (10,54), "GREMLIN" label, pack voltage (1, dec 2), battery % (65537; red variant < 15%), Status line at the bottom.

## New coil screen
"NEW COIL?", NEW 1048579 / OLD 1048835 (dec 3), YES, NEW (NewCoilAccept), **NO, OLD (initially highlighted, NewCoilReject)**, MEASURE (NewCoilResample, gray), **LOCK? + ohm-lock Toggle 85196802 (14×14, the same art as the main screen)**, Status. Not shown when ohms are locked, so the toggle is also the way back out: unlock, swap, lock again. The LOCK? label and its toggle are a variant pair (default `<Hidden/>` with the real element carrying `<Compare Operator="1" Field="1048579" RefValue="0" />` on an `UpdateLive` control): they appear only once 1048579 is non-zero, because locking before YES would latch cold ohms, which ships at 0 (`07` #22).

## Menu pages (title Normal at y 2, divider y 19, rows 15px from y 21, label white left x 3, value gray right)
- **MENU:** PROFILE, PREHEAT, DISPLAY, LOCK, INFO, CLOCK (links); STEALTH toggle (65543); BACK (MainScreen).
- **PROFILE:** Profile 262151, Watts, Temp, Coil 18350082, Session (toggle 84672514), Length 17498114, Ohm lock (toggle), Re-measure (ResampleOhms; deliberately off the main screen), BACK.
- **PREHEAT:** Preheat toggle 218103810, Power 151060482, Until 150994946, BACK.
- **DISPLAY:** Bright 7, Stealth, Stay on 720903, Flip 327687, Units 131079, BACK. (T step and W step removed.)
- **LOCK:** Auto lock 393223, After 458759, Clicks 524295, Max puff 655367, Pwr bank 917511, Set unlock (SetUnlockSequence), BACK.
- **INFO** (all ReadOnly): Battery 1, Level 65537, Board 6, Puffs 16777736, Last 100991496, Avg 100925960, FW 2162694, BACK.
- **CLOCK:** Time 65551, Date 15, Format 196615 (value column x 24), BACK.
- **Toggles:** ON/OFF text images, ON light gray 170 / OFF dark gray 100, black-outlined.
- **BACK:** ParentScreen on sub-pages; MENU's BACK uses MainScreen.
- **Reset stats:** deliberately omitted.

## Decisions and rejected ideas
- **Session timer shows session length only.** Live puff time isn't displayable (field 0 / Designer crash).
- **"At temperature" green readout dropped.** Heating Time Done is unsupported on this firmware.
- **READY/FIRING/NO ATOMIZER custom images removed** in favor of the chip's own status text, because the firmware gives no reliable signal for atomizer presence before the first fire.
- **Fonts tried and rejected:** Oxanium (condensed, crisp, and pure pixel variants), a custom 3×5 block font scaled 2×/3× (too blocky, even EPX-smoothed). Evolv's default Built SemiBold.
- **Labels on cold/live/lock icons were removed** (too small). Bottom tiles keep labels.
- **Snowflake (re-measure) on the main screen was removed:** too easy to trigger mid-session.

## Version history (condensed)
v0.1 initial (Built font, main/lock/coil) · v0.2 inverted highlight, outlined icons, Heating Done removed · v0.3 static session length, status attempt · v0.4 new menu screens · v0.5 white labels/gray values · v0.6 author metadata cleared · v0.7 description · v0.8 lock icons · v0.9 Ω icon, re-measure removed from main · v0.10–v0.12 status/box experiments → baked images · v0.13 SET white/value gray, date fix · v0.14–v0.18 custom NO ATOMIZER attempts (false positives) · v0.19–v0.24 chip Status line, boxes removed, READY removed, amber status color, red error color · v0.25 red battery under 15% · v0.26 removed T/W step · **v1.0 = v0.26.**


## Gremlin - Color Themes v2.x
Released file: `gremlin_v2.2_theme.ecigtheme` (theme title "Gremlin - Color Themes").

**Themes:** Classic (all switches off) plus six color themes under **MENU → THEMES**: Retro, Synth, Toxic, Ice, Desert, Terminal. Turn on one at a time. Each theme is a User Toggle (see `05`); if several are on, the last in this order wins: Retro, Synth, Desert, Terminal, Toxic, Ice.

**What a theme recolors:** home screen (live temperature, SET label, resistance values, divider, battery bar, icons) and lock screen (time, date, GREMLIN label, battery bar, gremlin image); in menus, only the **title and its divider**. Menu rows stay white. Full menu coloring was dropped for memory.

**Palettes:** Retro: neon green labels, hot-pink readouts, cyan values. Synth: hot pink, purple, cyan, sunset bar. Toxic: acid lime and purple. Ice: electric cyan, frost blue, white. Desert: sunset orange, turquoise, sand. Terminal: CRT greens. Desert and Terminal use the standard gremlin (memory); the others have recolored gremlins.

**Other v2.x changes:** orange FIRING box over the status line while firing; LOW BATTERY red banner replaces the battery bar under 15%; white profile names with a profile-colored accent line (slots 1–4); PROFILE menu shows the name full-width; CLOCK "Mode"; large font trimmed to temperature characters; LED color sequences stripped.

**Implementation:** `skins.py` (palettes, `SKINS`, `skinned()` / `skinned_img()` variant builders; a skin variant is a duplicate child element with `<Compare Operator="1" Field="<toggle>" RefValue="0" />`), `screens_skinned.py` (home and lock), `menus.py` (titles via `_sktitle`, THEMES screen ID 11).

**Version history (v2.x):** v1.1 FIRING box, profile colors → v1.2 menu wrap fixes → v1.3 LOW BATTERY banner → v1.4 white profile names with colored accent line → v2.0 betas: themes via User Toggles (Contrast built in, then split into its own theme), memory trims → **v2.1**: Retro, Synth, Toxic, Ice, Desert, Terminal; menu titles themed; LED sequences stripped; title "Gremlin - Color Themes" · **v2.2**: ohm-lock toggle on the new-coil screen, labelled **LOCK?** to read as part of the prompt; QuestCup TCR 120 (swab-verified); both vaping profiles start at 380°F.

**Memory (DNA75C, beta15 = v2.1):** off-board 93.6%, on-board 56.0%. Images and fonts use off-board memory; controls and variants use on-board. Off-board is the limit, so any new theme needs image savings first.

**High contrast** is a separate theme: `high-contrast/` (Gremlin High Contrast - Large Text v1.0).
