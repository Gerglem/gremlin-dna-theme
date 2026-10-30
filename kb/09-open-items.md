# 09 – Open Items

## Firmware limitations (not fixable in a theme)
- No "at temperature" indicator: Heating Time Done (353173506) is rejected by the DNA100C firmware.
- No live session countdown: Puff Time can't be displayed (Theme Designer crashes when it's set as a Field source).
- The chip can't report atomizer presence before the first fire; the themes rely on the chip's own "No Atomizer" status.
- Firing with no atomizer still enters the session state (no power flows).
- Full-screen pictures don't draw while firing; pure black picture pixels are transparent (`07`).

## Untested
- New-coil screen **OLD** value (field 1048835). It only appears with ohm lock off.
- ~~**Ohm-lock toggle on the new-coil screen.**~~ **Confirmed on a DNA100C 2026-10-30 (Color Themes):** toggling the lock while the NEW COIL? prompt is up latches the **new** reading, and `NewCoilAccept` does not dismiss the screen before the toggle can be reached. High Contrast prompted correctly but could not be confirmed at the time — it had no resistance readout, which is what the OHMS screen below now adds. **Then found the same day:** locking on the prompt can leave **0** locked — not because of the order of the presses, but because the lock is a flag and the configs ship cold ohms at 0 until a reading is committed (`07` #22). **Confirmed on High Contrast with the guard in place, 2026-10-30:** LOCK then YES locks the new value.
- **Hidden-until-measured guard on both new-coil lock controls.** default `<Hidden/>` with the real element carrying `<Compare Operator="1" Field="1048579" RefValue="0" />` on an `UpdateLive` control, so the label and padlock only appear once the prompt has a non-zero reading. **Partly confirmed 2026-10-30 (High Contrast):** the prompt appeared with the padlock reachable and the lock worked, so 1048579 does hold a real reading on that screen. Still untested: whether the guard ever actually *hides* the control — it has only been shown not to break the working path — whether the variant re-evaluates after MEASURE, and the same screen on Color Themes.
- **High Contrast Ω / OHMS screen** (v1.2). The menu's ohms row and the child screen behind it have not been exercised on hardware: whether the `Ω` label renders from codepoint 937 at FontStyle 0, whether `ChildScreen Screen="4"` reaches the new screen, and whether `ResampleOhms` works from a child screen (the color theme calls it from PROFILE, so it should).
- **High Contrast screenshots are stale.** `../high-contrast/images/menu-screen.png` and `new-coil-screen.png` predate the ohms row; there is no screenshot of the OHMS screen yet.
- Whether every chip warning (e.g., "Temp Protected") appears in the status line.

## Ideas
- **More color themes:** off-board memory is the limit (93.6% on the DNA75C). Free image space first, e.g. let more themes use the standard gremlin.
- **Full menu coloring** for one or two themes would fit in on-board memory (56%).
- ~~An "at temperature" indicator via a math condition comparing live vs set temperature.~~ **Not possible in a theme (settled 2026-10-30).** Three independent blocks: the setpoint and the live temperature are the *same* field (16778242 — live is that field with `UpdateLive` + `ReadOnly` while firing), so no condition can tell "how hot it is" from "what was asked for"; `<Compare>` only tests a field against a literal `RefValue` baked into the theme, so "live ≥ set" cannot be expressed; and the firmware's own flag, Heating Time Done (353173506), is rejected on upload (`07` #1). A hardcoded threshold is possible but lies as soon as the setpoint moves off it. Unexplored: the chip throttles power once it reaches temperature, so `profile == N` AND `watts < X` might approximate it, at the cost of per-profile constants.
- Larger temperature in the High Contrast theme would need a bigger custom font and layout rework (`11`).
