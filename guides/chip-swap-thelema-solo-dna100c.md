# Chip swap guide: Evolv DNA100C in a Lost Vape Thelema Solo

**TL;DR:** The Thelema Solo's Quest 2.0 chip has no custom TCR, so Divine Tribe cups can't be dialed in properly. I replaced the board with an Evolv DNA100C (about $75 direct from Evolv). It fits the stock shell, uses the stock buttons, and gives you true TCR, Session Mode (DNA's autofire), and a fully custom screen. Total cost was roughly the price of the mod + $75 + solder. Moderate soldering skill required: 4 joints.

---

## Why do this?

Divine Tribe heaters want a specific TCR value: **200 for the V5 XL cups** and **125 for the Lightning Quest**. The Thelema Solo's stock Quest 2.0 chip only offers preset materials (Ti, Ni, SS316, SS904). There's no custom TCR field, even though some of Lost Vape's marketing calls them "TCR modes." I tried calibrating with the presets using swab tests. You can get close, but the displayed temperature is meaningless and it scorches easily.

The DNA100C gives you:
- **Custom TCR**, loaded as a material curve, so the screen temperature matches the real cup temperature
- **Session Mode:** one click starts a timed heat-up session, one click stops it (international firmware)
- **Replay, preheat, and resistance lock**, plus a fully custom screen via Evolv's Theme Designer
- Proper low-voltage protection and USB-C charging

Lost Vape also sells a factory **Thelema Solo DNA100C** in the same shell, which is a strong hint the board fits. Mine did, with no modification to the frame.

---

## What I bought

| Item | Where | Notes |
|---|---|---|
| Lost Vape Thelema Solo (Quest 2.0) | [Element Vape](https://www.elementvape.com/lost-vape-thelema-solo) | Sold as a starter kit, but you only need the mod. If you're buying new, consider the factory DNA100C version instead. |
| **Evolv DNA100C** board | [evolvapor.com](https://www.evolvapor.com/products/evolv-dna-100-color) | **$74.99** list. Shipped in about a week. Includes the 160×80 color screen on a ribbon, onboard buttons, and USB-C. |
| Molicel P42A 21700 | Battery vendor of choice | Any quality 21700, or an 18650 with the included sleeve |
| 63/37 leaded rosin-core solder | Amazon/hardware store | Leaded flows much easier on the heavy battery pads |
| Flux pen | Amazon | Helps a lot |
| Kapton tape | Amazon | Insulating and holding wires |

**Tools:**
- **Soldering iron:** I used a Pinecil (runs off a 65W+ USB-C laptop charger) plus a Q-MING 80W kit for its **chisel tip**. You want a chisel or bevel tip with real thermal mass for the battery pads. A fine conical tip will struggle.
- Precision screwdriver set, tweezers, a plastic spudger
- **Multimeter**, for continuity checks before first power-up
- Optional: helping hands or a silicone soldering mat

---

## Before you start

- **Don't install the battery** until the continuity checks pass.
- You're working with a lithium-ion power circuit. A reversed battery connection can destroy the board. Label every wire before you cut or desolder anything.
- This voids any warranty. You do this at your own risk.

---

## Step 1: Disassembly

1. **Remove the battery.**

   **Don't try to pull the side panel off.** The "THELEMA SOLO" panel and the screws on it are decorative — it is not an access cover and it does not come off. Prying at it just marks up the finish.

   ![The side panel — decorative, it does not come off](../images/01-thelema-solo-side-panel.jpg)
   ![Battery bay — real screws live in here](../images/02-battery-bay.jpg)

2. **Remove the real screws.** They're in two places: **inside the battery compartment** (take the battery out first so you can see and reach them) and **on the bottom of the mod**. With those out, work the **510 assembly** loose. It stays wired to the board.

   ![510 assembly](../images/03-510-assembly.jpg)

3. **Slide the sled out.** Go slowly, because the wires to the 510 and the battery contacts are short.

   ![Removing the sled](../images/07-removing-sled.jpg)
   ![Sled out](../images/06-sled-removed.jpg)
   ![Quest board in sled](../images/04-quest-board-in-sled.jpg)

4. **Note the four connections:** **B+, B−** (battery) and **510+, 510−** (atomizer). Photograph them and **label each wire with tape.** Don't trust wire colors alone. Verify polarity with a multimeter before desoldering.

   ![Wire pads on the Quest board](../images/08-quest-board-wire-pads.jpg)
   ![Back of Quest board](../images/09-quest-board-back.jpg)

5. **Desolder the four wires** and remove the Quest board and its screen.

   ![Screen module](../images/05-screen-module.jpg)
   ![Empty frame](../images/10-empty-frame.jpg)

---

## Step 2: Solder in the DNA100C

![Parts and tools](../images/11-parts-and-tools.jpg)

**Iron settings that worked for me (63/37 leaded):**
- **350°C** to start with the chisel tip. **380°C** if the solder won't flow within a few seconds.
- Keep each touch **under about 5 seconds**.
- Add a dab of flux and melt a little fresh solder onto the tip first. Heat transfers through solder, not through a dry tip.

**Joint technique:**
1. Wick or wipe old solder blobs off the wire ends, then **re-tin each wire**: flux, then melt solder *into* the strands.
2. Pre-tin the board pad with a small blob.
3. **Lay the wire flat across the pad.** It should be touching the pad, not floating above it. Solder bridging a gap makes a weak, high-resistance joint, which messes up temperature control readings.
4. Heat the wire into the blob and let it sink in. Hold the wire down with tape or helping hands so you aren't juggling three things.
5. Look for a smooth, shiny joint that fully wraps the wire.

**Order:** 510− → 510+ → B− → B+.

The factory wires are short, with only a few millimeters of exposed copper. That's fine. Just lay what's there flat on the pad. If you have slack, strip another 1–2mm to make it easier.

![DNA100C wiring](../images/13-dna100c-wiring.jpg)

---

## Step 3: Connect the screen

The DNA100C's screen connects to the board with a ribbon cable into a small connector.

![Screen ribbon](../images/14-screen-ribbon.jpg)
![DNA board in frame](../images/15-dna100c-installed.jpg)
![ZIF connector](../images/16-zif-connector.jpg)

On mine, the connector had **no latch that would move**. It was a push-in style. Hold the ribbon by its black stiffener tip, **gold contacts facing down** toward the pins and the stiffener up, and slide it in from the side **straight and evenly** until it stops. Don't force it. If it won't go in with light pressure, it's crooked.

(If yours does have a flip-up or slide latch, open it gently with a fingernail first.)

---

## Step 4: The screen window

The DNA screen sits differently behind the Thelema's window than the Quest screen did. I **sanded down the original screen bezel/lens** from the Quest screen until it filled the gap cleanly, and it looks factory.

![Sanded bezel](../images/17-sanded-bezel.jpg)

**Securing it:**
- **Best:** thin double-sided phone-repair tape in 1–2mm width, like **tesa 61395** or **3M 300LSE**, laid as one continuous loop. It's semi-permanent: a hair dryer and gentle prying release it.
- **Also good:** a thin bead of **B-7000** or **E6000** on the outer rim only. Use it in a ventilated area, since wet E6000 fumes are nasty. Let it cure 24–48 hours away from the board.
- **Avoid super glue.** Its fumes fog the inside of clear lenses.
- **Avoid regular "acetoxy" RTV silicone** (the vinegar-smelling kind). It can corrode electronics.

---

## Step 5: Before the first power-up

With **no battery** installed, use the multimeter on continuity:
- **B+ to B−:** must **NOT** beep.
- **510 center pin to 510 body:** must **NOT** beep.
- Look over the board for solder blobs or stray strands.

Then:
1. Leave the case open so you can see the board.
2. Insert the battery, **with no atomizer**. The screen should light up. If you see smoke or smell anything, or anything gets hot, pull the battery immediately.
3. Connect USB-C and open **EScribe** (Windows or Mac), Evolv's free configuration software: <https://www.evolvapor.com/escribe>. The board should be detected.
4. Attach your atomizer and confirm the resistance reads correctly (my V5 XL cup reads about 0.43–0.46Ω).
5. Test fire at 10W, check for heat in the wires and joints, then go up to your normal wattage.
6. Close it up.

---

## Step 6: Firmware and battery settings (important)

- **Session Mode requires Evolv's international firmware.** In EScribe (<https://www.evolvapor.com/escribe>), accept the prompt to update to the **international edition (SP55.1 INT)**. **Pick international, not US** — the US edition won't show Session Mode, and the Gremlin theme won't upload without it.
- **Mod tab → Battery:**
  - **Cell Soft Cutoff:** I raised it from 2.75V to **3.0V** to be easier on the cell.
  - **Max USB Charge Rate:** 3A is within spec for a P42A. **1.5–2A** is gentler on the battery if you're not in a hurry.

The four buttons map naturally: **fire on top**, and the three-button row as **up / select / down**.

---

## Results

Everything works: true TCR, Session Mode, resistance lock, and a custom screen. My V5 XL cups heat noticeably more evenly than they did on my Pico, because the DNA holds temperature instead of overshooting.

The profiles, materials, and the custom theme I built for this mod are in the companion guide: **[Gremlin theme and Divine Tribe profiles](setup-gremlin-theme-profiles-calibration.md)**.

Full docs, photos, and files: https://github.com/Gerglem/gremlin-dna-theme

Questions or problems? Open an issue on this repository.
