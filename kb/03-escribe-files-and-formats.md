# 03 – EScribe, Firmware, and File Formats

## EScribe
- Windows and Mac. On Windows it installs to `C:\Users\<user>\AppData\Roaming\Evolv\EScribe Suite\`.
- Tabs: General (profiles), Theme, Safety, Display, Materials, Mod (Safety/Battery), Research. Tools: Device Monitor, Atomizer Analyzer.
- **Theme Designer** is inside EScribe (Theme tab → Theme Designer). It works without the mod connected.
- **Production Utility** add-in (for manufacturers: fire test, battery test). Not needed. If ever used, set the fire test to 36W/3s and an expected resistance of 0.40–0.50Ω.
- A serial command interface exists (9600 baud, address 128 default). Unused.
- Profiles can be edited on-device. Cold ohms can also be locked from the device.

## Firmware
- **International edition required for Session Mode.** This build runs **SP55.1 INT**. The US edition limits feature changes because of FDA rules.
- The DNA100C needs EScribe 2.0 SP77+ for TCR material work.
- **Theme uploads fail with "No Compatible Firmware"** if the theme references a field this firmware doesn't support. Example: Heating Time Done (353173506). See `07-gotchas`.

## Files
| Ext | What | Format |
|---|---|---|
| `.ecigtheme` | Theme | Zip containing `ECigTheme.xml` (see `04`) |
| `.ecigprofile` | One profile | Zip containing `ECigProfile.xml` |
| `.ecig` | Full device config (theme + profiles + materials + settings) | Zip containing `DEScribe.xml` |
| `.csv` | Material curve | See `02` |

### `.ecigprofile` (`ECigProfile.xml`, UTF-8 with BOM)
```xml
<?xml version="1.0" encoding="utf-8"?><ECigProfile>
 <Screen Name="DTv5XL" /><Power Watts="36" /><Temperature Fahrenheit="420" />
 <SessionMode Time="60" />
 <Atomizer MaterialName="DTv5XL" TemperatureProfile="<base64 of 'F,R\r\n-100,…\r\n68,1\r\n…'>">
   <ColdResistance2 Ohms="0.43" Fahrenheit="70.78" />   <!-- optional -->
 </Atomizer></ECigProfile>
```
- TemperatureProfile = base64 of the CSV points with header `F,R` and CRLF line endings.
- Wattage-only profile: omit Temperature, use `<Atomizer MaterialName="Watts" />`.
- Loading a profile does **not** lock ohms. Measure and lock the cold resistance afterward.

### `.ecig` (`DEScribe.xml`)
`<DESabertooth Device="109" …>` with many `<Feature Name="…" Index="n">value</Feature>` entries. Text values are base64, and some are XML-escaped plain text. Theme parts live here too: EvolvFont (XML-escaped font XML), EvolvUIDesign, EvolvWallpaper (PNG), EvolvThemeTitle/Author, EvolvColorScheme, EvolvLEDTrack, EvolvBatteryDischargeCurve, EvolvCVMaterialTemperatureProfile.
- **Default Evolv theme fonts were extracted from the default `.ecig`:** "Built SemiBold" at sizes 18 (Normal), 24 (Big), and 13 (Small), with `<Metrics Ascender/Descender>`. Gremlin uses these exact bitmaps.

## Reference setups (as published)
**Gremlin - Color Themes v2.2** (`../release/gremlin_v2.2.03.ecig`, also as single profiles in `../release/profiles/`):
- Slot 1 **DTv5XL** (material DTv5XL/TCR 200, 36W, 380°F, session 60s)
- Slot 2 **QuestCup** (material QuestCup/TCR 120, 25W, 380°F)
- Slot 3 **DTv5XL-Clean** (Watts, 38W, 120s), slot 4 **QuestCup-Clean** (Watts, 35W, 45s)
- Slots 5–8 hidden. Cold resistance 0 and unlocked on all slots. Battery soft cutoff 3.0V. Color theme switches off (Classic).

**Gremlin High Contrast v1.2** (`../high-contrast/files/gremlin_high_contrast_v1.2.03.ecig`):
- Same settings with short names **XL / QUEST / XL CLEAN / Q CLEAN**, both vaping profiles at 380°F, and **auto-lock off** (`EvolvXAutoLock=0`).

Notes:
- Materials needed on the device: **DTv5XL, QuestCup, Watts**. Others can be removed if no profile uses them.
- **User Toggles (the color theme switches) are not stored in `.ecig` files.** They are on-device state; a mod that has never set them starts with all off.
- `EvolvXPassword=FFFFF` and `EvolvPowerLockPassword=SSS` are **Evolv factory defaults** (they match Evolv's default config), not personal codes. Default unlock: press fire 5 times.
- A DNA "Temp Protect" error usually means a wattage material is on a TC profile (or vice versa).
- How to sanitize an export before publishing: `12-release-and-privacy-checklist.md`.
