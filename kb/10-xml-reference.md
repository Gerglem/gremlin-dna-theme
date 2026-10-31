# 10 – XML Reference: Evolv DNA File Types

A field-by-field reference for every file format used in this project, compiled from reverse-engineering four themes (Gremlin, Frank65 Thelema, Gauges, ProVapers), real EScribe profile exports, and full device configs (EScribe 1.3.x, DNA100C).

Confidence: **C** = confirmed in this project, **H** = consistent across files, **M** = inferred.
Field IDs (the `Field="…"` numbers) are listed in `05-field-id-dictionary.md`.

| Extension | Container | Root XML |
|---|---|---|
| `.ecigtheme` | Zip → `ECigTheme.xml` | `<ECigTheme>` |
| `.ecigprofile` | Zip → `ECigProfile.xml` | `<ECigProfile>` |
| `.ecig` | Zip → `DEScribe.xml` | `<DESabertooth>` |
| `.csv` | Plain text | (material curve) |

All XML is **UTF-8 with BOM**. Zips use deflate, with a single entry.

---

## 1. `.ecigtheme` → `ECigTheme.xml`

### 1.1 Root and top-level elements
```xml
<ECigTheme MinimumVersion="0.0" SaveVersion="1.3.25.4" Author="" Title="Gremlin"
           Color="1" Width="80" Height="160">
  <Comments>…</Comments>
  <Screen ID="Wallpaper" Bitmap="…" />
  <Localization LanguageID="…"> <String ID="…" Text="…" /> </Localization>
  <UIDesigns> <UIDesign ID="1" Data="…" /> … </UIDesigns>
  <UIFonts> <UIFont ID="1" Data="…" /> … </UIFonts>
  <Fading ActiveTime="30" IdleTime="0" FadeInTime="1" FadeOutTime="3" />
  <UIColorSequences> <UIColorSequence ID="…" Data="…" /> </UIColorSequences>
  <ColorScheme> … </ColorScheme>
</ECigTheme>
```

| Element / attribute | Values | Meaning | Conf |
|---|---|---|---|
| `ECigTheme@MinimumVersion` | `0.0` | Minimum EScribe version | H |
| `@SaveVersion` | e.g. `1.3.25.4`, `1.3.27.1` | EScribe version that saved it | H |
| `@Author`, `@Title` | text | Shown in EScribe's theme list | C |
| `@Color` | `1` | Color theme (color DNA chips) | H |
| `@Width`, `@Height` | `80`, `160` | Screen size (portrait) | C |
| `Comments` | text | Description shown under the title in EScribe | C |
| `Screen@ID` | `Wallpaper`, `Wallpaper 2`, `Wallpaper 3` | Wallpapers 0/1/2, referenced by `UIDesign@Wallpaper` | C |
| `Screen@Bitmap` | base64 PNG, 80×160 | Wallpaper image | C |
| `Localization/String@ID,@Text` | e.g. date format `M/d/yy` | Overrides firmware strings. Empty `<Localization />` = defaults | C |
| `UIDesign@ID` | 1…n | Screen ID. **`ChildScreen Screen=N` targets ID N+1** | C |
| `UIDesign@Data` | base64 XML | Screen definition (§1.3) | C |
| `UIFont@ID` | `1`, `2`, `3` | Font slot: 1 = Normal (FontStyle 0), 2 = Big (1), 3 = Small (2) | C |
| `UIFont@Data` | base64 XML | Font definition (§1.6) | C |
| `Fading@ActiveTime` | seconds | Time before the screen dims | H |
| `Fading@IdleTime / FadeInTime / FadeOutTime` | seconds | Idle/off and fade timings | H |
| `UIColorSequence@Data` | base64 XML (§1.7) | Indicator-LED blink patterns | H |

### 1.2 ColorScheme
Colors are **unsigned 32-bit ARGB integers in decimal**, for example `4294967295` = `0xFFFFFFFF` (white) and `4278190080` = `0xFF000000` (black).

| Element | Attributes | Meaning | Conf |
|---|---|---|---|
| `Normal` | `Text`, `Background` | Default text color for controls without `Color` | C |
| `Highlight` | `Text`, `Background`, `Opacity` (0–100) | The highlighted (selected) item | C |
| `HighlightDisabled` | same | Highlighted but not editable | H |
| `Selection` | same | A value being edited | C |
| `Error` | `Text` | Warning/error text color | H |

