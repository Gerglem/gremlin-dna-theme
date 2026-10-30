# 02 – Temperature Control and Calibration

## How TCR temperature control works (short)
The mod compares the heater's **live resistance** to its **locked cold resistance**. TCR (α) tells it how much resistance rises per degree. A higher TCR means the mod thinks it's cooler for a given resistance, so it heats more, and the real temperature runs hotter.
- **Swab too dark → lower TCR. Swab white → raise TCR.**
- Always lock the cold resistance with the heater **at room temperature**.

## Swab (cotton) test, the calibration method used throughout
1. Set the temperature to **470°F**. Light gold on a swab ≈ 470°F. Cotton ignites around 750°F.
2. Fire until the displayed temperature stops rising, then touch the swab to the cup floor for about **10s** while firing.
3. **Light gold** = calibrated. White = raise TCR. Brown or black = lower TCR.
4. Changing the TCR means generating a new material curve, re-importing it, re-locking the cold ohms, and swabbing again. Move in small steps — on the Pico the Lightning cup took 110 → 100 → 95, and on the DNA the Quest took 125 → 120.

**Working temperature: start low and climb.** Once the TCR is calibrated, set the temperature at the low end (~380°F) and work up a few degrees at a time rather than starting high. Vapor appears well below 350°F, so a low start is still usable and it avoids scorching the load. Sustained heat above ~500°F is a primary cup-wear driver.

## Heater settings
| Heater | TCR | Power | Notes |
|---|---|---|---|
| **DT V5 XL cup** | **200** (Divine Tribe published; 180 for the standard V5, 200 for the XL) | 36–37W (DT: 36W to reach 500°F; 27–37W pulsing) | **Swab at 470°F on the DNA was light gold at TCR 200.** Stay below 38W and 500°F; preheat, boost and punch off; Replay off with TC. |
| **DT Lightning Quest (LQ)** | **120** (swab-verified on this DNA100C; Divine Tribe publishes 125, reported values range 105–135 at 28W) | 25W | **Swab at 470°F: tan at TCR 125, light gold at 120.** One step. For comparison, a Pico Plus needed **TCR 95** (110 → medium brown, 100 → tan, 95 → light gold), which does **not** carry over to the DNA. |
| Original (SiC) Quest crucible | ~345 | ~30–48W | Reference only |

Reference V5 XL profile: **36W, set temperature 380°F** (380–420°F is a usable range; vapor appears even at 380°F because terpenes and THC volatilize below 350°F), **session 60s** (Divine Tribe guidance). Reference Lightning Quest profile: **25W, set temperature 380°F, session 60s**. Both vaping profiles ship at the bottom of the range so the user ramps up rather than down.

**No temperature ramp feature:** the DNA can't do a scheduled 380→420°F ramp, and a theme can't run timers. The workaround of using up/down steps was explored, but the step-size toggles (fields 10 and 266) seemed to do nothing and were removed from the theme.

## Cleaning (wattage mode)
| Heater | Setting | Source |
|---|---|---|
| V5 XL | **38W, cup upside down, 2 min**, then cool completely | Divine Tribe product page |
| V5 (alternative) | 35W, 20–30s intervals until R ≈ 0.90Ω | community guidance |
| **Lightning Quest** | **35W, up to 45s per cycle, stop if R ≈ 0.60Ω**, cool fully, repeat if needed | community guidance (side-heated cups) |
| Lightning **Pen** mini cup (different heater!) | max power, three 15s intervals with cooling | Divine Tribe copy |

Careful: the **Lightning Quest** and the **Lightning Pen** use different cups.

Profiles made: **DTv5XL-Clean** (38W, session 120s) and **QuestCup-Clean** (35W, session 45s), both using material **Watts**.

## Material CSVs (DNA)
The format is a header plus `°F,relative resistance` points, linear α in °F terms: `R = 1 + α·(T−68)·5/9`.
- `dtv5xl-tcr200.csv` (TCR 200, generated with the formula below):
  ```
  "Temperature (degF)","Electrical Resistivity"
  -100,0.813333333333333
  68,1
  200,1.002
  219.8738170347,1.16874868559411
  800,1.81333333333333
  ```
- `questcup-tcr120.csv` (generated with the same display fix):
  ```
  "Temperature (degF)","Electrical Resistivity"
  -100,0.888
  68,1.0
  200,1.002
  219.8738170347,1.1012492113564667
  800,1.488
  ```
