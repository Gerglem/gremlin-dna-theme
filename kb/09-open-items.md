# 09 – Open Items

## Where this effort stands

Updated 2026-10-30, late in a long session. **41 commits are local and unpushed**, by instruction.
Nothing in this stretch has gone to GitHub.

**Builds:** Color Themes `v2.2.04`, High Contrast `v1.2.04`. **The replace warning was tested 2026-10-30 and operator 129 failed; .04 is the fix, retest pending**
since the replace warning was rebuilt. That is the gate on pushing anything.

**Solved today, and large:** the mod is a plain-text command console over its USB serial port (`17`),
with `tools/dna-query.ps1` and `tools/dna-stream.ps1` working. The TCR curve is now **verified against
the hardware** to 0.04 F (`02`). Settings and themes are confirmed unreachable over serial - encrypted
binary, EScribe only (`16`), so the HID effort is only worth resuming for *writing* a config.

**Device state:** on COM4. Serial Output Format was switched to CSV for the stream test and **switched
back to Plain Text Serial**, so the query tool works as-is. The cup is locked at 0.464 ohm.

**Theme Designer mapping** (`15`) is most of the way done: Appearance, Screens, the condition editor,
Memo, Chart and most of Field. The checklist there says exactly where to resume - Field's Source
`Options` and `Type...` dialogs.

**The one correction worth remembering:** conditions are authored as expressions and compiled to the
`<Compare>` XML we hand-write. Operator 64 *is* AND; the bug was using 129 for equality where the tool
emits 4 (`07` #25). Several things in this repo are built around the wrong belief and are listed under
deferred simplifications below.

## Tracked: the new-atomizer screen

Reworked repeatedly on 2026-10-30 and **never tested as it now stands**. Both themes changed; load
`gremlin_v2.2.04.ecig` and `gremlin_high_contrast_v1.2.04.ecig`, and remember a full `.ecig` load
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

## Registered test card: v2.2.03 / v1.2.03 - WRITTEN BEFORE RUNNING, 2026-10-30

Neither build has been on hardware since the replace warning was rebuilt as layered flat variants.
This is the gate on pushing. Designed first, outcomes fixed before the run, per the rule that a verdict
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

### Result - RUN 2026-10-30: operator 129 is dead

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

    1 default | 2-7 six theme colours | 8 red>0.41 | 9 white p==1 X | 10 white p==3 X | 11 red>0.6 X

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

- **plain / RED / RED / plain** - the design works and the ceiling was the whole problem. Ship it, and
  record that a control may not exceed 8 children.
- **Profile 1 still RED** - the ceiling is not the cause either, and the layered-cancel approach
  should be abandoned for something that needs no two simultaneous matches.

The cost either way: that row loses its theme tint, which `07` #24 already accepted.

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

## Tracked: bring the device up to 2026 standards

Jake's stated goal for the whole device-access effort, recorded 2026-10-30 so the pieces are not
mistaken for ends in themselves.

### 1. A phone app that designs the UI on a touchscreen

**The most tractable piece, and it needs no device work at all.** A theme is XML this repo has fully
mapped - screens, controls, conditions, fonts, field IDs (`04`, `10`, `15`). An app that drags
controls on a phone-sized canvas and emits a `.ecigtheme` can be built and tested against EScribe's
own Theme Installer long before any new transport exists. Pushing the result is a separate problem,
solved by whichever transport is ready first.

### 2. Programmatic push

In progress, `16`. Read and control are solved over HID; writing a config is not.

### 3. Bluetooth - a bridge, not a dongle

**A USB-C Bluetooth dongle plugged into the mod will not work.** The DNA's USB is a *device* port; its
OTG support is for power-bank output, not for acting as a USB host, so the board cannot enumerate a
dongle and nothing in firmware would see it.

What works is a **bridge**: a small board that is a USB host on one side and BLE on the other -
ESP32-S3 or nRF52840 both qualify - which plugs into the mod, speaks the HID framing from `16`, and
exposes BLE to a phone.

Most of the hard part is already done: the framing (`01 | DE | len | payload`), the command table
(`17`) and the report geometry (63 in, 63 out) are all known. The bridge is largely transcription.

**Scope it properly before buying anything.** Open questions: whether the mod supplies enough current
to run the bridge or the bridge must carry its own power; whether a bridge can hold the link while the
mod is in use; and whether the settings-transfer protocol (`16`, unsolved) matters for a first version
or whether read-and-control is enough to be useful on its own. Likely it is - a phone that shows live
ohms, puff count and board temperature needs nothing further.

Do this one last. It is the only piece needing hardware that is not already on the bench.

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
