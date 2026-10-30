# 09 – Open Items

## Where this effort stands

Written 2026-10-30 so the thread survives a context loss. **23 commits sit local and unpushed** - nothing
in this stretch has gone to GitHub, by instruction.

**Current builds:** Color Themes `v2.2.03`, High Contrast `v1.2.03`, both internal mini versions (`00`).
Neither has been tested on hardware since the per-cup replace warning was rebuilt as a layered chain.

**Three threads are open at once:**

1. **The replace warning** works in principle but its layered implementation is a workaround for an AND we
   could not encode. Item 1 of the checklist in `15` would replace it with a single condition.
2. **Theme Designer mapping** (`15`) is part done - Appearance and Screens tabs, and the condition editor.
   The checklist there says what is left.
3. **Programmatic device access** (`16`) is scoped but not working. EScribe's .NET assemblies load and
   reflect, and `CreateForDNAColor()` returns the live device link; what is missing is how the stream is
   opened and which member reads settings out. The serial fallback has a listen-only probe written and
   never run.

**The most valuable single action** is item 1 of the `15` checklist: one save in the GUI settles how
conditions are really encoded, and several things in this repo are built around not knowing that.

## Tracked: the new-atomizer screen

Reworked repeatedly on 2026-10-30 and **never tested as it now stands**. Both themes changed; load
`gremlin_v2.2.03.ecig` and `gremlin_high_contrast_v1.2.03.ecig`, and remember a full `.ecig` load
zeroes cold ohms, so a cup has to be re-locked before anything resistance-driven can show.

What is unverified, in the order a single swap would exercise it:

1. **The LOCK? row is hidden until there is something to lock.** Guarded on cold ohms being non-zero,
   so on a fresh config it should be absent. Seen working once against the *earlier* guard, which
   watched the pending reading instead (`07` #22).
2. **Does the row appear after YES, and does the prompt stay open long enough to use it?** If
   `NewCoilAccept` dismisses the screen, the first lock has to happen on the ohms page or PROFILE
   instead, and the toggle on the prompt only helps on later swaps. This is the open question that
   decides whether the control earns its place.
3. **High Contrast shows the measured resistance** on that screen now, and MEASURE was removed to fit
   it (`11`). Never seen on hardware.
4. **The red replace warning** on the prompt and on the ohms page, rebuilt as a layered chain. The
   chain's logic is worked through but the layering itself has not run on the mod.

A cheap way to exercise 4 without aging a cup: Device Monitor can **write** cold ohms (`14`), so set it
past a threshold and watch the screen. That tests the layering far faster than swapping cups.

## Tracked: programmatic device access

Scoped in `16`, not working yet. The goal is reading and writing the mod from a command line so a change
can be uploaded and checked without the GUI in the loop.

**HID is the target** - it is how every config this project has shipped reached the mod. Next steps, in
order:

1. Find how the device **stream** is opened and handed to the programmer object. Likely an enumeration
   API in `DEScribe.Core` or `DimensionEngineering.Common`, neither of which reflects cleanly yet.
2. Work out how to construct the `NHW` cache argument that `CreateForDNAColor()` wants.
3. Identify the **read** path. `AX(IProgressMonitor, bool[])` is the candidate.
4. Only then consider a write - dry-run flag first, with a known-good backup to hand.

If obfuscation makes that too slow, **USB capture** of EScribe doing a real transfer gives the protocol
exactly and cannot fail; it just needs USBPcap or similar installed.

**The serial port is the fallback** (`13`, `16`). A listen-only probe is written and has never been run -
it needs the mod plugged in, writes nothing, and would tell us whether that port is a text console at
all. Cheap, and worth doing next time the mod is connected.

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
- **High Contrast Ω / OHMS screen** (v1.2). The menu's ohms row and the child screen behind it have not been exercised on hardware: whether the `Ω` label renders from codepoint 937 at FontStyle 0, whether `ChildScreen Screen="4"` reaches the new screen, and whether `ResampleOhms` works from a child screen (the color theme calls it from PROFILE, so it should).
- **Theme Designer has a `Screenshot` button** on the Screens tab (`15`), which should render a screen straight to an image. That is very likely the fix for the stale screenshots below, without photographing the mod. Untried.
- **Power Lock (`Usage=4`) and Theme Change (`Usage=5`) screens** exist and we have never built either (`15`). Theme Change is the interesting one for Color Themes, where switching looks is the whole feature.
- **High Contrast screenshots are stale.** `../high-contrast/images/menu-screen.png` and `new-coil-screen.png` predate the ohms row; there is no screenshot of the OHMS screen yet.
- Whether every chip warning (e.g., "Temp Protected") appears in the status line.

- **Replace-the-cup color warning** (both themes, 2026-10-30). Two things unverified: `<Compare Operator="2">` (greater-than) is listed **H**, not confirmed, and this is its first use in either theme — if it does not resolve, the number simply never turns red; and the thresholds rest on a **single** observed failure (0.43 → 0.61Ω), scaled to the Quest by ratio rather than measured. Limits and derivation in `02`.

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

## Ideas
- **More color themes:** off-board memory is the limit (93.6% on the DNA75C). Free image space first, e.g. let more themes use the standard gremlin.
- **Full menu coloring** for one or two themes would fit in on-board memory (56%).
- ~~An "at temperature" indicator via a math condition comparing live vs set temperature.~~ **Blocked by the field inventory, not by the condition system (revised 2026-10-30).** Theme Designer's measurement list has exactly one atomizer temperature and no separate live reading, which confirms the first block below. The second block is **withdrawn**: conditions are authored as expressions and can combine measurements, so comparing two fields is not inherently impossible (`15`). The original three blocks, as recorded: the setpoint and the live temperature are the *same* field (16778242 — live is that field with `UpdateLive` + `ReadOnly` while firing), so no condition can tell "how hot it is" from "what was asked for"; `<Compare>` only tests a field against a literal `RefValue` baked into the theme, so "live ≥ set" cannot be expressed; and the firmware's own flag, Heating Time Done (353173506), is rejected on upload (`07` #1). A hardcoded threshold is possible but lies as soon as the setpoint moves off it. Unexplored: the chip throttles power once it reaches temperature, so `profile == N` AND `watts < X` might approximate it, at the cost of per-profile constants.
- Larger temperature in the High Contrast theme would need a bigger custom font and layout rework (`11`).