- **Display fix:** the curve is flattened to 1.002 at 200°F and rejoins the linear line around 220°F. This makes the live-temperature readout work on DNA boards. Above 220°F it's identical to linear, so vaping temperatures aren't affected.
- To generate a new TCR `t`: α=t/100000; points (-100,R(-100)), (68,1), (200,1.002), (219.8738170347,R(219.87)), (800,R(800)).

## Cup health
## The curve, verified against the hardware (2026-10-30)

Two puffs captured off the serial stream at 64 Hz (`17`), 762 live samples, and the temperature the
**firmware reports matches our own material curve interpolated by hand to within 0.04 F**, mean error
0.012 F. Sample data: `../tools/samples/puff-dtv5xl-36w.csv`.

That verifies several things this project had only ever assumed:

- **The CSV curve is what the chip actually uses.** Feed `R=GET COLD` and the curve's breakpoints into
  a linear interpolation and you reproduce the device's own temperature reading almost exactly.
- **The 200-220 F display fix behaves as designed.** The flattened segment and the steep one above it
  were both exercised in one puff - the cup crossed 219.84 F - and the readings track the curve
  through the break with no discontinuity.
- **Cold resistance is the reference the whole thing hangs on.** The match only holds using the full
  precision value, 0.4637451171875; rounding to 0.464 shifts the computed temperature by about 0.6 F.

### What a V5 XL puff actually looks like at 36 W

| | |
|---|---|
| Duration | 7.34 s |
| Resistance | 0.471 -> 0.566 ohm |
| Temperature | 202 -> 267 F, **setpoint 385 F never reached** |
| Heating rate | ~8.9 F/s |
| Power | 35.98 W mean against a 36 W setpoint, range 34.8-36.2 |
| Current | 8.50 -> 7.97 A, falling as resistance rises |
| Battery | 3.98 -> 3.90 V under load, from 4.16 V idle |

**The power never throttled**, which means temperature protection never engaged - in seven seconds,
from an already-warm 202 F, the cup only reached 267 F. Extrapolating the observed rate, reaching 385 F
from room temperature would take on the order of twenty seconds at 36 W.

That reframes the reference settings below. The XL is a large thermal mass and 36 W is a gentle heat
for it; the 60 s session is not generous, it is roughly what the cup needs. It also explains why the
starting temperature matters less than expected on this cup - much of a short session is spent on the
way up rather than at the limit.

- A failing cup shows up as **cold resistance drifting upward**. One V5 XL cup went from 0.43 → 0.61Ω within two weeks and had to be replaced; the base was fine.
- **Measured cold resistance on this mod** (from locked configs, same meter, same method): **V5 XL 0.4637Ω**, **Lightning Quest 0.3141Ω**. Device Monitor read the same XL cup at **0.460Ω** on 2026-10-30, so the figure is stable across measurements and tools. These are the baselines the replace warning is derived from.
- **Replace thresholds (2026-10-30):** **V5 XL above 0.60Ω**, **Lightning Quest above 0.41Ω**. Both are the same proportional rise, **×1.294**, over the measured baseline above — 0.6 ÷ 0.4637 for the XL, and 0.3141 × 1.294 = 0.4064 rounded to 0.41 for the Quest. The one failure on record rose ×1.419 (0.43 → 0.61), so the warning fires before that. Both themes color the resistance **red** past the threshold (`06`, `11`), built as layered flat variants rather than a nested AND, which does not work on this hardware (`07` #24). **Caveat: one failure data point.** If used-but-healthy cups turn out to sit near the line, raise it.
- Wear drivers: sustained heat (>~500°F), thermal shock, frequent burn-offs.
- Fresh V5 XL cup: DT spec 0.44–0.49Ω — the measured 0.4637Ω above sits mid-spec. No published spec for the Lightning Quest; 0.3141Ω is the only measurement here. Live idle readings slightly above the locked value right after firing are normal (still warm).
- Multimeters give inconsistent sub-ohm readings (and the 2000k range reads 0). Mod readings are more reliable.

## Terp pearls
4mm quartz or ceramic, 2–3 in the Lightning Quest cup, single layer covering ≤ half the floor (general guidance; no official DT number found).

## IR thermometers
Not useful here (spot size, emissivity, access). A K-type thermocouple with a fine bead is better, but the swab test is sufficient.
