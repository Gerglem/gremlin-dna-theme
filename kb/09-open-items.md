# 09 – Open Items

## Firmware limitations (not fixable in a theme)
- No "at temperature" indicator: Heating Time Done (353173506) is rejected by the DNA100C firmware.
- No live session countdown: Puff Time can't be displayed (Theme Designer crashes when it's set as a Field source).
- The chip can't report atomizer presence before the first fire; the themes rely on the chip's own "No Atomizer" status.
- Firing with no atomizer still enters the session state (no power flows).
- Full-screen pictures don't draw while firing; pure black picture pixels are transparent (`07`).

## Untested
- New-coil screen **OLD** value (field 1048835). It only appears with ohm lock off.
- Whether every chip warning (e.g., "Temp Protected") appears in the status line.

## Ideas
- **More color themes:** off-board memory is the limit (93.6% on the DNA75C). Free image space first, e.g. let more themes use the standard gremlin.
- **Full menu coloring** for one or two themes would fit in on-board memory (56%).
- An "at temperature" indicator via a math condition comparing live vs set temperature.
- Larger temperature in the High Contrast theme would need a bigger custom font and layout rework (`11`).