### 1.3 Screen: `UIDesign` (decoded `Data`)
```xml
<UIDesign Name="MENU" Usage="0" UsageFlags="128" Wallpaper="0" ScreenSize="(80, 160)" CustomTabOrder="1">
  <Up><RoundRobin /></Up>
  <Down><RoundRobin /></Down>
  <Control …> … </Control>
</UIDesign>
```

| Attribute | Values | Meaning | Conf |
|---|---|---|---|
| `Name` | text | Label in Theme Designer (optional) | C |
| `Usage` | `0` generic, `1` lock screen, `2` main screen, `3` new-coil screen | Special role | C |
| `UsageFlags` | `128` | Fire button fires on this screen. Otherwise fire = back | C |
| `Wallpaper` | `0`/`1`/`2` | Which `Screen` wallpaper | C |
| `ScreenSize` | `(80, 160)` | Newer EScribe versions write it | H |
| `CustomTabOrder` | `1` | Highlight order follows ZOrder rather than position (ProVapers) | M |

**`Up` / `Down` children** (what the up/down buttons do when no item is being edited):
| Element | Meaning | Conf |
|---|---|---|
| `RoundRobin` | Move the highlight to the next/previous selectable control, wrapping around | C |
| `ParentScreen` | Go back | H |
| `SiblingScreen Screen="N"` | Jump to screen ID N+1 (page flipping) | H |
| `MainScreen` | Go to the main screen | H |

### 1.4 `Control`
```xml
<Control UpdateLive="1" InitiallyHighlighted="1" Location="(x, y)" Size="(w, h)" ZOrder="n">
  <!-- one or more child elements: the first without <Compare> is the default -->
</Control>
```
| Attribute | Meaning | Conf |
|---|---|---|
| `Location`, `Size` | Pixels, origin at top-left | C |
| `UpdateLive` | `1` = refresh while firing ("Update while firing"). Required for live readouts | C |
| `InitiallyHighlighted` | `1` = highlighted when the screen opens | C |
| `ZOrder` | Draw order (newer EScribe). Without it, file order applies | H |

**Child elements:** `Label`, `Field`, `Picture`, `Meter`, `Toggle`, `Status`, `Memo`, `Chart`, `Hidden`.
**Variant rule:** the first child without `<Compare>` is the default. Children with `<Compare>` replace it when true, and the last true one wins. Selectability comes from having an `Action` or an editable `Setting` (no `ReadOnly`).

### 1.5 Child elements

**Common attributes**
| Attribute | Values | Meaning |
|---|---|---|
| `Color` | `(r, g, b, a)` floats 0–1 | Text color. **Omit for default white so the highlight colors apply** |
| `FontStyle` | `0` Normal, `1` Big, `2` Small | Font slot |
| `HAlign` / `VAlign` | `0` left/top, `1` center, `2` right/bottom | Alignment within the control |
| `Status` | text | **Help text** shown in any `Status` element while this control is highlighted. Gremlin strips these |

**`Label`**: static text. Attributes: `Text`, common attributes. Children: `Action`, `Compare`, `Padding`. **Paints an opaque background.**

**`Memo`**: text block (seen once: `Text="Resample"` with an Action). Same attributes as Label.

