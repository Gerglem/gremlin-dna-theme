# 11 – Gremlin High Contrast - Large Text v1.2: Design Spec

Released file: `../high-contrast/files/gremlin_high_contrast_v1.2_theme.ecigtheme` (theme title "Gremlin High Contrast - Large Text"). User landing page: `../high-contrast/README.md`.

## Goals
Built for low vision. Large text, maximum contrast, only what's needed on each screen. Everything else stays at defaults and is changed in EScribe.

## Fonts (FontStyle → size)
- **0 Normal: Built SemiBold 24.** Evolv's 24 px font plus missing characters synthesized from the 18 px font scaled ×4/3.
- **1 Big: Built 24 scaled ×1.5 (about 36 px).** Temperature characters only: space - . 0–9 : ° C F O f. Digits about 33 px tall.
- **2 Small: Built SemiBold 18** (full character set).
- Measured widths: "450°F" Normal 50 px, Big 74 px. "TEMP" Small 35 px, "WATTS" Small 45 px. A row cannot hold a Small label plus a Normal temperature (35 + 50 > 80), so value rows stack the label above the value.

## Colors
Black background. White text; yellow `(1, 0.92, 0)` for labels and the live temperature; red for low battery; orange `(1, 0.59, 0.08)` for FIRING; orange status text. Highlight: **solid yellow bar, black text**. Editing: **white bar, black text**.

## Screens
**Home (Usage 2, fire fires):**
- y0–19: MENU (link to menu, top left) and battery % (top right; red under 15%)
- y20–24: battery bar (white; red under 15%)
- y24–67: profile name, Small, centered, **two lines tall** so long names wrap instead of clipping
- y68: white divider
- y70–106: live temperature, Big, yellow
- y107–132: "SET" (Small, yellow) + set temperature (Normal, editable, **initially highlighted**)
- y134–159: chip status line (its own row; never overlap it, see `07`)

**Firing takeover:** every home control has a Hidden variant while firing (field 17825798 ≠ 0) and is `UpdateLive`. Only these show: "TEMP" (Normal), the live temperature (Big, yellow), and FIRING (Normal, orange) inside a 76×42 orange frame picture.

**Menu (ID 4):** TEMP (label + large value, y0–41), WATTS (label + large value, y41–82), LIGHT + brightness value (y82–106), **LOCK + ohm-lock Toggle 85196802 (y106–134, 28×28 padlocks: the main theme's 14×14 art scaled ×2 nearest-neighbour and recolored white)**, BACK (y134–160). No profile row (profile is switched on the home screen). Fire also goes back. The divider is gone and the rows are packed edge to edge: at 24 px Normal glyphs, 160 px holds exactly these seven controls.

**Lock (Usage 1):** LOCKED (yellow), FIRE 5X, TO UNLOCK, divider, BATTERY + % (red under 15%), status line.

**New coil (Usage 3):** NEW COIL? (Small, yellow), YES, NO (initially highlighted, for safety), MEASURE, **LOCK + ohm-lock Toggle 85196802 (28×28)**, status. Accepting a new coil stores its cold resistance but does not lock it, which is why the toggle is here.

## Version history
v0.1 first build · v0.2 stop SET/watts wrapping, MENU moved to top · v0.3 firing takeover via hide-all · v0.4–v0.5 two-line profile name, simplified menu · v0.6 status line back in its own row, watts moved to menu · **v1.0 release** · **v1.1** lock screen shows unlock instructions; full setup ships auto-lock off; LED sequences stripped · **v1.2** ohm-lock toggle on the menu and on the new-coil screen, menu re-packed to fit it; both vaping profiles start at 380°F.
