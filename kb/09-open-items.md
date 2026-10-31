# 09 – Open Items

## Where this effort stands

Rewritten 2026-10-30 at the end of a long session. Everything below is current.

### Read this first if you are picking up cold

> **The mod may still be carrying a bench config.** The last thing uploaded to it in this session was
> `BENCH-HC-v06.ecig` (or `-v05`), which **locks fake resistances on all four profiles** - 0.4637,
> 0.4504, 0.6500, 0.3141 - so the replace warning could be exercised. Those do not match the cup in
> the deck. **Reload the real config before using the device.** Do not fire on a bench config.

**Repository is fully pushed.** `main` matches `origin/main`; nothing is held back. The earlier
instruction to keep work local was discharged on 2026-10-30.

**Current builds:** Color Themes **`v2.3.02`**, High Contrast **`v1.2.08`**. **Both proven on hardware**, both carrying Jake's own profile settings. Every control in either build has now been seen working except the new-coil prompt, **which is the one gate left before v2.3 is final**. **Neither has been on hardware.** `v2.3.00` carries the battery split (`18` A); `v1.2.06` carries the home-screen warning.

| | State |
|---|---|
| Replace warning, Color Themes | **Works. Proven on hardware** - `v2.3.02` reads theme / RED / RED / theme, one variant, tint intact |
| Replace warning, High Contrast (OHMS page) | **Works. Proven on hardware** - same four readings |
| Replace warning on the HC home screen | **Works. Proven on hardware** - `v1.2.07` reads dark / RED / RED / dark with the highlight on. `v1.2.06` had the right logic in an invisible color. Old entry: The profile name carries it. **Test registered and bench file built 2026-10-30** - `Downloads\BENCH-HC-HOME-WARNING.ecig`, card below |
| 380F starting temperature | **Confirmed on hardware** |
| Omega OHMS screen (HC) | **Confirmed working** - glyph, child screen, LOCK, MEASURE, BACK all render |
| New-coil screen, both themes | **The least-tested thing in either build.** One item half-confirmed, three open - see the section below |

### The big result: a per-control child limit

The replace warning failed all day and cost three wrong diagnoses. The cause was **not** any operator.
**A control may hold at most 8 children; extras are silently dropped.** The ohms readout had 11 - a
default, six theme colors and four threshold variants - and was the only control in either theme above
8. Its last three were never evaluated, so both cancels and the 0.6 threshold did nothing, and
swapping operator 129 for 4 changed nothing because **those variants were not being read at all**.

Full write-up in `07` #26. The ceiling of 8 is **inferred** from where every other control in the
theme stops, not measured - what is proven is that the chain works at five children.

### Operator facts, corrected

Three earlier beliefs in this repo were wrong. The current, evidence-backed position:

| | Status |
|---|---|
| **Last match wins** | **Confirmed on-device.** Two always-true variants, the second took effect. `04` and `10` were right all along; a mid-session claim of first-match-wins was wrong |
| **Operator 4 = equality** | **Confirmed on-device.** An isolated variant on `profile == 4` fired on exactly profile 4 |
| **Operator 129** | **Untested, not disproved.** It was blamed for the warning failure and that was premature. EScribe does zero the `RefValue` of any `129` compare it round-trips, so prefer 4 |
| **Operator 64 (AND)** / **65 (OR)** | **Both confirmed on-device 2026-10-30**, nesting operators `2` and `4`, on a four-profile truth table - and **64 is now proven in a shipping chain too**, on the `v1.2.07` home screen. The earlier "does not work" verdict was confounded by operator `129` inside every AND ever uploaded. **Nesting depth 2 is proven; depth 3 and 4 are not** |

### Device access: read and control are solved

`tools/dna-hid.py` talks to the board over the **vendor HID interface** - no EScribe, no COM port, no
driver install, just `pip install hidapi` (installed). Framing and traps in `16`; the command table is
`17` and applies to both transports. `tools/dna-query.ps1` does the same over serial, and
`tools/dna-stream.ps1` captures the 64 Hz CSV.

**Writing a config is not solved.** The architecture is mapped as far as reflection can take it
(`16`): the chain is `.ecig root -> GGQ -> DWB.JSL -> PYB -> PYB.UE -> Programmer`, and it is blocked
on obtaining a live `PYB`, because the flash layout is **derived per config** rather than declared per
board. `tools/probe_pyb.py` is inert and ready to run in Device Monitor.

### Device and environment state

- Mod on **COM4**, HID interface `MI_00` present. Serial Output Format is **Plain Text Serial**.
- `hidapi` installed into Python 3.14.
- `gh auth setup-git` has been run, so git push works from the terminal.
- **Claude can now push this repo itself** - a scoped rule in `~/.claude/settings.json` allows
  `git -C "<repo path>" push:*` for this repository only.

### What is genuinely untested

1. ~~**The High Contrast home-screen warning.**~~ **Confirmed 2026-10-30** - `v1.2.07` reads
   dark / RED / RED / dark, with the menu item highlighted. `v1.2.06` is superseded.
1b. ~~**v2.3.00** - the battery split.~~ **Answered 2026-10-30:** child 8 works, the split was
   unnecessary, and the build is withdrawn.
2. ~~**`ResampleOhms` from a child screen.**~~ **Confirmed 2026-10-30** - MEASURE on the HC OHMS page
   re-reads the current value. `Action` works from a child screen.
3. **The new-coil screen on Color Themes** - the hidden `LOCK?` row was only confirmed on High Contrast.
4. Where the child ceiling actually falls. **8 renders and 11 truncates**, both observed; 9 and 10 are unmeasured.

## Tracked: the new-atomizer screen — the least-tested thing in either build

Rewritten 2026-10-30 at the end of the session. The previous version of this section still told you to
load `v2.2.05` and `v1.2.06` and predates everything proven that day, so it is replaced rather than
amended. **Current builds: `v2.3.02` and `v1.2.08`.**

**Nothing in this session exercised this screen.** Every bench run read the home screen or the OHMS
page. Of the four things listed here, one is half-answered and three are open.

| | Item | State |
|---|---|---|
| 1 | `LOCK?` row hidden until there is something to lock | **Half.** Confirmed on High Contrast - a fresh upload at cold ohms 0 showed YES / NO / MEASURE and no `LOCK?` row. **Never checked on Color Themes** |
| 2 | Does the row appear after YES, and does the prompt survive `NewCoilAccept`? | **Open, and this is the one that matters** |
| 3 | High Contrast shows the measured resistance on that screen; MEASURE removed to fit it (`11`) | **Never seen on hardware** |
| 4 | The red replace warning on the prompt | **Never seen**, and it is now a different construction than when this was written |

### v2.3 release gate, set 2026-10-30

**Jake's call: the new-atomizer screen ships working in v2.3.** It is no longer a background tracker -
`v2.3` is not finished until the four items above are confirmed on hardware. The theme work in
`v2.3.02` is done and proven; this is what remains between it and a final release.

Test it with the plain **`gremlin_v2.3.02.ecig`**, not a bench config - the prompt is driven by a
fresh load zeroing cold ohms, and a bench config pre-locks resistances, which suppresses exactly the
condition under test.

### Why item 2 is still open despite an earlier "confirmed"

An earlier entry records that `NewCoilAccept` does **not** dismiss the screen before the toggle can be
reached, confirmed on Color Themes. **That was against the earlier guard**, which watched the *pending*
reading (1048579) and so showed the `LOCK?` row *before* YES was pressed. The guard now watches
**committed cold ohms** (17825794), so the row is hidden until YES commits a reading - which makes the
question "is the prompt still up *after* YES?", and the old observation does not answer it.

If YES dismisses the screen, the row is only ever reachable on a later swap, and a first lock has to
happen from the OHMS page (High Contrast) or PROFILE (Color Themes). Nothing can lock 0 either way, so
this decides documentation and whether the control earns its place, not correctness.

### Correction: the Device Monitor shortcut does not work for the prompt

The previous version suggested writing cold ohms from Device Monitor (`14`) to exercise item 4 without
aging a cup. **That tests the ohms page, not the prompt.** The new-coil prompt compares field
**1048579**, the pending reading, not cold ohms - so writing cold ohms moves a number the prompt does
not read. (`14` separately warns that whether a scripted write reaches a theme field the way a real
measurement does is itself unverified.)

### How to actually test it, no cup swap needed

A fresh `.ecig` load zeroes cold ohms and clears the lock, and that alone produces the prompt on the
next connect - which is exactly how the High Contrast half of item 1 got confirmed. So:

1. Load the build. The prompt should appear with **no `LOCK?` row** (item 1 on Color Themes).
2. Press **YES, NEW**. Does the screen stay up? If it does, does the `LOCK?` row appear now? (item 2)
3. On High Contrast, confirm the measured resistance is on that screen and MEASURE is gone (item 3).
4. For item 4, the reading has to be past the limit *for the selected profile*. Under the single
   variant now shipping, a V5 XL at ~0.46 is **under** its 0.6 limit and will correctly not go red.
   **Select the Quest profile with the XL cup fitted** - 0.46 is past the Quest's 0.41, so the prompt's
   reading should go red. That exercises the warning with no worn cup and no swap.

Step 4 is also the only remaining use of the per-cup rule that has never run on hardware; the same
rule is proven on the home screen and the OHMS page.

## Tracked: programmatic device access

Detail in `16`. Rewritten 2026-10-30 - the previous version of this section listed four next steps
that are all now answered.

### Done: read and control

`tools/dna-hid.py` drives the board over the **vendor HID interface** with no EScribe, no COM port and
no driver install. The framing is `report id 0x01 | magic 0xDE | length | payload`, the payload is the
same plain-text protocol as the serial console (`17`), and it works on macOS where the CDC port does
not. `tools/dna-query.ps1` is the serial equivalent.

### Not done: writing a config

The architecture is mapped as far as reflection goes:

    .ecig root element -> GGQ -> DWB.JSL(?, ggq, null) -> PYB -> PYB.UE(func, int) -> Programmer

- `GGQ` is the board identity and comes straight out of our own files - every `.ecig` opens with
  `<DESabertooth Device="109" Version="1">`, which is the *device code 109.1* in EScribe's debug log.
- **Blocked on obtaining a live `PYB`.** `DWB` is abstract, so it cannot be constructed out of process,
  and EScribe's device layer does not initialize outside its own process.
- **Do not hand-build a `LogicalLayout`.** The flash map is *derived per config* from feature IDs, not
  declared per board (`16`), so inventing offsets is inventing where to write live flash. The
  `dontUpload` dry-run validates the plan it is given, not whether that plan fits the board.

