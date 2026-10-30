# 01 – Hardware and Chip Swap

## Background
- Goal: a slim box mod with true custom TCR for Divine Tribe heaters (V5 XL, TCR 200; Lightning Quest, TCR 120 after calibration — Divine Tribe publishes 125), with an autofire/session feature like the Divine Tribe Pico Plus firmware.
- The stock **Lost Vape Thelema Solo (Quest 2.0 chip)** has **no custom TCR**, only preset materials (Ti, Ni, SS316, SS904). Lost Vape marketing calls them "TCR modes," which is misleading.
  - Calibration attempts on the V5 XL in **Ti mode at 37W**: displayed 300°F → black swab; 250°F → medium brown; 225°F → light tan (≈ true 470°F); 200°F → faint off-white but scorched quickly. That's roughly **2.6 true °F per displayed °F**. Unusable as real TC. SS904 is the closest preset but was never validated.
  - The Quest USB port is charge/update only. **Arctic Fox (NFE)** has unofficial Quest support, but it needs a modified USB cable, IC pin jumping, and on some boards about 50 solder-point processor replacements. Not pursued.
- **Decision:** replace the Quest board with an **Evolv DNA100C** ($74.99 list from evolvapor.com; shipped in about a week). Lost Vape sells a factory Thelema Solo DNA100C in the same shell, which suggested a good fit. The board fit with **no frame modification**.
- Alternative mods researched (for reference): Khonsu SBS+ DNA60C ($94.50, 83×50×26, 21700, 26mm atty); Early Bird Harrier DNA60C ($169.99); Rekavape Penon 3 DNA60C ($119.99); Pipeline Box DNA60C (€184.95); LVE Therion 2 DNA250C (2×18650); Dovpo Odin DNA250C ($180); Boxer Classic DNA250C ($274.95). Geekvape Z100C DNA was ruled out (magnetic pod, no reliable 510 adapter; adapters corrupt TC readings).

## DNA100C (as installed)
- 160×80 color TFT on a ribbon cable, onboard actuators (fire, up, select, down), USB-C, 1–100W.
- Charging defaults to 3A, adjustable in EScribe.
- Supports Replay, preheat/boost, ohm lock, and **Session Mode (needs international firmware)**.
- Physical buttons on the Thelema: **fire at top**, a three-button row below the screen = **up / select / down**. Mapping worked with no theme changes.

## Parts and tools
- DNA100C (Evolv direct), Molicel **P42A** 21700 (fine; ~4200mAh, ~30A).
- **63/37 leaded rosin-core solder** and flux. Leaded is fine: the joints are inside the case, away from the vapor path.
- **Pinecil** (fine conical tip only; runs from a 65W+ USB-C laptop charger with a 100W/5A cable) and a **Q-MING 80W kit** with a **chisel tip** for the heavy pads.
  - AliExpress TS100/Pinecil-compatible tips (~$3): **BC2** (buy two), D24 chisel, optional C4/K. Tips last years if kept tinned, cleaned with brass wool, and run at the lowest workable temperature. Never file a tip.
- 20 AWG silicone wire was planned (18 AWG acceptable). 16 AWG is oversized: at 37W the draw is about 11–12A. **The factory wires were reused,** which were short with only a few mm of exposed copper. That worked.
- Multimeter, precision drivers, tweezers, spudger, Kapton tape.

## Procedure as performed
Photos: `../images/`.
1. Remove the battery. **The "THELEMA SOLO" side panel and its screws are decorative — the panel does not come off, and nothing is accessed through it.** The screws that actually free the sled are **inside the battery compartment** and **on the bottom of the mod**. Unscrew those, free the 510 assembly, slide the sled out (short wires).
2. Label **B+, B−, 510+, 510−**. Verify polarity with a meter; don't trust colors alone. In the install photos, a **white wire went to B+**; black was the other battery lead.
3. Desolder, remove the Quest board and screen.
4. **Solder the DNA100C** in this order: 510− → 510+ → B− → B+.
   - At **350°C** the chisel tip did **not** melt the joints. **380°C** with flux and a tinned tip did. Keep each touch under 5s; 400°C is the ceiling.
   - The wire must **lie flat on the pad**. Solder shouldn't bridge a gap, since high-resistance joints hurt TC readings.
   - Trick: blob on the pad, wire taped down, iron presses the wire into the blob.
5. **Screen ribbon:** the DNA100C connector **did not have a movable latch** (it neither flipped nor slid). Push-in: stiffener up, contacts down, inserted from the left, straight and even. A YouTube Boxer DNA100C install video showed the same left-side entry.
6. **Bezel:** the original Quest screen bezel/lens was **sanded down** to fill the window around the DNA screen. Options discussed for securing it:
   - Thin phone-repair tape (**tesa 61395** black or **3M 300LSE** clear, 1–2mm, one continuous loop). Semi-permanent; heat releases it.
   - **B-7000 / E6000** on the outer rim only. Seals better. Wet E6000 contains tetrachloroethylene, so ventilate, wear gloves, and cure 24–48h. E6000 Plus is reportedly lower-odor.
   - Avoid super glue (fogging; use low-bloom like Loctite 460 if forced), Elmer's/Weldbond PVA (weak on smooth plastic, water-based), and acetoxy RTV (acetic acid corrodes). Neutral-cure RTV is OK.
7. **Pre-power checks:** B+↔B− and 510 center↔body must NOT have continuity. Case open, battery in with no atty, watch for smoke or heat. Then EScribe, atty resistance check, 10W fire, heat check, normal wattage, close up.

## First-boot findings
- Buttons worked as up/select/down.
- An audible **click from the atomizer on every fire press** is the current inrush (~11A at 36W) moving the heater and contacts slightly. It's normal. Watch for jumpy live resistance, burning smell, or inconsistent heat (none seen in this build).
- With no atomizer attached, pressing fire still enters the session state (no power flows). The chip status reads "No Atomizer."

## Battery settings (EScribe → Mod → Battery)
- Type: Lithium Ion 18650 (grayed out; same chemistry; only affects the % estimate).
- **Cell Soft Cutoff:** recommended **3.0V** (default 2.75V; the P42A is rated to 2.5V).
- Max USB Charge Rate: 3.0A is within spec. 1.5–2A recommended for cell longevity.
- Mod → Safety: **Ohm Lock Range ±25%**, Replay "Restrict to viable coils" (defaults, fine).

## Misc
- Flying with spare lithium cells: carry-on only, in a case.
- PACT Act limits shipping vapes, so sell used mods locally or via forum classifieds.
