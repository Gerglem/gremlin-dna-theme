# 05 – DNA Field ID Dictionary

Field IDs were mapped with Theme Designer: add a labeled condition for each measurement, save, and read the resulting `Field=` value back out of the XML (see the bottom of this file).
Confidence: **C** = confirmed (labeled test or on-device), **H** = high (consistent across labeled test files), **M** = medium (inferred).

**Pattern:** the low 16 bits look like the category (0x0002 profile/atomizer, 0x0007 device settings, 0x0001 battery/USB, 0x0006 system/general, 0x0208 stats, 0x000A step settings) and the high bits are the index.

## Atomizer / profile
| ID | Hex | Meaning | Conf |
|---|---|---|---|
| 16778242 | 0x1000402 | Temperature setpoint. With `UpdateLive` + ReadOnly, shows **live temperature while firing** | C |
| 16843778 | 0x1010402 | Power (watts). "Atomizer → Power" | C |
| 17825794 | 0x1100002 | Cold ohms (locked) | C |
| 1048642 | 0x100042 | Live ohms. **Reads 0 when idle after boot, and 0 during the first session after power-on** | C |
| 131138 | 0x20042 | Atomizer current (A). Also 0 during the first session | C |
| 196674 | 0x30042 | Atomizer voltage | H |
| 18350082 | 0x1180002 | Coil material (selectable) | H |
| 85196802 | 0x5140002 | Ohm (resistance) lock toggle | C |
| **84672514** | 0x50C0002 | **Session Mode → Enable** | C |
| **17498114** | 0x10B0002 | **Session Mode → Time** (editable seconds) | C |
| 17629186 | 0x10D0002 | Atomizer → Heating Time | C (ID); unused |
| 353173506 | 0x150D0002 | Atomizer → Heating Time Done. **Rejected by firmware: upload fails** | C |
| 83886082 | 0x5000002 | Temp-sensing material active (TC mode) / "Temp Protect" | H |
| 85458946 | 0x5180002 | Atomizer → Replay | H |
| 286654466 | 0x11160002 | Enable Replay | H |
| 85327874 | 0x5160002 | Replay playing / can replay now | H |
| 320208898 | 0x13160002 | Replay idle/active | M |
| 17432578 | 0x10A0002 | Replay warmth | H |
| 218103810 | 0xD000002 | Preheat/Boost enable | H |
| 151060482 | 0x9010002 | Preheat power | H |
| 150994946 | 0x9000002 | Preheat temperature | H |
| 151257090 / 151584770 | | Preheat punch | H |
| 151388162 | | Boost punch | H |
| 778 | 0x30A | Preheat by temp vs punch | H |
| 419889154 / 419954690 | | Can boost / can preheat | M |
| 1048579 | 0x100003 | New coil → cold ohms. **Blank outside the new-coil screen** | C |
| 1048835 | 0x100103 | Old coil cold ohms | M (unverified) |

## General / UI
| ID | Meaning | Conf |
|---|---|---|
| **17825798** | **General → Firing (UI)**: true during a session/fire | C |
| 0 | What Theme Designer saved for General → Firing → **Puff Time**. **Invalid** (shows blank); setting it as a Field source crashes Theme Designer | C |
| 1048582 | General → Theme → Status Displayed. True at boot and for about 1s after firing, **even with empty text** | C |
| 262151 | Selected profile (editable: switches profile) | C |

## Display / device settings
| ID | Meaning | Conf |
|---|---|---|
| 7 | Brightness (1–10) | C |
| 65543 | Stealth mode (toggle) | C |
| 589831 | Stealth level | H |
| 131079 | Temperature unit °F/°C | C |
| 327687 | Flip screen | H |
| 720903 | Keep screen on | H |
| 10 | Watt step toggle. **Did nothing visible**, so removed | C |
| 266 | Temp step toggle. **Did nothing visible**, so removed | C |
| 393223 | Auto lock | H |
| 458759 | Auto lock time | H |
| 524295 | Clicks to lock | H |
| 655367 | Max puff time | H |
| 65551 | Time | H |
| 15 | Date | H |
| 196615 | 12/24 hour | H |

## Battery / USB / power bank
| ID | Meaning | Conf |
|---|---|---|
| 65537 | Battery level (%). Used by meters | C |
| 1 | Pack voltage | C |
| 131073 | Charging state (used in conditions) | M |
| 262145 | Charge current | H |
| 1048833 / 1049089 / 1049345 / 1049601 | Cell 1–4 voltage | H |
| 1179649 | Cell count | H |
| 917511 / 851975 | Power bank enable / auto on | H |
| 196609, 458753, 589825, 720897 | USB connected, PC data, …, discharging | M |

## Misc / stats
| ID | Meaning | Conf |
|---|---|---|
| 6 | Board temperature | H |
| 65542 | Room temperature | H |
| 2097158 / 2162694 / 2228230 / 4194310 | Serial / firmware / service pack / edition | H |
| 16777736 | Puff count | H |
| 16908808 | Total energy | M |
| 100991496 / 100925960 / 100860424 / 101057032 / 100794888 | Last puff time / avg power / power / peak / energy | H |
| 1048584 | Reset count | M |

## Full measurement list (names only, from Theme Designer)
General: Firing (Button), Firing → Puff Time, Firing (UI), Atomizer/Profile, Theme → Highlighted, Theme → Status Displayed, Has Unsaved Changes. Display: Brightness, °F/°C, Flip, Power Lock (+Capable), Stealth, Clock (Year/Month/Day/Hour/Minute/Second, 12/24), Lock (Auto, Auto Time, Clicks). Atomizer: Power, Temperature, Replay (+Warmth), Temp Protect, Temp Sensing Detect, Temp Sensing Material, Heating Time, Heating Time Done, Preheat/Boost Enable/Punch, Preheat Enable/Power/Punch/Temperature, Boost Enable/Punch, Session Mode Enable/Time, Coil Cold Ohms (+70°F), Ohm Lock, Can Boost/Preheat/Replay/Replay Now, New Coil / Old Coil Cold Ohms. Statistics: Last Puff, Since Reset, Total (energy/time/count), Reset Count. Recordings: Puff, Settings, Chart Present. Research → Sealed. Battery: Current, Voltage, Cell 1–4, Cell Count, Level, Charge, Charging, Discharging. Misc: Board/Room Temp, Atomizer Current/Voltage/Live Ohms, Debug (uptime, random), Firmware Edition US-only, USB (connected, PC, power bank, current, voltage, power). User → Toggle 1–9.

**To get the ID of any field:** in Theme Designer, add a Label, use Add Condition → measurement → field, set that tab's Text to the field name, save, and read the Compare `Field=` next to each Text in the XML.