**Next step:** run `tools/probe_pyb.py` (inert) from Device Monitor. It walks EScribe's own
statics for a live `PYB` or `FWB` and dumps `PE()` - the real region sizes, offsets and paging. One
report settles whether this route is viable.

If that fails, the fallback is a **USB capture** of a real upload. Much of the groundwork exists: the
transfer framing is already decoded from a passive capture (`16`,
`tools/samples/hid-upload-capture.log`), and only the PC-to-device direction is missing.

## Firmware limitations (not fixable in a theme)
- No "at temperature" indicator: Heating Time Done (353173506) is rejected by the DNA100C firmware.
- No live session countdown: Puff Time can't be displayed (Theme Designer crashes when it's set as a Field source).
- The chip can't report atomizer presence before the first fire; the themes rely on the chip's own "No Atomizer" status.
- Firing with no atomizer still enters the session state (no power flows).
- Full-screen pictures don't draw while firing; pure black picture pixels are transparent (`07`).

## Untested
- New-coil screen **OLD** value (field 1048835). It only appears with ohm lock off.
- ~~**Ohm-lock toggle on the new-coil screen.**~~ **Confirmed on a DNA100C 2026-10-30 (Color Themes):** toggling the lock while the NEW COIL? prompt is up latches the **new** reading, and `NewCoilAccept` does not dismiss the screen before the toggle can be reached. High Contrast prompted correctly but could not be confirmed at the time — it had no resistance readout, which is what the OHMS screen below now adds. **Then found the same day:** locking on the prompt can leave **0** locked — not because of the order of the presses, but because the lock is a flag and the configs ship cold ohms at 0 until a reading is committed (`07` #22). **Confirmed on High Contrast with the guard in place, 2026-10-30:** LOCK then YES locks the new value.
- **Lock guarded on committed resistance, both new-coil screens.** default `<Hidden/>` with the real element carrying `<Compare Operator="1" Field="17825794" RefValue="0" />` on an `UpdateLive` control, so the label and padlock appear only once cold ohms is non-zero. **Confirmed 2026-10-30 (High Contrast), against the earlier 1048579 guard:** the prompt appeared with the padlock reachable and the lock took the new value, so a guard on that screen does resolve and the Toggle works from the prompt. **The decisive open question for the cold-ohms guard is whether the prompt survives `NewCoilAccept`.** On a fresh setup cold ohms is 0, so the lock row is hidden until YES commits a reading: if the screen stays up, the row appears and can be pressed; if YES dismisses it, the row is only reachable on a swap where a previous resistance is already stored, and a first lock has to be done from the OHMS page (High Contrast) or PROFILE (Color Themes). Either way nothing can lock 0. **Guard confirmed hiding the control 2026-10-30:** on a fresh High Contrast upload (cold ohms 0) the new-coil screen showed YES, NO and MEASURE with no LOCK? row, which is the condition resolving correctly. Still untested: the same screen on Color Themes, and whether the row appears after YES (the open question above). **Also found:** MEASURE on the High Contrast prompt looked dead because that screen displayed no resistance — `NewCoilResample` updates 1048579 and nothing was showing it. The screen now has the readout and MEASURE has been removed from it (`11`).
- ~~**High Contrast Ω / OHMS screen** (v1.2).~~ **Confirmed working 2026-10-30.** The `Ω` renders from codepoint 937 at FontStyle 0, `ChildScreen` reaches it from the menu, and LOCKED, the value, the LOCK toggle, MEASURE and BACK all display. `ResampleOhms` from a child screen is still unexercised - the button is there but was not pressed.
- **Theme Designer has a `Screenshot` button** on the Screens tab (`15`), which should render a screen straight to an image. That is very likely the fix for the stale screenshots below, without photographing the mod. Untried.
- **Power Lock (`Usage=4`) and Theme Change (`Usage=5`) screens** exist and we have never built either (`15`). Theme Change is the interesting one for Color Themes, where switching looks is the whole feature.
- **High Contrast screenshots are stale.** `../high-contrast/images/menu-screen.png` and `new-coil-screen.png` predate the ohms row; there is no screenshot of the OHMS screen yet.
- Whether every chip warning (e.g., "Temp Protected") appears in the status line.

- ~~**Replace-the-cup color warning**~~ **RESOLVED 2026-10-30 - it works on both themes.** The cause was the 8-child ceiling (`07` #26), not any operator. The investigation below is kept as history. Original entry: two things unverified: `<Compare Operator="2">` (greater-than) is listed **H**, not confirmed, and this is its first use in either theme — if it does not resolve, the number simply never turns red; and the thresholds rest on a **single** observed failure (0.43 → 0.61Ω), scaled to the Quest by ratio rather than measured. Limits and derivation in `02`.

  **Registered test design, 2026-10-30 — RESULT: neither went red.** Throwaway test themes were built with deliberately wrong limits — profile 1 (XL) **0.40**, profile 2 (QUEST) **0.90** — against known-good locked readings of XL 0.4637Ω and Quest 0.3141Ω. **Revised method:** neither cup was locked on the mod and the loose `.ecigprofile` files all carry `ColdResistance2 = 0`, so a theme-only test could not fire at all. The test configs instead **pre-lock both cups** (`EvolvWDColdOhms` 256/257 set to the readings above, `EvolvWDOhmLock` 1) so the test is self-contained and independent of device state. They lock a resistance that may not match the fitted cup, so they are bench tests: do not fire, and reload the real config afterwards. Published configs keep cold ohms 0 per `12`. Three outcomes, decided before running:
  - XL red, Quest white → operator 2 **and** the AND gating both work, as designed.
  - Both red → operator 2 works but the profile condition is not gating; the AND or the profile numbering is wrong.
  - Neither red → operator 2 does not resolve on this firmware; fall back to a different comparison or drop the warning.
  Requires a locked reading on the XL profile; with cold ohms 0 the test is inconclusive rather than negative.

  **Result, 2026-10-30:** on the XL profile the OHMS page read **0.464 in white**, not red, against a 0.40 limit; QUEST read 0.314 white as expected. **Color Themes behaves identically** — its home screen showed 0.464 in the theme color, not red, on the same test config. So the warning does not fire, and it is not a layout or variant-ordering quirk of one theme: on the High Contrast OHMS page the red variants are the only variants on that control, with nothing to lose a precedence fight to. **But "neither red" does not isolate the cause:** operators **2** (`>`) and **64** (AND) are both used *only* by this new code. The original v1.0 theme used exactly one operator, **3** (`<`), for the low-battery red, and that is the only comparison ever proven on this hardware. kb/10 lists 64 as confirmed, but not from a working theme here.

  **Probe build — RESULT, 2026-10-30: the AND is the problem.** One theme puts three independent probes on the OHMS page in three colors, so a single photo decides it:
  - value **red** if `ohms > 0.4` (flat, no AND) — tests operator 2 alone.
  - LOCKED **magenta** if `AND(profile == 1, ohms > 0.4)` — tests operator 64.
  - MEASURE **cyan** if `ohms < 0.9` (flat, operator 3) — tests whether cold ohms can be compared at all, using the one operator known to work.

  Readings: MEASURE cyan but value white → operator 2 is the problem, and the warning should be rebuilt inverted on operator 3 (default red, white below the limit). Value red but LOCKED white → the AND is the problem. Nothing colored → cold ohms cannot be used in a `Compare`, and the warning needs a different source field or has to be dropped.

  **Read on the XL profile at 0.464:** the value went **red** (`ohms > 0.4`, flat) and MEASURE went **cyan** (`ohms < 0.9`, flat), but LOCKED stayed yellow (`AND(profile == 1, ohms > 0.4)`). So **operator 2 works, operator 3 works, and the field is readable in a `Compare`** — only the nested AND fails. **Rebuilt 2026-10-30** as five layered flat variants instead (`07` #24); the layering is now the untested part, though every operator in it is confirmed on-device. `10` corrected: operator 2 promoted to confirmed, operator 64 marked as not working on this firmware.

## Audit of v2.2.05, 2026-10-30 - two defects and a contradiction

A full structural pass over both shipping builds, done with the `07` #26 lesson in hand: **count the
children first**. Every control in both themes was counted and every non-cosmetic variant located by
position. Method is reproducible - it is the only way to see this class of bug.

### Child-count census

| Children | Color Themes v2.2.05 | High Contrast v1.2.06 |
|---|---|---|
| 1 | 108 | 23 |
| 2 | 4 | 14 |
| 3 | - | 2 |
| 5 | 5 | 2 |
| 6 | - | 1 |
| 7 | 27 | - |
| **8** | **2** | - |

**High Contrast is structurally clean** - nothing above 6, because it has no theme tints. **Color
Themes spends 6 of its 8 slots on tinting**: 27 controls carry a default plus the six
`Operator="1"` toggle variants and nothing else. Those are safe (they are purely cosmetic and the six
are mutually exclusive), but they leave **one usable slot** on any tinted control, which is the real
structural limit of the v2 design.

### Defect 1: the low-battery warning sits on the ceiling - WITHDRAWN, it was never broken

> **Overturned on hardware 2026-10-30.** Child 8 is evaluated; the banner renders and persists. The
> analysis below is correct that the warning *sits* on the ceiling and wrong that the ceiling cuts
> below it. `v2.3.00`, which "fixed" it, is withdrawn as a regression. Kept as the record of how a
> plausible inference became a shipped build.

> Split per `18` principle 1 on 2026-10-30 and shipped as `v2.3.00`. The red `Picture` now sits on its own
> 2-child control over the same rect, next in both file order and `ZOrder`. Verified off-device: the only
> difference from `v2.2.05` anywhere in the eleven screens is this split, the warning image is byte-identical,
> and `tools/check-theme.py` passes. **The red bar has not been seen on hardware since the change.**


**The only functional variant in the whole theme that sits above position 5 is the low-battery red,
and it is child 8 of 8** - on both the home screen and the session screen, at `(0, 0)`.

| | Battery meter at `(0, 0)` |
|---|---|
| `v1.0` | **2 children** - default, then red `Meter` if level `< 15%`. Proven in service |
| `v2.2.05` | **8 children** - default, six theme tints, then the red `Picture` if level `< 15%` **last** |

Adding the themes pushed a proven warning from position 2 to position 8. It has to be last, because
last-match-wins is what lets it override a tint - so **the warning is only alive if the ceiling is
exactly 8, and that number is inferred, not measured** (`07` #26). Nobody would notice either way
without running the pack below 15%. This is the same failure mode as the ohms bug, in the one feature
with a clean service history.

**It is also fixable for free.** The 8th child is already a `Picture`, not a `Meter`, so it does not
need the level: move it into its own control over the same rect at a higher `ZOrder`, with a default
`<Hidden/>` ahead of it. Two children, no new images, and the tints keep their seven slots.

### Defect 2: the live-ohms row shows a field known to read 0

Session screen `(16, 104)` displays field **1048642**, which `05` records as *"Live ohms. Reads 0 when
idle after boot, and 0 during the first session after power-on."* It carries seven children, all
tinting, so it is not a ceiling risk - but it is a row that is blank or wrong exactly when a user would
first look at it.

### The contradiction: is operator 64 confirmed or dead?

`09` and `10` disagree, and have since the replace-warning investigation closed:

- **`10` line 183:** *"`64` - AND of the nested Compares. **Confirmed** - this is exactly what Theme
  Designer emits for the word `and`"*, rated **C**.
- **`09`, operator table:** *"Operator 64 (AND) Does not work on this firmware (`10`). Unchanged."*

**`10` is closer to right, and neither is properly evidenced.** Every `.ecig` ever uploaded to this
device containing an `Operator="64"` had **operator 129 inside it**:

| File | The AND it carried |
|---|---|
| `gremlin_v2.2.02-TEST-threshold.ecig` | `AND(129 profile==1, 2 ohms>0.4)` |
| `gremlin_high_contrast_v1.2.02-TEST-threshold.ecig` | same shape, four times |

`129` is the operator EScribe **zeroes the `RefValue` of** on round-trip (`10`), so those compares read
`profile == 0`, which never matches - the AND could not have fired whatever operator 64 does. **The
on-device evidence against operator 64 is confounded, and the three-color probe that produced the
verdict predates the discovery that the tool emits `4` for equality, so it almost certainly used `129`
too.**

The fair test already exists and was never run: **`Downloads\Condition A and B.ecigtheme`**, authored
by Theme Designer itself, one control, **two children**, carrying
`AND(Operator 2 ohms > 0.4, Operator 4 profile == 1)` - both operators confirmed on-device, far below
any ceiling. Independent support: Copyman's third-party theme uses `Operator="65"` (OR) and runs
(`10` line 184), so nesting itself works.

**This one test decides the shape of v3.** If the AND resolves, all four replace-warning chains
collapse from five children to two, the cancel layers disappear, the Color Themes home screen gets its
theme color back across an XL's healthy range, and the cleaning-profile special case goes away.

## Registered: the v2.3.00 battery overlay - WRITTEN BEFORE RUNNING, 2026-10-30

`v2.3.00` moved the low-battery red off the battery meter onto its own control (`18` A). What is
unproven is not the 15% threshold - unchanged and working since `v1.0` - but **whether a second
control drawn over the same rectangle renders at all**.

Draining a pack to test it is a poor ask, and faking the level is unreliable: `Battery Charge` appears
in Device Monitor's writable table (`14`) but it is a live measurement the ADC re-reads, and `14`
already warns that a scripted write may not reach a theme field the way a real reading does.

**So flip the threshold, not the battery.** `Downloads\BENCH-BATTERY.ecig` is `v2.3.00` with every
low-battery compare changed from `< 15` to `< 101`, which is true at any state of charge.

**This one is not a locked bench config** - cold ohms ship 0 and unlocked, exactly as `v2.3.00` does,
so nothing about resistance is faked and it is safe to fire. Just do not keep it: it reads low battery
permanently.

### Three compares were flipped, and the third is the control

| Where | Control | Role |
|---|---|---|
| Home `(0, 0)` | the **overlay**, 2 children | the thing under test |
| Session `(0, 0)` | the **overlay**, 2 children | the thing under test |
| Home `(40, 118)` | battery **percentage text**, 2 children, never an overlay | **positive control** |

The percentage text was never at risk - it has always been a plain 2-child control. So it going red
proves the upload landed and the compare resolves, which separates *"the overlay does not draw"* from
*"nothing happened"*.

### Expected, decided before running

| Observation | Meaning |
|---|---|
| **Percentage red AND bar red** | the overlay draws. `18` A confirmed, and principle 1 is viable for the ohms row too (`18` C) |
| **Percentage red, bar NOT red** | **the overlay does not render.** The split is wrong; revert to the v2.2.05 shape and accept the ceiling risk, or find another construction |
| **Bar red but misplaced, doubled or clipped** | it draws but geometry is off - check `Location`/`Size` on the new control |
| **Neither red** | void, not negative. The upload did not land; re-check and re-run |

Then, on loading real `v2.3.00` afterwards, **neither should be red** at normal charge - the off state,
which completes the pair without any extra upload.

### RESULT, 2026-10-30: the logic is right, the cancel color is not

| Profile | Locked | Expected | Observed |
|---|---|---|---|
| 1 XL | 0.4637 | white | **nothing renders - the name is invisible** |
| 2 QUEST | 0.4504 | RED | **RED** |
| 3 XL CLEAN | 0.6500 | RED | **RED** |
| 4 Q CLEAN | 0.3141 | white | **black and clearly legible** |

**Red on exactly the two profiles that should be red**, so the chain, the thresholds and the
cleaning-profile handling are all correct. The failure is presentation.

**Cause: white text on the white selection highlight.** The profile name is a selectable control, so
the firmware draws it on a white highlight band. Profile 1's cancel paints explicit `(1, 1, 1, 1)`
onto that, and the two disappear into each other. Profile 4 is the proof: no variant matches, it falls
through to the default, and the firmware renders the default **dark** on the highlight - legible.

**`07` already has this written down** and the `v1.2.06` build walked straight into it: *"Explicit
`Color="(1, 1, 1, 1)"` on selectable items keeps text white on the white highlight (invisible). Omit
the color for default white."* The rule was learned on menu rows and never connected to the cancel
layers, which were inherited from Color Themes - where the background is dark and white is correct.

**Not fixed by picking a better cancel color.** Explicit black would be invisible the moment the
highlight moved off that control, and a cancel with *no* `Color` is unproven - whether a matching
variant that sets no color repaints in the default or paints nothing was hypothesis **b** of Probe 1
and was never cleanly settled, because the child ceiling confounded that run.

**Fixed in `v1.2.07` by deleting the cancels instead.** With operator 64 confirmed the same hours
earlier, the chain is stated directly and nothing but RED is ever set, so the default is never
overridden and the highlight problem cannot arise:

    default -> RED if ohms > 0.6
            -> RED if AND(ohms > 0.41, profile == 2)
            -> RED if AND(ohms > 0.41, profile == 4)
            -> Hidden while firing

Five children. `ohms > 0.6` needs no profile test because 0.6 is already past the Quest's own 0.41
limit, so it is red on every profile anyway - which is what removes the XL rules entirely. This is
`18` B, applied to the one control that is broken; the OHMS page and the new-coil prompt keep their
proven five-layer chains until there is a reason to touch them.

### Also confirmed in the same sitting: `ResampleOhms` works from a child screen

MENU -> Ω OHMS -> **MEASURE** re-reads the current value, reported by the operator. That closes one of
the three long-standing untested items and means **`Action` works from a child screen**, which was
genuinely open - it matters for any future screen built behind the menu.

## Registered: v1.2.07, the recut home-screen chain - WRITTEN BEFORE RUNNING

`Downloads\BENCH-HC-v1207.ecig`, same four locked resistances. Read the **profile name on the home
screen**. This is also the **first shipped use of operator 64**, so it doubles as confirmation that
the AND survives outside a probe.

| Profile | Locked | Matches | Expected |
|---|---|---|---|
| 1 XL | 0.4637 | none | **default - dark and legible, like Q CLEAN was** |
| 2 QUEST | 0.4504 | `AND(>0.41, p==2)` | **RED** |
| 3 XL CLEAN | 0.6500 | `>0.6` | **RED** |
| 4 Q CLEAN | 0.3141 | none | **default - dark and legible** |

- **dark / RED / RED / dark** - fixed, and operator 64 is proven in a shipping build.
- **Profile 1 still invisible** - the default itself is white here and the highlight is the whole
  problem; the control needs an explicit color that contrasts, or to move off the highlight.
- **Profile 2 or 4 not red** - the AND does not survive in a real chain the way it did on a 2-child
  probe control. That would be a significant finding; re-run the probe before concluding.
- **Profile 3 not red** - the flat `>0.6` regressed, which contradicts the OHMS page.

### RESULT, 2026-10-30: the overlay draws, then gets painted over

Operator report: *"the low battery shows for a short time when the home screen first displays, but is
then replaced by the regular battery screen."*

So the red **does** render - `ZOrder`/file order is honoured on the initial paint, and the split is
geometrically correct. But it does not survive.

**Cause, read straight out of the file:** all seven tinted `Meter`s on that control are bound to
**field 65537**, the live battery level. The red `Picture` has **no `Source` at all**. The meters
therefore repaint every time the level refreshes, and the static overlay above them is never dirty,
so it is never redrawn - the meter simply paints over it.

### This revises `18` principle 1

> **Splitting a warning onto its own control only works over a control that does not repaint.**

The single-control design that `18` set out to replace is *correct* for a live control, and for a
reason worth stating: when the whole control repaints, its variant list is re-evaluated from scratch,
so the winning child is re-chosen every frame. An overlay has to be re-dirtied by something, and a
static child never is.

That leaves the battery with no free lunch, and it **casts real doubt on `18` C** - the ohms readout
is live too, so the same trap applies there.

**`v2.3.00` is therefore not recommended until this resolves.** A warning that flashes and vanishes is
worse than one that never appears, because it trains you to disbelieve it. The repo keeps the build;
`09` and the release notes say not to rely on it.

## Registered: which battery construction actually holds - WRITTEN BEFORE RUNNING

`Downloads\BENCH-BATTERY-2.ecig`, built from **`v2.2.05`** with every low-battery threshold moved to
`< 101`, true at any charge. Two different constructions, one on each screen, so a single upload
answers both. Cold ohms ship 0 and unlocked - nothing about resistance is faked, safe to fire, but do
not keep it.

| Screen | Construction | Question |
|---|---|---|
| **Main** (design 2) | the **`v2.2.05` shape** - red `Picture` as child **8** of the meter control | **Is child 8 evaluated at all?** The ceiling of 8 has only ever been inferred |
| **Lock** (design 1) | the split, but the overlay is a **live red `Meter`** bound to 65537 instead of a static `Picture` | **Does a live overlay get redrawn** when the control under it repaints? |

`tools/check-theme.py` deliberately **fails** this file on the main screen - that control is the old
shape on purpose, and the failure is the tool working, not a defect in the bench build.

### Expected, decided in advance

| Main screen | Lock screen | Conclusion |
|---|---|---|
| red **persists** | either | **The ceiling is at least 8 and child 8 works.** The audit's defect was theoretical; revert the `v2.3.00` split and keep the tints |
| red flashes or never shows | red **persists** | Child 8 really is dropped, **and a live overlay is the fix.** Rebuild the split with a `Meter`, not a `Picture` |
| red flashes or never shows | also flashes | Neither construction works over a live control. Fall back to the **`v1.0` shape** - drop the six tints from the battery bar, leaving default + red at 2 children. Costs the bar its theme color, the same trade the ohms row already made |
| red persists | red flashes | 8 works and overlays do not. Same action as the first row, and `18` C is dead - the ohms row can never be tinted |

The battery **percentage text** on the lock screen is the positive control, as before: it is a plain
2-child control that was never at risk, so it going red proves the upload landed.

### RESULT, 2026-10-30: child 8 works. The defect was not a defect, and v2.3.00 is withdrawn

| Screen | Construction | Observed |
|---|---|---|
| **Main** (design 2) | `v2.2.05` shape - LOW BATTERY banner as child **8** | **Red, and it stays.** Operator: *"It stays like this"* |
| **Lock** (design 1) | split, overlay is a **live red `Meter`** | **Red, and it renders** - banner plus the 99% in red |

**Child 8 is evaluated.** The ceiling is at least 8, so the control that the audit called a live
defect was working the whole time. The low-battery warning has never been broken.

That makes **`v2.3.00` a regression introduced to fix nothing**, and it is withdrawn: the build files
are removed and `release/RELEASE-NOTES.md` says so. `v2.2.05` is the Color Themes release again.

**What the ceiling actually is:** 8 renders, 11 truncates (`07` #26). The cutoff is somewhere in 9..10
and still unmeasured - but the number that matters for day-to-day work is that **8 is safe**, which is
now observed rather than inferred.

**Second confirmation of the repaint rule.** The live-`Meter` overlay on the lock screen *did* render,
where `v2.3.00`'s static `Picture` overlay flashed and vanished. So an overlay survives if it has its
own live source and is re-dirtied with the control beneath it. That is a real finding, and it is
**not needed** - the single-control design is simpler, already shipping, and now proven.

### The cost of this episode, recorded honestly

Three builds and two bench uploads were spent fixing something that was not broken. The audit was
right that child 8 *could* be truncated and wrong that it *was*, and the gap between those two is
exactly the test that was never run. The 8-child ceiling from `07` #26 was inferred from where other
controls happened to stop, and that inference got treated as a measurement for most of a day.

**What was actually gained:** the ceiling is now measured at the only value anyone needed, the repaint
rule is understood and written down, `tools/check-theme.py` exists and is correct, and `18`'s central
principle was wrong in a way that would have been far more expensive to discover while rewriting all
four replace-warning chains.

### What this reopens

With 8 confirmed, `1 default + 6 tints + 1 warning variant = 8` is **viable**, so `18` C is alive
again - the ohms row could keep its theme color if the whole replace warning collapses to a *single*
variant. That needs

    red if OR( ohms > 0.6, AND( ohms > 0.41, OR(profile == 2, profile == 4) ) )

which is **nesting depth 4**, and only depth 2 is proven (`09`, the operator-64 probe). One probe
would settle it. The cheaper fallback, if deep nesting fails, is to drop one tint from that control
and use two variants at depth 2 - one theme loses its ohms tint rather than all six.

### RESULT, 2026-10-30: dark / RED / RED / dark, exactly as registered. v1.2.07 passes

| Profile | Locked | Expected | Observed |
|---|---|---|---|
| 1 XL | 0.4637 | dark | **dark and legible** |
| 2 QUEST | 0.4504 | RED | **RED** |
| 3 XL CLEAN | 0.6500 | RED | **RED** |
| 4 Q CLEAN | 0.3141 | dark | **dark and legible** |

Read **with the menu item highlighted**, which is the case that broke `v1.2.06` - so the fix is
confirmed under the condition that caused the bug, not around it.

**Three things are settled by this one run.**

1. **The white-on-white bug is fixed.** Profile 1 reads like Q CLEAN always did. Deleting the cancel
   layers was the right call: nothing but RED is ever set now, so the default is never overridden and
   the highlight cannot swallow it.
2. **Operator 64 works in a shipping chain**, not just on a 2-child probe control. Profiles 2 and 4
   carry `AND(ohms > 0.41, profile == N)`; it fired on 2 at 0.4504 and correctly stayed silent on 4 at
   0.3141, which is the AND evaluating *both* children in a real theme.
3. **The flat `ohms > 0.6` covers the XL family** with no profile test at all - profile 3 reds from it
   while profile 1 does not. That is what let the two cancel layers and the cleaning-profile special
   case be deleted outright, and it is the shape `18` B prescribes for the remaining three controls.

`v1.2.07` is the High Contrast release and is **proven on hardware**.

**Checked afterwards, so the same trap is not waiting elsewhere:** four controls still carry explicit-white
cancel layers - the HC OHMS page and new-coil prompt, and the Color Themes home screen and new-coil prompt.
**None of them is selectable** (all `ReadOnly`, no `Action`), so none can be drawn on the highlight and none
is at risk. The rule is now mechanical in `tools/check-theme.py`, which fails `v1.2.06` and passes
`v1.2.07`. Rewriting those four to the `18` B shape is therefore **cleanup, not a bug fix**.

### RESULT, 2026-10-30: nesting works to depth 4, and nested operators are strictly BINARY

Read with the **Retro theme on**, so the tinting was live throughout and did not interfere - the
probes sit on their own 2-child controls with explicit colors.

| Profile | Locked | `DEP2` depth 1 | `DEP3` depth 3 | `OR3` 3-child OR | `DEP4` depth 4 |
|---|---|---|---|---|---|
| 1 XL | 0.4637 | **orange** | grey | grey | grey |
| 2 QUEST | 0.4504 | **orange** | **magenta** | **grey** | **green** |
| 3 XL CLEAN | 0.6500 | **orange** | grey | **grey** | **green** |
| 4 Q CLEAN | 0.3141 | grey | grey | grey | grey |

**Two findings, and the second was not on the card as a possibility.**

**1. Nesting resolves to at least depth 4.** `DEP3` fired on profile 2 only, exactly as registered, and
`DEP4` fired on profiles 2 and 3 and nowhere else - which is the entire per-cup replace warning,
correct, **in a single variant**.

**2. `Operator="65"` (and by implication `64`) takes exactly TWO children. A third kills it.**
`OR3` never lit on any profile. That is not "the third child was ignored": with three children
`OR(ohms > 0.6, AND(…p==2), AND(…p==4))`, dropping *any* one of them still leaves a form that is true
on profile 2 or profile 3, and it was grey on both. So the compare does not partially evaluate - **it
fails outright**. `64` and `65` are binary operators, not n-ary lists, and the only way to combine
three conditions is to nest a second operator. That is worth knowing before anyone writes one by hand
in Theme Designer and wonders why a condition never fires.

`10` updated with both.

### What this buys

The warning now fits in **one** variant, so the Color Themes ohms row can be
`1 default + 6 tints + 1 variant = 8 children` - and 8 is confirmed to render. **The compromise
`07` #24 accepted is over:** the home-screen resistance gets its theme color back across a V5 XL's
healthy range, instead of reading white.

The shape to use everywhere, all operators and the depth confirmed on-device:

```xml
<Compare Operator="65">
  <Compare Operator="2" Field="<ohms>" RefValue="0.6" />
  <Compare Operator="64">
    <Compare Operator="2" Field="<ohms>" RefValue="0.41" />
    <Compare Operator="65">
      <Compare Operator="4" Field="262151" RefValue="2" />
      <Compare Operator="4" Field="262151" RefValue="4" />
    </Compare>
  </Compare>
</Compare>
```

Read aloud: *red if the resistance is past 0.6, or past 0.41 on either QuestCup profile.* The XL needs
no rule of its own because 0.6 is already past the Quest's limit, and the cleaning profiles stop being
a special case because they are just members of their cup's family.

## Registered: v2.3.01 - the single-variant warning, with the tint back - WRITTEN BEFORE RUNNING

`Downloads\BENCH-CT-v2302.ecig`, the four standard locked resistances. Rebuilt from `v2.3.02` so the bench config carries the same profile settings as the release; the theme is unchanged from `v2.3.01`, so the expected results below stand. **Do not fire.**

Two controls changed and nothing else, verified by diffing every control in all eleven screens:

| Screen | Control | Before | After |
|---|---|---|---|
| Main | `(16, 88)` cold ohms | 5 children, no tints | **8** - default, six tints, one warning |
| New coil | `(32, 24)` pending reading | 5 children | **2** - default, one warning |

### Expected

| Profile | Locked | Home-screen ohms |
|---|---|---|
| 1 XL | 0.4637 | **theme color** - cyan on Retro, not white and not red |
| 2 QUEST | 0.4504 | **RED** |
| 3 XL CLEAN | 0.6500 | **RED** |
| 4 Q CLEAN | 0.3141 | **theme color** |

**The thing to look at is profile 1.** On `v2.2.05` that row reads white; it should now take whichever
theme is on. Switch themes under MENU -> THEMES and it should follow. That is the whole point of the
release - everything else behaves exactly as `v2.2.05` did.

- **theme / RED / RED / theme** - ships.
- **Profile 1 red** - the `OR(p==2, p==4)` arm is matching when it should not. Contradicts `DEP4`.
- **Profile 2 or 3 not red** - the warning lost to a tint, meaning it is not last or is being
  truncated at child 8. Count the children before anything else.
- **Profile 1 white rather than themed** - the tints are not matching on that control; compare their
  `Compare` fields against the live-ohms row they were copied from.
- **Nothing themed anywhere** - the theme toggle is off; not a result.

### RESULT, 2026-10-30: theme / RED / RED / theme, exactly as registered. v2.3.02 passes

| Profile | Locked | Expected | Observed |
|---|---|---|---|
| 1 DTv5XL | 0.4637 | theme color | **cyan** - the Retro resistance tint |
| 2 Quest | 0.4504 | RED | **RED** |
| 3 DTv5XL-Clean | 0.6500 | RED | **RED** |
| 4 Quest-Clean | 0.3141 | theme color | **cyan** |

**The tint is back.** On `v2.2.05` the cold-ohms row read white while the live-ohms row beneath it
took the theme color; they now match, which is the visible proof that the compromise `07` #24
accepted is over. One variant instead of five left room for the six tints, and the warning still wins
because it is last.

**Three things are settled by this run.**

1. **The single-variant warning works in a shipping build.** `OR(ohms > 0.6, AND(ohms > 0.41,
   OR(p==2, p==4)))` - nesting depth 4, operators 2, 4, 64 and 65 - fires on exactly the two profiles
   it should. The depth-4 probe is confirmed outside a probe.
2. **The theme tint and the warning coexist on one control at 8 children**, with the warning as child
   8. That is the arrangement `18`'s withdrawn principle 1 said to avoid, and it is correct.
3. **The profile settings landed.** Visible in the same photos: 385 F and 120 s on DTv5XL and Quest,
   36 W / 25 W / 38 W / 35 W, 45 s on Quest-Clean, and the shorter **Quest** and **Quest-Clean** names.

**Every control in both shipping builds is now proven on hardware** except the new-coil prompt, which
is tracked separately below and was not exercised by this run.

## Registered: how deep can nesting go, and is OR n-ary? - WRITTEN BEFORE RUNNING, 2026-10-30

**This decides what `v2.3` contains.** Section B of `18` - stating the replace warning as real
conditions - is proven and ships regardless. What is open is whether the warning can collapse to a
**single** variant, because `1 default + 6 tints + 1 variant = 8`, and 8 is now confirmed to render.
A single variant is therefore the difference between the Color Themes ohms row keeping its theme
color and staying white, which is the one user-visible thing `v2.3` could deliver.

`Downloads\PROBE-DEPTH.ecig`, built from `v2.2.05` with the four standard locked resistances. Four
probes on the main screen, each on its own **2-child** control. **Do not fire.**

| Row | Colour | Condition | Nesting |
|---|---|---|---|
| `DEP2` | orange | `ohms > 0.41` | depth 1 - the positive control, already proven |
| `DEP3` | magenta | `AND(ohms > 0.41, OR(p==2, p==4))` | **depth 3** - an OR inside an AND |
| `OR3` | cyan | `OR(ohms > 0.6, AND(>0.41, p==2), AND(>0.41, p==4))` | depth 3, but the **OR has three children** |
| `DEP4` | green | `OR(ohms > 0.6, AND(>0.41, OR(p==2, p==4)))` | **depth 4** |

`OR3` and `DEP4` express the *same* rule two ways - the whole per-cup warning in one variant. Either
one working is enough.

### Expected, decided before running

| Profile | Locked | `DEP2` | `DEP3` | `OR3` | `DEP4` |
|---|---|---|---|---|---|
| 1 XL | 0.4637 | **orange** | grey | grey | grey |
| 2 QUEST | 0.4504 | **orange** | **magenta** | **cyan** | **green** |
| 3 XL CLEAN | 0.6500 | **orange** | grey | **cyan** | **green** |
| 4 Q CLEAN | 0.3141 | grey | grey | grey | grey |

The `OR3`/`DEP4` column is exactly the replace warning's intended behaviour, which is the point: if
those two light on profiles 2 and 3 and nowhere else, the rule fits in one variant.

Note `DEP3` is deliberately *not* the full rule - it omits the `> 0.6` case, so it should fire on
profile 2 only. That is what separates "depth 3 works" from "the rule is expressible".

### What each result means, fixed in advance

- **`OR3` or `DEP4` correct** → the warning collapses to one variant. `v2.3` ships section B **and**
  restores the ohms theme color on the Color Themes home screen, undoing the compromise `07` #24
  accepted. Record the working depth in `10`.
- **Both wrong, `DEP3` correct** → depth 3 works but the rule needs two variants, which is
  `2 + 6 + 1 = 9` and over the ceiling. `v2.3` ships section B only; the ohms row stays white.
- **`DEP3` also wrong** → nesting stops at depth 2. Same outcome, and `10` gets a measured limit.
- **`DEP2` grey anywhere it should be orange** → void, not negative. The upload or the locks did not
  land; re-run.
- **Anything lit on profile 4** → something matches unconditionally; suspect the default child.

## Registered: does operator 64 (AND) actually work? - WRITTEN BEFORE RUNNING, 2026-10-30

Settles the contradiction in the audit above, and decides whether v3's replace warning is two layers or
five. Every AND ever put on this device had operator `129` inside it, whose `RefValue` EScribe zeroes,
so **no previous run could have fired whatever 64 does**.

`Downloads\Condition A and B.ecigtheme` was examined first and **rejected as a test**: its one AND sits
on a control at `Location="(70, 49)"` on an 80-wide screen, so it renders a few clipped pixels, and it
is on the new-coil screen. Authored in Theme Designer, never positioned to be read - which is why no
result was ever recorded for it.

**Bench file:** `Downloads\PROBE-AND.ecig`, built from `v2.2.05` with the four standard locked
resistances. **Do not fire. Reload the real config after.**

### The probe

Four independent probes on the main screen, each **its own control with exactly 2 children** so the
child ceiling cannot confound anything, and each using **only operators confirmed on-device** inside
the nesting. Each reads dark grey `(0.3, 0.3, 0.3, 1)` when its condition is false, so an unmatched
probe is still legible and cannot be mistaken for a missing control.

| Row | Replaces | Condition | Color when true |
|---|---|---|---|
| `AND1` | the big temperature, `(0, 24)` | `AND(ohms > 0.41, profile == 1)` | **green** |
| `AND2` | the SET label, `(0, 50)` | `AND(ohms > 0.41, profile == 2)` | **magenta** |
| `OR13` | the watts readout, `(2, 67)` | `OR(profile == 1, profile == 3)` | **cyan** |
| `FLAT` | the live-ohms row, `(16, 104)` | `ohms > 0.41` - flat, no nesting | **orange** |

`FLAT` is the positive control: operator 2 is proven, so if it never lights the upload or the lock did
not take and the run is void rather than negative. The profile name and the ohms readout are kept, and
menu navigation is untouched - `(56, 140)` still opens MENU, so profiles switch from MENU -> PROFILE.

### Expected, decided before running - a full truth table in four photos

| Profile | Locked | `AND1` | `AND2` | `OR13` | `FLAT` |
|---|---|---|---|---|---|
| 1 DTv5XL | 0.4637 | **green** | grey | **cyan** | **orange** |
| 2 QuestCup | 0.4504 | grey | **magenta** | grey | **orange** |
| 3 DTv5XL-Clean | 0.6500 | grey | grey | **cyan** | **orange** |
| 4 QuestCup-Clean | 0.3141 | grey | grey | grey | grey |

Profile 4 is the all-grey row: nothing may light there, which catches a variant that matches
unconditionally. Profiles 1 and 2 together are what actually prove the AND - each has one probe true
and one false on the *same* two fields, so an AND that merely ignores its second child is caught.

### What each result means, fixed in advance

- **The table as printed** - operators 64 and 65 both work. v3 collapses all four warning chains to two
  children, drops the cancel layers, restores the home-screen theme color on the ohms row, and uses
  `OR` for the cleaning profiles. `09`'s deferred simplification is live and `10` line 183 is vindicated.
- **`FLAT` lights, `AND1` never does** - operator 64 does not resolve. Keep the five-layer chains; mark
  64 dead in `10` with evidence this time, and close the contradiction the other way.
- **`AND2` lights on profile 1** (or `AND1` on profile 2) - **64 is not an AND.** It behaves as an OR or
  ignores a child. Worse than useless: never use it, and note that the five-layer chain is the only
  safe construction.
- **`OR13` lights but `AND1` does not** - OR works, AND does not. Partial win: the cleaning-profile
  special case collapses, the thresholds stay layered.
- **`FLAT` grey on every profile** - void, not negative. The upload did not take or the locks did not
  land; check MENU -> PROFILE shows a non-zero resistance and re-run.
- **A row missing entirely** - a layout or font problem in the probe, not a logic result. Re-cut it.

### RESULT, 2026-10-30: the table exactly as registered. Operators 64 and 65 both work.

Read with the **Retro theme enabled**, which the earlier precedence probes were not - so the tinting
was live throughout and did not interfere.

| Profile | Locked | `AND1` | `AND2` | `OR13` | `FLAT` | Ohms readout |
|---|---|---|---|---|---|---|
| 1 DTv5XL | 0.4637 | **GREEN** | grey | **CYAN** | **YELLOW** | 0.464 white |
| 2 QuestCup | 0.4504 | grey | **MAGENTA** | grey | **YELLOW** | 0.450 **RED** |
| 3 DTv5XL-Clean | 0.6500 | grey | grey | **CYAN** | **YELLOW** | 0.650 **RED** |
| 4 QuestCup-Clean | 0.3141 | grey | grey | grey | grey | 0.314 plain |

**All sixteen cells match.** Green appears on profile 1 only and magenta on profile 2 only - the two
cells that cannot both be right unless the AND is evaluating *both* of its children. Profile 4 is
entirely dark, so nothing matches unconditionally. `FLAT` lights on 1-3 and not 4, so the run is valid.

**`Operator="64"` is a true AND and `Operator="65"` is a true OR**, with operators `2` and `4` nested
inside, on this firmware. `10` line 183 was right; the `09` entry calling 64 dead was wrong, and the
cause was exactly the confound identified in the audit - every previous AND had operator `129` inside
it, whose `RefValue` EScribe zeroes.

**Free regression in the same run:** the `v2.2.05` replace warning read white / RED / RED / plain
across the four profiles, matching the result it shipped on, this time with a theme active.

**Proven depth is 2** - one `Compare` nested inside one `Compare`. Three levels (an `OR` inside an
`AND`) is **not** tested, and `18` section C explains why collapsing the condition does **not** buy the ohms row its theme color
back either way - even one variant plus the six tints lands on the ceiling - and why the open
question is a text-over-text overlay instead.

## Registered: the HC home-screen replace warning (v1.2.06) - WRITTEN BEFORE RUNNING, 2026-10-30

The last untested piece of either shipping build. `v1.2.06` moved the replace warning onto the High
Contrast **home screen** by coloring the profile name, because ohms is not on that screen (corrected
after the v1.2.05 run, below). Verified by inspection only until now.

**Bench file:** `Downloads\BENCH-HC-HOME-WARNING.ecig` - the `v1.2.06` theme plus four locked
resistances, so one upload exercises every layer. **Do not fire on it. Reload the real config after.**

### The chain, read out of the built file

Screen index 1 (design ID 2), the profile-name control at `(0, 24)`, **6 children** - inside the
ceiling of 8 (`07` #26), which was checked first this time:

    default (no Color) -> red if ohms > 0.41 -> white if profile == 1
            -> white if profile == 3 -> red if ohms > 0.6 -> Hidden while firing

Only operators **2** and **4** appear, both confirmed on-device. The final `<Hidden>` is gated on
`17825798` (Firing), so it should never match while the mod is idle - but note it is the **last**
child, so under last-match-wins it would blank the name if it ever did.

### Expected, decided before running

| Profile | Name | Locked | Layers that match | Expected |
|---|---|---|---|---|
| 1 | XL | 0.4637 | red(>0.41), white(p==1) | **white** |
| 2 | QUEST | 0.4504 | red(>0.41) | **RED** |
| 3 | XL CLEAN | 0.6500 | red(>0.41), white(p==3), red(>0.6) | **RED** |
| 4 | Q CLEAN | 0.3141 | none | **white** (the default) |

### What each failure would mean, decided in advance

- **white / RED / RED / white** - it works. `v1.2.06` ships, and every chain in both themes is proven.
- **Profile 1 RED** - the `p == 1` cancel is not winning on this screen, although the identical chain
  wins on the OHMS page. Suspect the trailing `<Hidden>` child interfering with precedence; test by
  moving it to the front.
- **Profile 3 white** - the `> 0.6` layer is not winning. Contradicts the proven OHMS-page chain.
- **Profile 4 RED** - something matches unconditionally; suspect the default child.
- **No profile name at all** - the `<Hidden>` on `17825798` matches when not firing, so Firing reads
  non-zero at idle. Invert it or drop it.

### Riding along in the same sitting, both free

- **`ResampleOhms` from a child screen.** MENU -> `Omega OHMS` -> press **MEASURE**. The button has
  never been pressed. Expected: the resistance re-reads. This is the only way to find out whether an
  action works from a child screen.
- **The OHMS page chain re-confirmed.** Same four profiles, same expected column, already proven on
  `v1.2.05`. Free regression check.

**Not covered by this upload:** the Color Themes new-coil `LOCK?` row, which needs a Color Themes
config. That stays open.

## HISTORY: the replace-warning investigation, 2026-10-30

> Everything from here to *High Contrast bench test* is the **record of how the bug was found**, kept
> because the wrong turns are instructive and because each test was registered before it ran. It
> contains conclusions that were later overturned - they are marked where they appear. **For the
> settled answer, read the top of this file and `07` #26.**

### Registered test card: v2.2.03 / v1.2.03 - WRITTEN BEFORE RUNNING

Neither build has been on hardware since the replace warning was rebuilt as layered flat variants.
Designed first, outcomes fixed before the run, per the rule that a verdict
is not recorded until it has been waited out.

### What is actually at risk

`v1.0`, the only build with a clean service history, used **one** operator: `3`. Everything else is new.

| Operator | Uses in v2.2.03 | Proven on this device? |
|---|---|---|
| `1` (!=) | 187 | **Yes** - the new-coil lock guard hides at cold ohms 0 |
| `2` (>) | 4 | **Yes** - the probe build, 2026-10-30 |
| `3` (<) | 3 | **Yes** - the v1.0 low-battery red |
| `129` (equals) | 12 | **No. Never exercised.** `10` marks it confirmed; that overstates what was checked |

The whole per-cup design rests on `129`. If it does not resolve, every cup falls back to the single
0.41 limit and the XL reads red from the day it is fitted.

### The variant chain, as built

Identical on all four displays (CT home 17825794, CT prompt 1048579, HC prompt 1048579, HC OHMS 17825794).
Last matching variant wins:

    default -> red if ohms > 0.41 -> plain if profile == 1 -> plain if profile == 3 -> red if ohms > 0.6

Profiles are 1-based and, confirmed from `EvolvATFriendlyName` in the config, are
**1 XL, 2 Quest, 3 XL-Clean, 4 Quest-Clean**. So the two whitelisted profiles are both the XL, which is
the intent: the XL is governed by 0.6 and the Quest by 0.41.

### The bench configs

Two configs, one per theme, each locking a different resistance on each of the four profiles so a single
upload exercises every layer. Built in the scratchpad, **not committed** - published configs ship cold
ohms 0 (`12`), and these lock a resistance that will not match the fitted cup.

**Do not fire on these.** Reload the real config afterwards.

| Profile | Cup | Locked ohms | Layers that match | Expected |
|---|---|---|---|---|
| 1 | XL | 0.4637 | red(>0.41), plain(p==1) | **plain** |
| 2 | Quest | 0.4504 | red(>0.41) | **RED** |
| 3 | XL-Clean | 0.6500 | red(>0.41), plain(p==3), red(>0.6) | **RED** |
| 4 | Quest-Clean | 0.3141 | none | **plain** |

### What each result means, decided in advance

- **plain / RED / RED / plain** - everything works. The warning ships, and `129` is genuinely confirmed.
- **Profile 1 RED** - `129` does not resolve. Not a layering bug: red(>0.41) is simply the last match.
  Rebuild the whitelist on operator `1` (!=) instead, which is proven, by inverting the sense.
- **Profile 3 plain** - the `>0.6` layer is not winning. Either operator `2` regressed at that value or
  variant precedence is not last-match-wins, which would contradict `04`.
- **Profile 2 plain** - operator `2` regression. Contradicts the probe build; re-run the probe.
- **Profile 4 RED** - something matches unconditionally. Suspect the default variant.

### The rest of the run, same sitting

| # | Check | Expected |
|---|---|---|
| E | Fresh upload of the real config, both themes | Both non-cleaning profiles start at **380F**; resistance **0**, lock **off** |
| F | New-atomizer screen at cold ohms 0 | **No `LOCK?` row** (the guard). After a reading is committed the row appears, and locking takes the real value, never 0 |
| G | HC menu -> `Omega OHMS` | Child screen opens, the omega glyph renders, MEASURE resamples, BACK returns |

`F` carries the one question left from 2026-10-30: **does the prompt survive `NewCoilAccept`?** If YES
dismisses the screen, the lock row is only reachable on a later swap, and a first lock has to be done
from the OHMS page (HC) or PROFILE (CT). Either way nothing can lock 0, so this decides documentation,
not correctness.

### Result - RUN 2026-10-30 (conclusion later OVERTURNED: the operator was not the cause)

| Profile | Locked | Expected | Observed |
|---|---|---|---|
| 1 DTv5XL | 0.4637 | plain | **RED** |
| 2 QuestCup | 0.4504 | RED | RED |
| 3 DTv5XL-Clean | 0.6500 | RED | RED |
| 4 QuestCup-Clean | 0.3141 | plain | plain |

This is the pre-registered **"Profile 1 RED"** outcome: **operator `129` does not resolve on this
firmware**. All four readings fit that single explanation - with the profile whitelist never matching,
every cup falls back to the one 0.41 threshold, which is exactly what the photographs show.

**Confirmed in passing:** both non-cleaning profiles start at **380F** and the cleaning pair at 450F,
so that change works.

**Fixed in v2.2.04 / v1.2.04** by switching the profile equality to **operator 4**, which is what
Theme Designer compiles `=` to (`10`). Awaiting a re-run of this same card.

## Registered probe: variant precedence - WRITTEN BEFORE RUNNING, 2026-10-30

The v.04 retest returned **exactly the same four colors as v.03** - profile 1 still red at 0.464 - so
**switching the operator changed nothing, and "operator 129 is dead" was a premature conclusion.** The
operator may never have been the cause.

Three candidates remain, and the earlier test cannot separate them:

| | Hypothesis |
|---|---|
| **a** | **First matching variant wins**, not the last. `04` and `10` both assert last-match-wins and **neither cites evidence**. No shipped feature ever tested it: the six theme toggles and the low-battery bar can only have one variant true at a time, so the replace warning is the first control with two simultaneous matches |
| **b** | **A matching variant with no `Color` paints nothing**, so the earlier red survives. The two cancel variants carry **no Color attribute at all** - `07` #24 claims they set an explicit color, and the built files disagree with the doc |
| **c** | **Operator 4 does not match either** |

### The probe

`PROBE-variants.ecig`, built from v2.2.04 with the same four locked resistances, changes two things:

- **A** - the two ohms cancel variants are given an explicit **white** `(1, 1, 1, 1)`.
- **B** - the session-time field (top right, `60s`) gets a **green** variant on `profile == 4` with
  operator 4 and **no competing variant**, isolating the operator.

### Outcomes, fixed before running

| Profile 1 ohms | Profile 4 session time | Conclusion |
|---|---|---|
| **white** | green | **b** - the missing color was the bug. Ship it: give every cancel layer an explicit color |
| **red** | **green** | **a** - operator 4 works, so precedence is first-match-wins. `04` and `10` are wrong and the warning needs redesigning around it |
| **red** | not green | **c** - operator 4 does not match either. Equality may be unavailable; fall back to a design using only `1`, `2`, `3` |
| white | not green | contradictory - re-run before concluding anything |

Note **b** and **a** are not exclusive in principle, but the probe separates what matters: whether a
later variant can repaint at all.

## Probe 1 result, and Probe 2 registered - 2026-10-30

### Probe 1: operator 4 works; precedence is the problem

| Profile | Ohms | Session time |
|---|---|---|
| 1 DTv5XL | 0.464 **RED** | white |
| 2 QuestCup | 0.450 RED | white |
| 3 DTv5XL-Clean | 0.650 RED | white |
| 4 QuestCup-Clean | 0.314 plain | **45s GREEN** |

The isolated operator-4 variant **fired**, so equality matches and hypothesis **c** is dead. The ohms
cancel variant carried an explicit white this time and **still lost to the red above it**, so **b** is
dead too. That leaves **a: the first matching variant wins, not the last.**

The theme was switched off for this run (confirmed by the operator), so the six theme variants never
matched and cannot explain the result.

**`04` and `10` are therefore both wrong**, and the replace warning was designed on the wrong rule
from the start - which is also why no amount of operator-swapping helped. No shipped feature ever
caught it: the theme toggles and the low-battery bar can only ever have one variant true at a time.

### Probe 2, registered before running

`PROBE2-precedence.ecig`, same four locked profiles.

**A - decide precedence outright.** The session-time field gets two variants that are *both always
true*: **GREEN** if `profile != 0`, then **BLUE** if `cold ohms != 0`.

- **GREEN** -> first match wins. Confirms the reading above.
- **BLUE** -> last match wins, which would contradict Probe 1 and send this back to the start.

**B - the fix.** The ohms chain reordered most-specific-first, which is what first-match-wins
requires:

    default -> red if ohms > 0.6 -> white if profile == 1 -> white if profile == 3
            -> red if ohms > 0.41 -> the six theme colors

Expected, if first-match-wins holds:

| Profile | Locked | First match | Expected |
|---|---|---|---|
| 1 XL | 0.4637 | `profile == 1` | **plain/white** |
| 2 Quest | 0.4504 | `ohms > 0.41` | **RED** |
| 3 XL-Clean | 0.6500 | `ohms > 0.6` | **RED** |
| 4 Quest-Clean | 0.3141 | none | **plain** |

A green session time plus that column is the whole fix verified in one upload. Note the ordering
costs the XL its theme color across its healthy range, the same trade `07` #24 already accepted.

## Probe 2 result and Probe 3 registered - 2026-10-30

### Probe 2: last match wins after all, and I had called it backwards

The session-time field carried two always-true variants, GREEN then BLUE. **Every profile showed
BLUE** - the second one. So **the last matching variant wins**, `04` and `10` were right, and the
"first-match-wins" conclusion drawn from Probe 1 was wrong.

The reordered ohms chain gave RED / RED / RED / plain, which plain last-match-wins explains on its
own: `red > 0.41` still sat *after* the two cancels, so it won.

### The real cause: a per-control child limit

Counting every control in the theme:

| Children | Controls |
|---|---|
| 1 | 108 |
| 2 | 4 |
| 5 | 4 |
| 7 | 27 |
| 8 | 2 |
| **11** | **1 - the ohms readout** |

**The ohms control is the only one in the theme above 8 children.** With a ceiling of 8 (a default
plus seven variants) the v.04 order loses its last three entries:

    1 default | 2-7 six theme colors | 8 red>0.41 | 9 white p==1 X | 10 white p==3 X | 11 red>0.6 X

leaving `red > 0.41` as the only threshold - which is precisely the behavior seen in every run so far,
under both operators. It also explains why changing 129 to 4 made no difference: the variants carrying
those operators were never evaluated.

**The ceiling is inferred, not proven.** 8 is where every other control in this theme happens to stop,
so it is a plausible boundary rather than a measured one. What Probe 3 actually tests is whether the
chain works once the control is small; it does not pin the exact limit.

### Probe 3, registered before running

`PROBE3-fix.ecig`. The six theme tints are dropped from the ohms control, leaving **5 children** in
last-match-wins order:

    default -> red if ohms > 0.41 -> white if profile == 1 -> white if profile == 3 -> red if ohms > 0.6

| Profile | Locked | Last match | Expected |
|---|---|---|---|
| 1 XL | 0.4637 | white `p == 1` | **plain/white** |
| 2 Quest | 0.4504 | `red > 0.41` | **RED** |
| 3 XL-Clean | 0.6500 | `red > 0.6` | **RED** |
| 4 Quest-Clean | 0.3141 | none | **plain** |

### RESULT: plain / RED / RED / plain - exactly as registered

**The design was right all along; the control was simply overfull.** Profile 1 reads white at 0.4637,
the Quest reds at 0.4504, the XL reds at 0.6500, and the Quest-Clean stays plain at 0.3141.

Shipped as **v2.2.05 / v1.2.06**, with all four chains rewritten to five children in last-match-wins
order and explicit white on both cancels. Largest control in either theme is now 8.

The cost either way: that row loses its theme tint, which `07` #24 already accepted.

## High Contrast bench test - registered 2026-10-30

Color Themes is proven. High Contrast's two chains are structurally identical and verify clean on
inspection, but **no HC build has been on the device today**, so this closes the gap rather than
assuming it.

`BENCH-HC-v05.ecig`, same four locked resistances. Read the ohms from **MENU -> Omega OHMS**.

| Profile | Name | Locked | Expected |
|---|---|---|---|
| 1 | XL | 0.4637 | **plain** |
| 2 | QUEST | 0.4504 | **RED** |
| 3 | XL CLEAN | 0.6500 | **RED** |
| 4 | Q CLEAN | 0.3141 | **plain** |

### RESULT: plain / RED / RED / plain - High Contrast passes

| Profile | Locked | Observed |
|---|---|---|
| 1 XL | 0.4637 | plain |
| 2 QUEST | 0.4504 | **RED** |
| 3 XL CLEAN | 0.6500 | **RED** |
| 4 Q CLEAN | 0.3141 | plain |

**Both themes are now proven on hardware.**

**Also confirmed in the same run: the Omega OHMS screen works.** The omega glyph renders from
codepoint 937 at FontStyle 0, the child screen opens from the menu, and LOCKED, the value, the LOCK
toggle, MEASURE and BACK all display. That had been untested since v1.2 (`09`, Untested).

**Correction to the instructions, not the build:** ohms is **not** on the High Contrast home screen -
it lives only on the OHMS page and the new-coil prompt. The test instruction said home screen and was
wrong.

Worth checking in the same pass, both outstanding from the original card: the new-atomizer screen
shows **no `LOCK?` row** until a resistance is committed, and the **Omega OHMS** row opens its child
screen with MEASURE and BACK working.

## Deferred: known simplifications

Things we know are now unnecessarily complicated, held back deliberately so they can be applied in one
pass rather than one reload at a time. Expect this list to grow as the UI, the docs and the HID work
turn up more.

### A better input than raw cold ohms

The source list has **`Atomizer -> Coil -> Cold Ohms @ 70F`** (`15`) - cold ohms normalized to room
temperature. Our thresholds compare raw cold ohms, which moves with how cold the room is, so a cup
measured on a cold morning reads higher and drifts toward the warning for no reason. Worth switching
the replace warning to the normalized field once its ID is captured (`15` item 3b), and re-deriving the
two thresholds against it.

### Collapse the replace warning from five layers to two

The per-cup warning is currently a chain of five flat variants per control that emulates an AND
(`07` #24), built when a real AND appeared not to work. It does work - the failure was operator `129`
for equality where the tool emits `4` (`07` #25). So each of the four resistance displays can become:

```xml
<Compare Operator="64">
  <Compare Operator="2" Field="<ohms field>" RefValue="0.6" />
  <Compare Operator="4" Field="262151" RefValue="1" />
</Compare>
```

plus the same with `0.41` and profile `2`. Two variants, not five.

Three things fall out of it. The **cancel layers disappear**, so the Color Themes home screen keeps its
theme color instead of going white across an XL's healthy range - the compromise accepted on 2026-10-30
stops being necessary. The **cleaning-profile special case disappears** too: profile 3 needed its own
cancel only because the chain could not express "profile 1 **or** 3 **and** over the limit", and `or`
is available. And the intent becomes readable, which the chain never was.

**Do not apply this piecemeal.** It touches all four displays in both themes and needs a hardware test
to confirm operator 4 behaves as the generated file implies - worth doing once, with whatever else has
accumulated.

## Follow-up: a board temperature warning?

**Board Temperature** and **Room Temperature** are both readable measurements (`05`, and Device Monitor
displays them side by side), and both appear by name under `Miscellaneous` in Theme Designer's source
list (`15`) - so a theme can certainly display them. Only the numeric IDs are missing. Raised 2026-10-30: is a hot-board warning worth surfacing in a theme, or
does the chip already protect itself?

Unanswered either way. The DNA almost certainly has its own thermal limits and will throttle or refuse
to fire, but **whether it tells the user anything** is the open question - and if it only shows a status
line, a theme could make it unmissable. Worth checking what the chip does at temperature before building
anything, so the theme is not warning about a condition the firmware has already handled silently.

## Jake's profile settings are now what ships, 2026-10-30

Taken from his own `gremlin_v2.1.ecig` and confirmed against the four `.ecigprofile` files he
supplied, which are the authoritative statement of what he runs.

| | Name | Watts | Temperature | Session | Material |
|---|---|---|---|---|---|
| 1 | DTv5XL | 36 W | 385 F | 120 s | DTv5XL |
| 2 | **Quest** | 25 W | 385 F | 120 s | QuestCup |
| 3 | DTv5XL-Clean | 38 W | power only | 120 s | Watts |
| 4 | **Quest-Clean** | 35 W | power only | 45 s | Watts |

Six values changed in each build: `EvolvPSTemperature[0,1]` 380 -> 385, `EvolvWMTime[0,1]` 60 -> 120,
and `EvolvATFriendlyName[1,3]` to the shorter names. Everything else already matched - watts,
materials, both cleaning profiles, and the DTv5XL curve.

**This reverses the 380 F start shipped in v2.2** (`06`). That was a deliberate change; 385 is what
he actually uses, so the config now agrees with reality.

### Two things deliberately NOT copied

- **His locked cold ohms.** `v2.1` and the two vaping `.ecigprofile` files carry real readings with
  the lock set - 0.4637 @ 69.3 F on the XL, 0.3141 @ 71.2 F on the Quest. Published configs ship 0
  and unlocked (`12`), a baked-in lock is wrong for anyone else's cup, and it goes stale the moment a
  cup is swapped. `tools/` asserts this on build.
- **The Quest TCR curve.** His `Quest.ecigprofile` computes to **TCR 125**; the shipped config is
  **TCR 120**. `02` records 120 as swab-verified on this very DNA100C - *tan at 125, light gold at
  120* - with 125 reading about 5% hot because it is Divine Tribe's figure for their own board. His
  profile file simply predates that test. **Keeping the measured value over the published one -
  confirmed by Jake the same day: "the tcr for the quest should be 120".** The `.ecigprofile` on disk
  is the stale one, not the config; worth regenerating it from the shipped curve so the two agree.

### How the curves compare, since the formats differ

A `.ecigprofile` stores the temperature curve as CSV text (`F,R` then points); a `.ecig` stores the
same curve as `<Curve><Sections>` XML. A string comparison says every curve differs; comparing the
*values* shows only the Quest differs. **Compare decoded points, never the encoded blob.**

### An indexing trap in the same file

`EvolvPSTemperature` and `EvolvWMTime` are indexed **0..7** for profiles 1..8, while `EvolvWDMaterial`,
`EvolvWDColdOhms` and `EvolvWDOhmLock` are indexed **256..263** for the same profiles. Two bases in
one document; `make-bench-config.py` uses the 256 base and is correct for what it touches.

## v3.0 probe 1 result, 2026-10-30: no static route to a PYB

`tools/probe_pyb.py`, run from Device Monitor. Full report:

    === hunting a live PYB ===
    PYB type found: True
    live candidates: 0

**What this rules out and what it does not.** The type exists in `DEScribe.Core`, so the chain in
`16` is real. What came back empty is the *search*, and that search was narrow: it walked **static**
fields and properties whose declared type is `PYB` or `FWB`, in `DEScribe.Core` only. So:

- **Ruled out:** a static field or property that hands you a `PYB` or `FWB` directly.
- **Not ruled out:** a live one held as an **instance** field somewhere - which is the likelier shape.
  `FWB` is the document holder, and a document normally hangs off a form or a view-model, not a
  static. Nothing reaches those from a static-only scan.
- **Not ruled out, and possibly the whole answer:** whether a config was even **open** in EScribe when
  the probe ran. With no document loaded there may be no `PYB` in existence to find.

**`tools/probe_pyb3.py` is the follow-up** and is the one to run next, **with a config open**.

> `probe_pyb2.py` came first and **froze EScribe** - it seeded its walk by reading every static field in
> the assemblies, which runs every type initializer (`07` #28). Stopped manually, nothing reached the mod,
> script deleted. Probe 3 walks only from objects that already exist, so no initializer can fire, and it
> is interruptible with a 20-second budget. It
walks instance fields outward from `Application.OpenForms`, bounded by a node cap, a depth cap, a
visited set and a wall-clock budget, and honours Device Monitor's Stop button.
It also prints the open forms, so the report says whether a document was loaded - which makes an
empty result interpretable instead of ambiguous.

One safety change worth noting: probe 2 reads **fields only, never properties.** A property getter can
run arbitrary code; a field read cannot. Probe 1 read static properties, which was a small risk when
the search was narrow and not one worth carrying into a wide walk.

### Probe 3, run 1 - blind, not negative

    === roots ===
      could not enumerate forms: No module named Forms
      global ECig / Device / Directories / UI / Script
    objects visited: 277   finished the graph
    === live PYB / FWB found: 0 ===

**Device Monitor's IronPython host does not reference `System.Windows.Forms`.** So the probe never
reached the form tree - the one place a document is actually likely to live - and walked only five
shallow globals. 277 objects and the graph exhausted says those globals go nowhere, not that no `PYB`
exists.

Fixed in place: the probe now `clr.AddReference`s WinForms before enumerating (falling back to
`AddReferenceByPartialName`), prints the full type of every root, and says explicitly if
`OpenForms` comes back **empty** - which would mean the script host does not share EScribe's UI
thread, and would itself be the finding. **A second empty result will mean something; the first one
did not.**

### Probe 3, run 2 - the real finding: the script host cannot see EScribe's document

With WinForms loaded, `Application.OpenForms` contains **exactly one form: Device Monitor's own
window.** The main EScribe window is not there, so neither is the open document. 296 objects, graph
exhausted, zero hits - and this time that means something.

Also learned: `ECig` and `Device` are the *same* object (`A.OJA`), i.e. the device interface, not a
document; `Directories`, `UI` and `Script` are small host helpers (`A.ARO`, `A.JRO`, `A.SDO`). None
of them leads anywhere near a `PYB`.

**So three probes have now failed to find a live `PYB`, and the third explains why hunting harder
will not help.** The document is simply not reachable from the script host.

> **Privacy note, and a bug in our own tooling:** EScribe puts the **device serial in the window
> title** - `Device Monitor - <theme> - <serial>`. Probe 3 printed form titles verbatim, so pasting a
> report into this repo would have leaked it (`12`). Fixed: the probe prints the form's type name
> only. Worth remembering for anything else that enumerates windows.

### The pivot: build a PYB instead of finding one

`16` mapped `.ecig root -> GGQ -> DWB.JSL(?, ggq, null) -> PYB -> PYB.UE(f, i) -> OCC` and called it
blocked because **`DWB` is abstract**. But nobody has looked for a **concrete subclass**. If one
exists, a `PYB` can be built from one of our own `.ecig` files and the live document stops mattering
entirely - which also means the whole thing works without a document open.

`tools/probe_dwb.py` asks exactly that, and reads **metadata only** - `BaseType`, `IsAbstract`,
`GetConstructors`, `GetParameters`. It never reads a value and never invokes anything, so no static
constructor can fire (`07` #28). It also reports whether `DEScribe.UI` is even loaded in the script
host, which confirms or kills the separate-context theory outright.

## The roadmap, and what each version means

Set by Jake 2026-10-30. The point of the device-access work is not the protocol; it is these two
releases, and everything in `16` and `17` is in service of them.

| Version | Ships when | State |
|---|---|---|
| **v2.3** | the theme is right **and the new-atomizer screen works** | theme done and proven; new-coil prompt is the remaining gate |
| **v3.0** | **Claude can push edits straight to the device** | blocked on one thing, below |
| **v4.0** | **Bluetooth** | not started; needs v3.0's work first |

### v3.0 - direct device push

This is the one that changes how the project is worked on. Today every change is: build a file, hand
it over, upload it by hand in EScribe, photograph the screen. With a push, the loop closes.

**Reading and driving the mod is already solved** - `tools/dna-hid.py` talks to the board over the
vendor HID interface with no EScribe, no COM port and no driver install (`16`, `17`).

**Writing a config is not**, and the blocker is specific and known. The chain is

    .ecig root -> GGQ -> DWB.JSL(?, ggq, null) -> PYB -> PYB.UE(func, int) -> Programmer

and it stops at **obtaining a live `PYB`**: `DWB` is abstract, so it cannot be constructed out of
process, and the flash layout is **derived per config from feature IDs** rather than declared per
board - which is exactly why a layout must not be hand-built (`16`). Writing to a guessed offset is
writing to live flash at an address nobody verified.

**The next action is one script.** `tools/probe_pyb.py` is inert and ready: run it from EScribe's
Device Monitor -> Diagnostics -> Advanced -> Run Script. It walks EScribe's own statics for a live
`PYB` or `FWB` and dumps `PE()` - the real region sizes, offsets, paging and read-only flags. **One
report settles whether this route is viable.** If it is not, the fallback is a USB capture of a real
upload; the device-to-PC half is already decoded (`16`, `tools/samples/hid-upload-capture.log`) and
only the PC-to-device direction is missing.

The safety gates to preserve are inventoried in `16` - pre-upload backup, device identity check,
firmware handshake, per-frame CRC, differential hashing, the write transaction, and the `dontUpload`
dry run. Calling Evolv's own uploader keeps all of them by construction, which is the whole reason
that route was chosen over reimplementing the protocol.

### v4.0 - Bluetooth

**A USB-C Bluetooth dongle plugged into the mod will not work.** The DNA's USB is a *device* port;
its OTG support is for power-bank output, not for acting as a host, so the board cannot enumerate a
dongle and nothing in firmware would see it.

What works is a **bridge**: a small board that is a USB host on one side and BLE on the other -
ESP32-S3 or nRF52840 both qualify - which plugs into the mod, speaks the HID framing from `16`, and
exposes BLE to a phone.

Most of the hard part is already done: the framing (`01 | DE | len | payload`), the command table
(`17`) and the report geometry (63 in, 63 out) are all known, so the bridge is largely transcription.

**Scope it before buying anything.** Open questions: whether the mod supplies enough current to run
the bridge or it must carry its own power; whether a bridge can hold the link while the mod is in
use; and whether the settings-transfer protocol matters for a first version, or whether read-and-
control is enough to be useful on its own. Likely it is - a phone showing live ohms, puff count and
board temperature needs nothing further. **Do this last.** It is the only piece needing hardware that
is not already on the bench.

### Not versioned: a phone app that designs the UI on a touchscreen

Jake's other stated goal, and **the most tractable piece - it needs no device work at all.** A theme
is XML this repo has fully mapped: screens, controls, conditions, fonts, field IDs (`04`, `05`, `10`,
`15`, `18`). An app that drags controls on a phone-sized canvas and emits a `.ecigtheme` can be built
and tested against EScribe's own Theme Installer long before any new transport exists. Pushing the
result is a separate problem, solved by whichever of v3.0 or v4.0 lands first.

## Ideas
- ~~**User toggles** as a new discovery.~~ **We already use them.** The six Color Themes are exactly
  this: fields `10`, `266`, `778`, `1034`, `1290`, `1546`, each tested with `Operator="1"` against 0.
  So `User -> Toggle N` is the mechanism behind THEMES, it is proven on-device, and the Language tab's
  `Toggles` section is where their `On:`/`Off:` text comes from (`15`). What remains open is only
  whether any **unused** toggles are free for a new feature.
- **A puff graph on the mod.** The `Chart` control draws the device's own puff recording and takes one
  setting, `Time Bars` (`15`). `Recordings -> Chart Present` (`05`) is the condition for hiding it when
  empty. 64x64 fits an 80x160 screen. Nothing in either theme uses this, and it would put the heat
  curve we verified over serial (`02`) on the device itself.
- **More color themes:** off-board memory is the limit (93.6% on the DNA75C). Free image space first, e.g. let more themes use the standard gremlin.
- **Full menu coloring** for one or two themes would fit in on-board memory (56%).
- ~~An "at temperature" indicator via a math condition comparing live vs set temperature.~~ **Not possible in a theme. Settled twice over, 2026-10-30.** I withdrew the second block below on seeing that conditions are authored as expressions, then tested it: Theme Designer **rejects** `Atomizer -> Temperature > Miscellaneous -> Board Temperature` with *"Invalid Value - Must be a number!"*. The right-hand side of a comparison must be a literal, so the original finding was right and the withdrawal was wrong. Both blocks stand, and the measurement list confirms the first independently - there is one atomizer temperature and no separate live reading. The three blocks, as recorded: the setpoint and the live temperature are the *same* field (16778242 — live is that field with `UpdateLive` + `ReadOnly` while firing), so no condition can tell "how hot it is" from "what was asked for"; `<Compare>` only tests a field against a literal `RefValue` baked into the theme, so "live ≥ set" cannot be expressed; and the firmware's own flag, Heating Time Done (353173506), is rejected on upload (`07` #1). A hardcoded threshold is possible but lies as soon as the setpoint moves off it. Unexplored: the chip throttles power once it reaches temperature, so `profile == N` AND `watts < X` might approximate it, at the cost of per-profile constants.
- Larger temperature in the High Contrast theme would need a bigger custom font and layout rework (`11`).
