# 15 – Theme Designer: the GUI, mapped to the XML

Everything in this project is built by editing XML directly, so Theme Designer has mostly been a viewer. This maps its interface onto the file format, which matters for two reasons: it tells you what Evolv considers a first-class setting, and when something here has no XML equivalent we know about, that is a feature we have not found yet.

Built from screenshots, 2026-10-30. **Incomplete** — tabs and dialogs are added as they are seen.

---

## Window

**Menus:** File · Edit · Options · Tools · Help
**Toolbar:** New · Open · Save · Undo · Redo
**Actions:** `Apply` · `Download Theme` · `Upload Theme` · `Space Used` · a *Share Themes* link
**Tabs:** **Appearance** · **Screens** · **Indicator Light** · **Language** · **Credits**

The tabs line up with the top-level elements of `ECigTheme.xml` (`04`):

| Tab | XML |
|---|---|
| Appearance | `<Screen>` wallpapers, `<ColorScheme>`, `<UIFonts>`, `<Fading>` |
| Screens | `<UIDesigns>` |
| Indicator Light | `<UIColorSequences>` / LED track — **stripped from our releases** (`06`) |
| Language | `<Localization>` — **must stay empty** or dates force to d/M/yy (`07` #13) |
| Credits | `Author` and `<Comments>` on the root element |

`Space Used` is the memory check the release process depends on (`00`).

---

## Appearance tab

### Wallpaper — three slots

Slots 1, 2 and 3, each `Load…` / `Save…` / `None`, over the note *"Screens are 80 pixels wide and 160 pixels tall."* They are `<Screen ID="Wallpaper">`, `"Wallpaper 2"` and `"Wallpaper 3"`, each holding a base64 PNG. A `UIDesign` picks one with its `Wallpaper="n"` attribute; ours are all `Wallpaper="0"`.

### Color Scheme — the highlight colors live here, not on controls

Five rows, each a Text and a Fill swatch, three with an Opacity percentage:

| GUI row | XML element | What it does |
|---|---|---|
| Normal | `<Normal Text Background />` | Default text and background |
| Highlight Read-Only | `<HighlightDisabled … Opacity />` | A highlighted control you cannot edit |
| Highlight Selectable | `<Highlight … Opacity />` | **The selection bar.** Color Themes uses black on white; High Contrast uses black on yellow |
| Selected | `<Selection … Opacity />` | A control being edited |
| Error | `<Error Text />` | Error text; fill is not offered |

This is where the inverted highlight that every menu row depends on is configured — it is a **theme-wide** setting, not a per-control one, which is why no control carries highlight colors.

**Colors here are packed ARGB as an unsigned 32-bit decimal**, not the `(r, g, b, a)` float tuples used on controls. `4294967295` is `0xFFFFFFFF` white, `4278190080` is `0xFF000000` black. Two different color encodings in the same file — don't mix them up.

### Fonts

| GUI label | `FontStyle` | `UIFont ID` | Color Themes |
|---|---|---|---|
| Big Font | `1` | 2 | Built SemiBold 24pt |
| Normal Font | `0` | 1 | Built SemiBold 18pt |
| Small Font | `2` | 3 | Built SemiBold 13pt |

The GUI lists them Big, Normal, Small; the `FontStyle` numbers run Normal, Big, Small; the `UIFont` IDs run Normal, Big, Small. Three orderings for the same three fonts — worth re-reading whenever you touch font sizes. The sizes shown match `04` exactly, so that mapping is now confirmed from the tool and not just inferred.

### Fading

`<Fading ActiveTime IdleTime FadeInTime FadeOutTime />`, in seconds. Ours: active 30, idle 0, fade-in 1.

> **Discrepancy to resolve.** The GUI showed **Fade-out Time 0.7** while our file stores `FadeOutTime="2.97674418604651"`. Either the tool scales this value on load, or the theme open in the designer was not the one in `release/`. Don't edit fade timings by hand until this is settled.

### Miscellaneous — a setting we have no XML for

**Text Positioning: `Use pixel bounds (compatible)`**, a dropdown.

"Compatible" strongly implies a second, newer mode — presumably one that positions text by font metrics rather than by the rendered pixel bounds. Nothing in our themes' root attributes corresponds to it, so it is either stored somewhere we have not looked or only written when changed from the default.

**This is worth investigating.** Every layout in this project is built from measured glyph widths and hand-tuned control heights (`07` #9, #15), and a different positioning mode would change where text lands in its control. If the alternative mode centers text properly on its line box, some of the per-row fudging in the High Contrast layouts could go away.

---

## Screens tab

Three panels: a **control palette** down the left, the **canvas** in the middle (the 80x160 screen, with
everything past 80 px shown as checkerboard), and the **properties** of whatever is selected on the right.
A **preview strip** of every screen runs down the far right, and **Add New Screen** sits under it.

### Control palette, and a naming trap

| Palette | XML element | Used by us |
|---|---|---|
| Label | `<Label>` | 130 |
| Memo | `<Memo>` | - |
| Field | `<Field>` | 74 |
| **Gauge** | **`<Meter>`** | 15 |
| Toggle | `<Toggle>` | 17 |
| Picture | `<Picture>` | 110 |
| Status | `<Status>` | 3 |
| Chart | `<Chart>` | - |
| Hidden | `<Hidden>` | 3 |

**The GUI calls it Gauge; the XML calls it `Meter`.** The battery bar is one. Searching the file for
"Gauge" finds nothing.

### Screen properties, mapped

With nothing selected, the properties panel edits the **Form** - the screen itself.

| GUI | XML | Notes |
|---|---|---|
| Wallpaper: 1 / 2 / 3 / None | `Wallpaper="n"` | **0-indexed**: the XML's `0` is the GUI's `1` |
| Special Usage | `Usage="n"` | The full list, below |
| Fire from this screen | **`UsageFlags="128"`** | Present on our main screen and nowhere else, and the checkbox is clear on the lock screen - which is what this attribute has always been |
| Size | - | Fixed 80, 160 |
| Name | `Name="..."` | Our menu screens carry one; the three special screens do not |
| Exit Up / Exit Down | **no XML equivalent found** | Screen-level navigation we have never used. Not written when unset |
| Tab Order: Automatic / Manual | **not in our XML** | Automatic is the default, so nothing is written |
| Listing Order | **not in our XML** | Appears to be the `UIDesign ID` order |

Buttons: Free Motion - Show Grid - **Screenshot** - Copy Screen - Paste Screen - Delete Screen.

### Special Usage: two screen types we never knew existed

| GUI | `Usage` | Have we built one? |
|---|---|---|
| None | `0` | Yes - every menu screen |
| Lock Screen | `1` | Yes |
| Main Screen | `2` | Yes |
| New Atomizer | `3` | Yes |
| **Power Lock** | `4` | **No** |
| **Theme Change** | `5` | **No** |

`04` and `06` only ever documented 0-3, because those are the ones our themes use. **Power Lock** presumably
shows while the mod's power lock is engaged - the feature behind `EvolvPowerLockPassword` (`03`). **Theme
Change** presumably shows when the active theme switches, which is directly relevant to Color Themes, where
switching looks are the whole point.

Neither has been tried. Both are worth a look before the next feature gets squeezed into an existing screen.

### The preview strip does not evaluate conditions

The strip renders every screen with placeholder values - profile 1, 400F, 250W, cold ohms 0.250. In the
New Atomizer preview the **NEW** value renders **red** at 0.250, when the replace warning only turns red
above 0.41 (`02`). The red is the last variant on that control, so the preview appears to draw the
**last variant regardless of its condition** rather than the one the firmware would pick.

So the preview is good for layout and useless for conditional color. `07` is amended accordingly: use it
to check that things fit, and never to check that a condition works.

## The condition editor - an expression language

This is the most consequential thing in the tool, and it is not what the XML suggested.

**Add Condition** has two inputs:

- **Control** - which element the variant uses: Label, Field, Gauge, Toggle, Picture, Status, Hidden. This is the variant's element type, the thing `04` describes as "a duplicate child element". The same seven appear in the **Change Control** dialog, which swaps a control's type in place. **Memo and Chart are in the palette but not in either list**, so they can be placed but apparently cannot be a conditional variant.
- **Condition** - a **free-text expression box**, with four inserter menus beside it.

### What the inserters offer

| Menu | Contents |
|---|---|
| **measurement** | The full device field list, grouped - the same inventory as `05` |
| **comparison** | `<` &nbsp; `<=` &nbsp; `=` &nbsp; `!=` &nbsp; `>=` &nbsp; `>` |
| **math** | `+ - * / ^ mod`, `pi`, and the functions below |
| **and** / **or** / **not** | Inserted as literal words into the expression |

Functions in the math menu:

| Function | Does |
|---|---|
| `abs(v)` `ceil(v)` `floor(v)` `int(v)` | Absolute value; round up, down, toward zero |
| **`if(test, true result, false result)`** | Picks one of two values |
| `min(a, b)` `max(a, b)` `sqrt(v)` | |
| `sin(deg)` `cos(deg)` `tan(deg)` | Degrees, not radians |
| `discretize(v, step)` | Snaps to steps, rounding down |
| **`known(v)` / `unknown(v)`** | True when the value **is** / **is not** set |

`known()` is interesting on its own: it is a direct test for "has this been measured yet", which is
exactly what the new-coil lock guard approximates by comparing cold ohms against zero (`07` #22).

### What this corrects

**`and` is offered by the tool, so AND is supported.** Our `<Compare Operator="64">` nesting failed on
hardware (`09`), and the conclusion drawn was that the firmware does not support AND. That was too strong.
The right conclusion is that **our encoding of AND was wrong** - operator 64 is our guess at how the tool
encodes the word `and`, and it is evidently not right.

**The `<Compare>` XML is a compiled form, not the authoring language.** Everything in this project has been
written by hand-authoring `<Compare>` elements inferred from existing themes. The tool authors expressions
and compiles them. That explains why our reverse-engineered operator table has odd gaps - `2` and `3` used
by us but by no one else, `130` and `131` used by Copyman - and it means a hand-written condition is only
as good as our guess at the compiler's output.

**The decisive experiment is cheap:** build a condition in the GUI using `and`, save the theme, and read
the XML. One save settles the encoding, and the per-cup replace warning could then be written as the single
condition it should be rather than the five-layer chain that emulates it (`07` #24).

### Tested 2026-10-30: what the editor accepts

| Expression | Result |
|---|---|
| `Atomizer -> Coil -> Cold Ohms > 0.4 and General -> Atomizer/Profile = 1` | **accepted** |
| `Atomizer -> Temperature > Miscellaneous -> Board Temperature` | **rejected**: *Invalid Value - Must be a number!* |

So `and` is real, and **the right-hand side of a comparison must be a literal**. A measurement can be
compared only against a number, never against another measurement - the inserter will put a second
measurement into the box, but the dialog refuses it on OK.

That settles a question this project has gone back and forth on. The limit is real; it is the
*reason* given for it that was wrong earlier (`09`).

### What it does not change

The at-temperature indicator is still blocked, but **for a different reason than recorded** (`09`). The
measurement list has exactly one temperature for the atomizer, `Atomizer -> Temperature`, with no separate
live reading - matching the finding that the setpoint and the live value are the same field. So the
obstacle is the **field inventory**, not the comparison mechanism. If a live temperature were exposed,
an expression could compare the two directly.

---

## Control properties

### Common to every control

| GUI | XML |
|---|---|
| Alignment, a 3x3 grid | `HAlign` and `VAlign` together - nine combinations, one click |
| Color -> Set... | `Color="(r, g, b, a)"` |
| Font: Big / Normal / Small | `FontStyle` 1 / 0 / 2 |
| Padding, four boxes | `<Padding Left Top Right Bottom />` |
| Action -> Set... | `<Action>` |
| Status | the help-text attribute `07` #7 says to strip |
| Location, Size | `Location="(x, y)"`, `Size="(w, h)"` |
| **Z Order** | `ZOrder` - **a first-class field in the GUI.** EScribe writes it on every control;
  our hand-written designs omit it entirely and work, so it is optional, with document order as the
  implicit default |
| Initially highlighted | `InitiallyHighlighted="1"` |

Below those sit six alignment and distribution buttons, and **Add Condition... / Change Control... /
Delete Control**.

### Memo is a multi-line Label

That is the whole difference. Its **Text** box is multi-line where a Label's is a single field, and it
wraps within the control - a Memo at 80x40 rendered "Testing" and "1 2 3..." on two lines. Every other
property matches Label exactly.

Useful where a sentence has to fit a narrow screen without hand-splitting it across two Labels, which
is what the High Contrast lock screen currently does (`11`). Note it **cannot be a conditional
variant**, so it is no use for anything that appears and disappears.

### Chart plots the recorded puff, and we never knew

The surprise of the mapping. A Chart has **one property of its own: `Time Bars`** - and no data source
to choose. It is not a general plotting control; it draws the device's own puff recording, and the
only thing you configure is how many time divisions it shows. The designer previews it with a sine
wave placeholder.

That ties to a field already in the dictionary and never used: **`Recordings -> Chart Present`**
(`05`), which is exactly the condition for "hide this control when there is nothing recorded". The
pieces for a working puff graph are all present.

A 64x64 chart fits comfortably on an 80x160 screen. The data behind it is the same recording the
serial stream exposes at 64 Hz (`17`) - resistance and temperature through a heat cycle - so a theme
could show on the mod what we have only ever looked at in a CSV.

## Still to map

Worked from screenshots. Each item says **what to capture** and **what it would settle**, so this can be
picked up cold. Tick them off here as they land.

### 1. The `and` encoding - do this first

Not mapping, an experiment, and it is worth more than the rest combined.

**Capture:** in the GUI, add a condition to any control using two measurements joined by `and` - for
example cold ohms above a number `and` profile equals 1. Save the theme to a file.

**Settles:** how the tool compiles `and`. Our `<Compare Operator="64">` guess does not work on hardware
(`09`), so every multi-term condition in this repo is currently written as a chain of single-term variants
that emulate one (`07` #24). With the real encoding, the per-cup replace warning collapses from five
layers to one condition. While doing it, also try an expression comparing **two measurements** to see
whether field-to-field comparison compiles.

### 2. Memo and Chart

The two controls nobody here has used. They are in the palette but in neither the Add Condition nor the
Change Control list, so they cannot be conditional variants.

**Capture:** place one of each on a scratch screen, select it, and photograph the whole properties panel.

**Settles:** what they are. A **Chart** on an 80x160 screen is the intriguing one - if it plots puff
history it is a feature this project never knew it had. **Memo** the help describes only as a text block
with a format.

### 3. Field - the richest control

**Capture:** the whole properties panel for a selected Field, and the **Format** box with its `+` menu open.

**Settles:** GUI names for `Decimals`, `HideUnits`, `ReadOnly` and `StepSize` (`10`), and how format
strings are entered. Format strings put the unit inside the value - `#W` renders `10.0W` - so a value can
label itself without a second control. On screens that are full to the pixel, that is real space back.

### 4. Gauge

Ours is the battery bar, and everything about it was inferred from reading files.

**Capture:** properties panel for a selected Gauge.

**Settles:** `Full` / `Empty` images, `Direction`, `Orientation`.

### 5. Label, Toggle, Picture, Status

Mostly confirming. For **Label**, the `Text` box with its `+` tag menu open - inline color and font tags
are documented in EScribe's help and unused here. For **Picture**, whatever `PictureEncoding` is called.

### 6. Common properties, on any control

**Capture:** visible in any of the panels above.

**Settles:** the GUI names behind `Location`, `Size`, the `Status` help-text attribute that `07` #7 says to
strip, `InitiallyHighlighted`, `UpdateLive`, and `ZOrder`. `ZOrder` appears in EScribe's own output but
never in ours, and it is not known whether that matters.

### 7. The action list

**Capture:** the full list offered when attaching an action to a control.

**Settles:** the last reverse-engineered table in `10`. Three entries there - `SiblingScreen`, `LockScreen`
and the recording actions - are marked unverified.

### 8. The remaining tabs and menus

Indicator Light, Language, Credits; the File, Edit, Options, Tools and Help menus; and the **Space Used**
dialog with a DNA75C selected, since that is the memory check every release depends on (`00`).
