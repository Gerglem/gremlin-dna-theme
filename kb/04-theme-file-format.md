# 04 – `.ecigtheme` File Format (reverse-engineered)

## Container
Zip containing a single `ECigTheme.xml` (UTF-8 **with BOM**). Rezip with deflate, keeping the same entry name.

```xml
<ECigTheme MinimumVersion="0.0" SaveVersion="…" Author="" Title="Gremlin" Color="1" Width="80" Height="160">
  <Comments>…description shown in EScribe…</Comments>
  <Screen ID="Wallpaper" Bitmap="<base64 PNG 80x160>" />     <!-- wallpaper 0 -->
  <Screen ID="Wallpaper 2" Bitmap="…" />                      <!-- wallpaper 1 -->
  <Screen ID="Wallpaper 3" Bitmap="…" />                      <!-- wallpaper 2 -->
  <Localization />            <!-- String overrides; cleared, since a populated one forces d/M/yy dates -->
  <UIDesigns> <UIDesign ID="n" Data="<base64 of screen XML>" /> … </UIDesigns>
  <UIFonts>   <UIFont ID="1|2|3" Data="<base64 of font XML>" /> </UIFonts>
  <Fading ActiveTime="30" IdleTime="0" FadeInTime="1" FadeOutTime="2.97…" />
  <UIColorSequences> … </UIColorSequences>   <!-- indicator LED patterns; Gremlin ships these empty -->
  <ColorScheme>
    <Normal Text=ARGB Background=ARGB/> <Highlight …Opacity/> <HighlightDisabled …/>
    <Selection …/> <Error Text=ARGB/>
  </ColorScheme>
</ECigTheme>
```
Colors in ColorScheme are **unsigned 32-bit ARGB integers** (e.g., 4294967295 = white, 4278190080 = black).

## Screen (UIDesign) XML
```xml
<UIDesign [Name="MENU"] Usage="0|1|2|3" [UsageFlags="128"] Wallpaper="0">
  <Up><RoundRobin /></Up> <Down><RoundRobin /></Down>
  <Control [UpdateLive="1"] [InitiallyHighlighted="1"] Location="(x, y)" Size="(w, h)">
     … one or more child elements: Label | Field | Picture | Meter | Toggle | Status | Hidden | Chart | Memo …
  </Control>
</UIDesign>
```
- **Usage:** 1 = lock screen, 2 = main screen, 3 = new-coil screen, 0 = generic screen.
- **UsageFlags="128"** = fire button fires on that screen. Without it, fire acts as **back** (one level up on this firmware).
- **Up/Down** at the screen level: `RoundRobin` (moves the highlight), `ParentScreen`, `SiblingScreen Screen="n"`. The lock screen has no Up/Down.
- **Screen references:** `ChildScreen Screen="N"` targets the **design whose ID = N + 1**.
- Control `UpdateLive="1"` = refresh while firing ("Update while firing" in Theme Designer). This is how the live temperature is shown.

### Child elements
- `Label Text="…" Color="(r, g, b, a)" FontStyle="0|1|2" HAlign="0|1|2" VAlign="0|1|2"` (+ optional `<Action>`, `<Padding Left Top Right Bottom/>`, `<Compare>`). Colors are floats 0–1. **Labels paint an opaque background.**
- `Field` + `<Source><Setting Field="id" [Decimals="n"] [HideUnits="1"] [ReadOnly="1"] [StepSize="n"] /></Source>`. Editable unless ReadOnly. The firmware supplies units (°F, W, s).
- `Picture Image="<base64 PNG>"` (+ optional `<Action>`). Transparent PNGs are fine.
- `Meter Full=PNG Empty=PNG Direction="1" Orientation="0|1"`. Shows `Full` cropped to the value, over `Empty`. Orientation 1 = horizontal. Editable if the Setting isn't ReadOnly (e.g., brightness).
- `Toggle Full=PNG Empty=PNG` + Source Setting: an on/off switch. Select toggles it.
- `Status FontStyle HAlign VAlign [Color]`: shows the chip's status text ("Firing," "No Atomizer," and the highlighted control's `Status="…"` help text). See gotchas.
- `Hidden`: nothing drawn.
- `FontStyle`: **0 = Normal (UIFont 1), 1 = Big (UIFont 2), 2 = Small (UIFont 3).**
- Element attribute `Status="text"` = help text the chip shows in the Status element when that control is highlighted. **Gremlin strips all of these.**

### Conditional children (how variants work)
A control lists several children. The first child **without** `<Compare>` is the default. Later children with a `<Compare>` replace it when their condition is true, and **the last matching one wins**.
```xml
<Compare Operator="1" Field="17825798" RefValue="0" />      <!-- firing != 0 -->
<Compare Operator="64"> <Compare …/> <Compare …/> </Compare> <!-- AND -->
<Compare Operator="65"> … </Compare>                        <!-- OR -->
```
**Operators** (determined by testing): `1` ≠, `129` = (128 = negate), `2` >, `3` <, `4` ≥(?), `130`/`131` negated forms, `64` AND, `65` OR. `3` = "<" is confirmed: Gremlin uses it for the low-battery variant (field 65537, ref 15).

### Actions (`<Action>…</Action>` on Label/Picture)
`ChildScreen Screen`, `ParentScreen`, `SiblingScreen Screen`, `MainScreen`, `LockScreen`, `ResampleOhms`, `NewCoilAccept`, `NewCoilReject`, `NewCoilResample`, `ResetStatistics`, `ResetDeviceMonitor`, `SetUnlockSequence`, `RecordingPreviousPuff`, `RecordingNextPuff`, `RecordingNewestPuff`.

### Selectability
A control is highlightable if it has an Action or an editable (non-ReadOnly) Setting. Theme Designer's "Selectable" checkbox maps to this. Make display-only values `ReadOnly="1"`.

## Fonts (UIFont Data → XML)
```xml
<Font Name="Built SemiBold" Size="18">
  <Metrics Ascender="20" Descender="5" />
  <Char Codepoint="48" Bytes="<base64>" Width="8" Height="17" XOffset="0" YOffset="-16" XAdvance="8" />
</Font>
```
- Bytes = one byte per pixel, row-major, alpha 0–255 (4-bit values duplicated, e.g., 0x77).
- YOffset is relative to the baseline (negative = above).
- Include Ω as **both** U+03A9 (937) and U+2126 (8486). A missing glyph renders as a box. **The shipped fonts carry 937 only**, in Normal and Small but not Big — so a label must use U+03A9, and `Ω` is a plain text label rather than a picture (High Contrast uses it for the ohms row).
- **Built SemiBold metrics:** Normal 18 (digits ~17px), Big 24 (~22px), Small 13 (~13px; line height = 14+4 = **18px**, so Status controls need **≥19px height** or the top gets clipped).
- **Label widths are exact and checkable:** a string's pixel width is the sum of its glyphs' `XAdvance`, so you can measure a label against its control before building. Worked examples at High Contrast sizes (Normal 24, Small 18): `Ω OHMS` = 65px Normal, `NEW COIL?` = 88px Normal but 68px Small (which is why it is Small), `LOCK?` = 53px Normal but 40px Small in a 44px control. Over-wide labels wrap or clip. When parsing the font XML, note `Bytes` is base64 and can contain `/`, so match `[^>]*?` rather than `[^/]*?` to reach `XAdvance`.

## Images
PNG, base64, RGBA. Battery meter images 80×7. Icons are 12×12 pixel art. Wallpapers 80×160 (pure black in Gremlin).
