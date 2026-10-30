# 09 – Known Limitations and Untested Items

## Firmware limitations (not fixable in a theme)
- No "at temperature" indicator: Heating Time Done (353173506) is rejected by the DNA100C firmware.
- No live session countdown: Puff Time can't be displayed (Theme Designer crashes when it's set as a Field source).
- The chip can't report atomizer presence before the first fire, so the theme relies on the chip's own "No Atomizer" status.
- Firing with no atomizer still enters the session state (no power flows).

## Untested
- **Lightning Quest swab calibration on a DNA board.** Start at TCR 125.
- New-coil screen **OLD** value (field 1048835). It only appears with ohm lock off.
- Wattage-mode profiles: the main-screen temperature readout may show blank or "Off."
- Whether other chip warnings (e.g., "Battery Low," "Temp Protected") appear in the Status line.

## Possible improvements
- An "at temperature" indicator via a math condition comparing live vs set temperature.
- Warnings on the lock screen beyond the existing Status line.
- Adding indicator-LED color sequences (both themes ship with none; irrelevant if the mod has no LED).
- More color themes: off-board memory is at 93.6% on the DNA75C. Free image space first (e.g., use the standard gremlin for more themes).
- Full menu coloring for one or two themes would fit in on-board memory (56%).