**`Field`**: live or editable value. Children: `Source/Setting`, `Action`, `Compare`, `Padding`.
- **Format strings (from EScribe's own help, not yet used here):** a Field can carry a format in which `#` marks where the number goes — `#W` renders `10.0W`, `#V` renders `4.20V`, `You have taken # puffs` renders the count inline. That is a cleaner way to label a value than a separate Label control, and it costs no extra control.
- **Inline color and font tags:** a Label's text and a Field's format can both carry tags that switch color or font partway through, so one control can mix them — e.g. a number in white with its unit in gray. The palette slots are the "Extra Color" entries in Theme Designer's Appearance tab. Also unused here.
```xml
<Field FontStyle="1" HAlign="1" VAlign="1">
  <Source><Setting Field="16778242" Decimals="0" HideUnits="1" ReadOnly="1" StepSize="2" /></Source>
</Field>
```
| `Setting` attribute | Meaning | Conf |
|---|---|---|
| `Field` | Field ID (see `05`) | C |
| `Decimals` | `0`–`4`; omitted = automatic | C |
| `HideUnits` | `1` = hide the firmware unit (Ω, °F, W, s) | C |
| `ReadOnly` | `1` = display only (not selectable) | C |
| `StepSize` | `2`, `3` seen. Edit step multiplier | M |

**`Picture`**: image. `Image` = base64 PNG (RGBA, transparency respected). Also `HAlign`, `VAlign`, `PictureEncoding="0"`, `Status`. Children: `Action`, `Compare`.

**`Meter`**: fill bar. `Full`/`Empty` = base64 PNGs; the Full image is cropped to the value and drawn over Empty.
| Attribute | Values | Meaning |
|---|---|---|
| `Orientation` | `0` vertical, `1` horizontal | Fill axis |
| `Direction` | `0`/`1` | Fill direction |
| `DragMarker`, `VisualStyle`, `MeterEncoding`, `HAlign`, `VAlign` | `0` | Newer EScribe defaults |
Children: `Source/Setting` (editable if not ReadOnly, e.g., brightness), `Compare`.

**`Toggle`**: on/off switch. `Full` = ON image, `Empty` = OFF image, `ToggleEncoding="0"`. Children: `Source/Setting`, `Compare`. Select flips it.

**`Status`**: the chip's status text ("Firing," "No Atomizer," …) plus highlighted-control help text. Attributes: `Color` (works), `FontStyle`, `HAlign`, `VAlign`. Children: `Compare`, `Padding`.
- Paints an opaque background while active.
- **Put it in its own control, unconditional.** It rendered blank inside conditional variants.
- Needs height ≥ the font's line height (Built Small: ≥19px).

**`Chart`**: Device Monitor graph. `TimeBarColor="(r,g,b,a)"`, `Status`. Children: `Action`.

**`Hidden`**: draws nothing (used as a default or variant).

**`Padding`**: `<Padding Left Top Right Bottom />` in pixels.

**`LiveViewReadout`**: appears with `Field`/`ReadOnly` (fields 1, 2, 6, 65538, 65542, 131074, 196610, 655361, 1048578). Selects what the Device Monitor live view records (M).

### 1.6 `Compare`: conditions

> **`<Compare>` is a compiled form.** Theme Designer authors conditions as **expressions** - a text
> box with `and`, `or`, `not`, six comparisons and a math library including `if()` and `known()`
> (`15`). The elements below are what that compiles to, inferred from reading themes. Treat the
> operator numbers as our best reconstruction of a compiler's output, not as the format's own
> vocabulary - which is why the table has gaps and disagreements.

```xml
<Compare Operator="1" Field="17825798" RefValue="0" />
<Compare Operator="64"> <Compare …/> <Compare …/> </Compare>
```
| Operator | Meaning | Conf |
|---|---|---|
| `0` | (seen; likely "always" or "==") | M |
| `1` | value ≠ RefValue | C |
| `2` | value > RefValue | **C** (on-device 2026-10-30, the probe build). No other theme seen uses `2` or `3`; Copyman's expresses comparisons with `130` / `131` instead |
| `3` | value < RefValue | C |
| `4` | **equals.** Theme Designer compiles `=` to this, not to `129` (2026-10-30). Previously guessed as ≥/≤, which was wrong | **C** |
| `128 + n` | negated form of n (`130` ≤; `131` ≥). **`129` is NOT equality — it does not resolve on this firmware.** Proven on hardware 2026-10-30 (`09`), and EScribe corroborates by zeroing the `RefValue` of any `129` compare it round-trips (`07`). Use **operator 4**. | `129` **disproved**. `130` / `131` **H+** — Copyman's theme uses them 1 and 7 times, together on field `1179649` to bracket a range, which is consistent with ≤ and ≥ but does not prove which is which |
| `64` | **AND of the nested Compares. Confirmed - this is exactly what Theme Designer emits for the word `and`** (2026-10-30, generated file diffed against ours). An earlier conclusion that 64 was unsupported was wrong; see `07` #25. | **C** |
| `65` | OR of the nested Compares | **H+** — used by **Copyman's** third-party theme (`13`), e.g. `<Compare Operator="65"><Compare Operator="1" Field="419954690" RefValue="0" /><Compare Operator="1" Field="419889154" RefValue="0" /></Compare>` on a preheat field. That theme runs, so **nesting itself works** and operator 64 failing is about that value, not the structure. Not vendor-confirmed: Evolv's own Default Theme contains no conditions at all. |
`RefValue` is numeric and compared in the field's units (%, °F, seconds…).

### 1.7 `Action`
`<Action><ChildScreen Screen="3" /></Action>` on a Label, Picture, Field, Memo, or Chart.
| Element | Meaning | Conf |
|---|---|---|
| `ChildScreen Screen="N"` | Open screen ID N+1 | C |
| `ParentScreen` | Back one level | C |
| `SiblingScreen Screen="N"` | Switch to screen ID N+1 (same level) | H |
| `MainScreen` | Home | C |
| `LockScreen` | Lock screen | H |
| `ResampleOhms` | Re-measure cold resistance | C |
| `NewCoilAccept` / `NewCoilReject` / `NewCoilResample` | New-coil screen choices | C |
| `ResetStatistics` | Reset puff stats | H |
| `ResetDeviceMonitor` | Clear recordings | H |
| `SetUnlockSequence` | Record an unlock button sequence | H |
| `RecordingPreviousPuff` / `RecordingNextPuff` / `RecordingNewestPuff` | Browse recorded puffs | H |

### 1.8 Font (decoded `UIFont@Data`)
```xml
<Font Name="Built SemiBold" Size="18">
  <Metrics Ascender="20" Descender="5" />
  <Char Codepoint="48" Bytes="…" Width="8" Height="17" XOffset="0" YOffset="-16" XAdvance="8" />
</Font>
```
| Item | Meaning |
|---|---|
| `Name`, `Size` | Informational |
| `Metrics@Ascender/Descender` | Line metrics. Line height = sum (affects control height needed) |
| `Char@Codepoint` | Unicode code point. Include Ω as 937 **and** 8486 |
| `Char@Bytes` | base64, one byte per pixel (alpha 0–255, row-major, Width×Height) |
| `Width`, `Height` | Glyph bitmap size |
| `XOffset`, `YOffset` | Placement. YOffset is from the baseline (negative = up) |
| `XAdvance` | Cursor advance |
A missing glyph renders as a box. Built SemiBold: Normal 18 (Asc 20/Desc 5), Big 24 (26/7), Small 13 (14/4).

### 1.9 LED color sequence (decoded `UIColorSequence@Data`)
```xml
<Sequence>
  <Entry Time="1"> <Color R="0" G="0" B="0" /> <Color R="1" G="0" B="1" /> </Entry>
</Sequence>
```
Each entry fades from the first to the second color over `Time` seconds (M). Only matters on mods with an indicator LED.

---

## 2. `.ecigprofile` → `ECigProfile.xml`

Real EScribe export:
```xml
<?xml version="1.0" encoding="utf-8"?><ECigProfile>
  <Screen Name="DTv5XL" />
  <Power Watts="36" />
  <Temperature Fahrenheit="392" />
  <SessionMode Time="60" />
  <Atomizer MaterialName="DTv5XL" TemperatureProfile="…">
    <ColdResistance2 Ohms="0.459" Fahrenheit="70" />
    <PowerOnly />
  </Atomizer>
</ECigProfile>
```
| Element / attribute | Meaning | Conf |
|---|---|---|
| `Screen@Name` | Profile name shown on the device | C |
| `Power@Watts` | Wattage (TC max power, or the wattage setting) | C |
| `Temperature@Fahrenheit` | Set temperature. Omitted for wattage-only profiles | C |
| `SessionMode@Time` | Session length in seconds. Present = Session Mode on | C |
| `Atomizer@MaterialName` | Material name. Must exist on the device (or be created from the curve) | C |
| `Atomizer@TemperatureProfile` | base64 of the curve: `F,R\r\n` header then `°F,relativeR` lines, CRLF | C |
| `ColdResistance2@Ohms, @Fahrenheit` | Stored cold resistance and its temperature. `0` = unmeasured | C |
| `PowerOnly` | Wattage-mode profile (no temperature control). Used with material `Watts` | C |
Preheat, boost, replay, and ohm-lock elements may appear when set (not exercised here, M). Loading a profile doesn't lock ohms; measure and lock afterward.

---

## 3. `.ecig` (full device config) → `DEScribe.xml`

```xml
<DESabertooth Device="109" Version="1" SWVersion="1.3.77.0">
  <Features>
    <Feature Name="EvolvXBrightness" Index="0">…</Feature>
    <NullFeature … />
  </Features>
</DESabertooth>
```
- `Device="109"` = DNA100C (in this config). `SWVersion` = EScribe version.
- **`Feature@Index`** is the array slot: profile number (0–7), material number, font slot, screen number, and so on.
- **Values:** plain numbers, base64 binary/text, or XML-escaped XML (fonts).

**Feature names observed** (108), grouped:
- **Device/meta:** DeviceManufacturerName, DeviceProductName, DeviceSkin, EvolvATFriendlyName, EvolvSerialOutput
- **Theme:** EvolvThemeTitle, EvolvThemeAuthor, EvolvThemeComments, EvolvUIDesign, EvolvFont, EvolvUseFontBaseline, EvolvWallpaper, EvolvColorScheme, EvolvColorSchemeOpacity, EvolvLEDTrack, EvolvFadeTime, EvolvFadeIdleTime, EvolvScreenBrightingTime, EvolvScreenDimmingTime, EvolvScreenOrientation, EvolvScreenRotated, EvolvScreenType
- **Battery:** EvolvBatteryType, EvolvBatterySoftVoltage (cell soft cutoff), EvolvBatteryDischargeCurve, EvolvBatteryLowChargeRate, EvolvBatteryMaxPulsedCurrent(+Time), EvolvBatteryMaxSustainedCurrent, EvolvExternalCharger
- **Output limits:** EvolvOutputMax/MinPower, EvolvOutputMax/MinResistance, EvolvOutputMax/MinTemperature, EvolvOutputMaxPeakCurrent(+Time), EvolvOutputMaxSustainedCurrent, EvolvModResistance, EvolvTemperatureProtectionMandatory
- **Materials:** EvolvCVMaterialDescription, EvolvCVMaterialTemperatureProfile, EvolvCVMaterialTemperatureSensing
- **Profiles (indexed per profile):** EvolvSPProfile, EvolvPSPower, EvolvPSTemperature, EvolvPSTemperatureOff, EvolvPHSPower/Temperature/TemperatureRelative/Off/BoostPunch/BoostOff/BoostMode2 (preheat/boost), EvolvPSHL* (replay), EvolvWDMaterial, EvolvWDColdOhms(+Temperature), EvolvWDOhmLock, EvolvWMEnable / EvolvWMTime (Session Mode), EvolvXHiddenProfile
- **UI/device settings:** EvolvXBrightness, EvolvXCelsiusMode, EvolvXClockMode, EvolvXAutoLock, EvolvXLockTime, EvolvClicksToLock, EvolvXMaxFireTime, EvolvMaxFireTime, EvolvXStealthMode, EvolvXStealthLevel, EvolvXScreenFlipped, EvolvXIndicatorMode, EvolvXLiveViewReadout, EvolvXPassword, EvolvPowerLockPassword, EvolvButtonInputType, EvolvButtonRemap, EvolvOhmLockThreshold, EvolvHLRestriction
- **Thermal model:** EvolvCaseChargingDT0/DT1/DT1Mode/DT1W, EvolvCaseCoolingTimeConstant, EvolvCaseHeatingTimeConstant, EvolvCaseStaticDT, EvolvMax/MinAmbientTemperature
- **Research/limits:** EvolvResearch*, EvolvLimitEnergy/Puffs/Time(+Enabled), EvolvReturnByDate(+PCOnly, Enabled)

Mapping notes (M unless stated): WM = "warm mode" = Session Mode (`EvolvWMEnable`, `EvolvWMTime`). WD = coil/atomizer data. PS = profile setting. PHS = preheat. PSHL = replay ("hold last"). The default Evolv theme's fonts were read from `EvolvFont` (C).

---

### 3.1 Lock and user-toggle notes
- `EvolvXAutoLock` (0/1), `EvolvXLockTime` (seconds, default 240), `EvolvClicksToLock` (default 5), `EvolvXPassword` (unlock sequence, default `FFFFF` = fire ×5), `EvolvPowerLockPassword` (default `SSS`).
- **User Toggles 1–8 (fields 10 + 256·(n−1)) are not stored in `.ecig`.** No Feature or NullFeature holds them.
- Profile names are `EvolvATFriendlyName`, base64 UTF-8, indexed by slot 0–7.

## 4. Material curve `.csv`

```
"Temperature (degF)","Electrical Resistivity"
-100,0.8133
68,1
200,1.002
219.8738170347,1.1687
800,1.8133
```
- Column 1: temperature in °F. Column 2: resistance relative to 68°F (1.0 at 68°F).
- Linear TCR α (per °C ×10⁵): `R = 1 + (α/100000)·(T−68)·5/9`.
- The **200°F → 1.002 / 220°F rejoin** points are the display fix that makes the live-temperature readout behave. Above 220°F the curve is linear.
- Imported via EScribe → Materials → Import Material. Check "Temperature-Sensing." Inside profiles and `.ecig` files, the same points are stored base64-encoded with a `F,R` header.
