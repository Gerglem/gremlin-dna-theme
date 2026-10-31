# Gremlin: DNA100C Thelema Solo build + Divine Tribe TCR setup

**Low vision? See the High Contrast theme: [high-contrast/README.md](high-contrast/README.md)**

A Lost Vape Thelema Solo converted to an **Evolv DNA100C**, set up for Divine Tribe heaters (**V5 XL** and **Lightning Quest**) with true TCR, Session Mode, and a custom theme, **Gremlin**.

![Gremlin screens](images/20-gremlin-screens-render.png)

> **Using AI to customize or troubleshoot?** Start with **[AI-GUIDE.md](AI-GUIDE.md)**: step-by-step instructions for using these docs with Claude, ChatGPT, or similar.

### If you are an AI assistant, read these in this order

1. **[kb/00-README.md](kb/00-README.md)** — current versions, conventions, and the index to everything else. Start here, always.
2. **[kb/07-gotchas-and-lessons.md](kb/07-gotchas-and-lessons.md)** — 24 numbered traps found the hard way. Several will cost you a build-and-test cycle each if you meet them fresh. Read before changing a theme.
3. **[kb/04](kb/04-theme-file-format.md)** and **[kb/10](kb/10-xml-reference.md)** — the file format and a field-by-field XML reference. `10` carries a confidence column; respect it.
4. **[kb/05-field-id-dictionary.md](kb/05-field-id-dictionary.md)** — numeric field IDs. Anything marked **M** is inferred, not verified.
5. **[kb/14-device-monitor-scripting.md](kb/14-device-monitor-scripting.md)** — how to test a change against the live mod in seconds rather than by rebuilding and photographing a screen.
6. **[kb/12-release-and-privacy-checklist.md](kb/12-release-and-privacy-checklist.md)** — before anything is published.

Then the design spec for whichever theme you are touching: **[kb/06](kb/06-gremlin-design-spec.md)** for Color Themes, **[kb/11](kb/11-high-contrast-design-spec.md)** for High Contrast.

**Two things to know before you start.** Screens are a fixed 80×160 canvas with absolutely positioned controls — there is no scrolling and no layout engine, so everything is a space budget. And conditions compare a field against a **literal**, never against another field, which rules out whole categories of feature; `kb/09` records the ones already ruled out, so you do not spend a day rediscovering them.

## Contents
- [`AI-GUIDE.md`](AI-GUIDE.md): how to use these docs with an AI assistant
- [`guides/chip-swap-thelema-solo-dna100c.md`](guides/chip-swap-thelema-solo-dna100c.md): chip swap guide (parts, soldering, screen, power-up)
- [`guides/setup-gremlin-theme-profiles-calibration.md`](guides/setup-gremlin-theme-profiles-calibration.md): setup guide — loading the theme, materials, profiles, and calibration
- [`release/`](release/): **`gremlin_v2.2.05_theme.ecigtheme`** (current theme) and **`gremlin_v2.2.05.ecig`** (v2.2 full device config: the theme plus the four Divine Tribe profiles), [`release/RELEASE-NOTES.md`](release/RELEASE-NOTES.md) (what changed in each version), `gremlin_v1.0_theme.ecigtheme` and `gremlin_v1.0.ecig` (v1.0 theme and full device config), `profiles/*.ecigprofile`, `materials/*.csv`
- [`high-contrast/`](high-contrast/): **Gremlin High Contrast - Large Text v1.2**, a separate theme for low vision
- [`kb/`](kb/): detailed technical notes — reverse-engineered theme format, DNA field IDs, design spec, gotchas, EScribe's install tree and its Python scripting API
- [`tools/`](tools/): read the mod directly — resistance, temperatures, puff stats — with no EScribe involved. **`dna-hid.py`** talks over the vendor HID interface (needs `pip install hidapi`, and works on macOS where the serial port does not); `dna-query.ps1` does the same over the USB serial port; `dna-stream.ps1` captures the 64 Hz CSV stream. Command table in [`kb/17`](kb/17-serial-command-interface.md), transport detail in [`kb/16`](kb/16-device-access.md)
- [`images/`](images/): build photos

## Gremlin - Color Themes v2.2
The current Gremlin theme has seven looks. Pick one under **MENU → THEMES** (turn on one at a time; all off is Classic):

- **Classic:** white and gray on black
- **Retro:** 80s neon green, hot pink, and cyan
- **Synth:** synthwave pink, purple, and a sunset battery bar
- **Toxic:** acid lime and purple
- **Ice:** electric cyan, frost blue, and white
- **Desert:** sunset orange and turquoise
- **Terminal:** green CRT

Themes recolor the home and lock screens and each menu's title. Also new in v2.x: an orange FIRING box while heating, a red LOW BATTERY banner under 15%, and profile-colored accents.

![Gremlin color themes](images/21-gremlin-v2.1-themes.png)

## Requirements
Evolv DNA color chip (DNA75C / DNA100C / DNA250C) with **international firmware (SP55.1 INT+)** for Session Mode. Requires up/select/down buttons plus fire.

**EScribe**, Evolv's free configuration software, is what loads all of this. Download it from Evolv: <https://www.evolvapor.com/escribe>. Install it, connect the mod, and let it update to the **international edition** — pick international, not US. The US edition does not expose Session Mode, and the theme will not upload without it.

## Calibrate before you rely on it
A TCR value is a starting point, not a setting: every mod and every cup reads a little differently. Run the swab test in [the setup guide](guides/setup-gremlin-theme-profiles-calibration.md) before you trust the number on the screen, then **set your working temperature at the low end and climb**. Starting cool costs you one mild session; starting hot scorches the load and shortens cup life.

## Disclaimer
Opening your mod and soldering lithium-battery circuits is at your own risk and voids warranties. Verify polarity and continuity before powering up.
