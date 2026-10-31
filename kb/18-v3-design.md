# 18 – Gremlin v3 design

Written 2026-10-30, after the structural audit of `v2.2.05` (`09`) and the operator-64 result (`09`,
`10`). **Nothing here is built yet.** This is the spec; `06` stays the record of what shipped.

## Why there is a v3 at all

`v2` works. Both replace-warning chains are proven on hardware and the themes look right. But the
audit found that **the way v2 is built is one theme away from breaking silently**, and the operator
result means the hardest part of it no longer needs to be built that way.

Two facts set the whole design:

1. **A control holds at most ~8 children and drops the rest without a word** (`07` #26). Six of those
   slots go to theme tinting on 27 controls, leaving **one**.
2. **Operators 64 (AND) and 65 (OR) work** (`09`, confirmed on a four-profile truth table). The
   five-layer cancel chains that exist only to emulate an AND are no longer necessary.

## The two principles

### 1. ~~Cosmetic and functional variants never share a control~~ — WRONG, withdrawn 2026-10-30

This was the centrepiece of the v3 design and **hardware refuted it twice in one sitting.**

The idea was that a warning has to be the *last* matching variant to beat a tint, so every warning on
a tinted control sits on the ceiling by construction - and the fix was to split it onto its own
control over the same rectangle, ordered by `ZOrder`. Shipped as `v2.3.00` for the battery meter.

**What actually happens:** the overlay draws on the first paint and is then painted over. The meters
beneath it are bound to the live battery level, so they repaint; the static overlay above them is
never re-dirtied, so it is never redrawn (`09`).

And the premise was false anyway. **Child 8 is evaluated** - the single-control design was working
the whole time, and `v2.3.00` is withdrawn as a regression.

> **The rule that replaces it: keep every control at 8 children or fewer, and put conditions in the
> same control as the tints.**
>
> A control that repaints re-evaluates its whole variant list and re-picks its winning child every
> frame, which is exactly what makes the single-control design correct on a live readout. Splitting
> is not a tool for getting around the ceiling; the ceiling is a hard budget, and the only way to
> spend less of it is to write fewer variants - which is what principle 2 is for.
>
> An overlay *can* work if it carries its own live source and is re-dirtied alongside the control
> beneath it (the lock-screen `Meter` did render). That is a curiosity, not a technique: it is more
> fragile than the thing it replaces.

### 2. Conditions are written as conditions

With `AND` and `OR` available, intent goes in the file instead of in a chain whose meaning has to be
reconstructed by simulating it. Every layered-cancel construction in `v2` is a workaround for a tool
limitation that turned out not to exist.

## Changes, in the order they should be built

### A. ~~Split the battery meter~~ — WITHDRAWN. It was never broken

Shipped as `v2.3.00`, found to flash and vanish, then found to have been fixing nothing: child 8 is
evaluated and the LOW BATTERY banner has always rendered (`09`). Build files removed, `v2.2.05`
restored as the release. The only durable output is `tools/check-theme.py` and a measured ceiling.

### B. Rewrite the replace warning as real conditions

Four controls, both themes. The current five-layer chain becomes **three flat variants, all at nesting
depth 2, every operator confirmed on-device**:

```xml
<Field … />                                                  <!-- 1. default -->
<Field … Color="(1, 0.24, 0.16, 1)">                         <!-- 2. anything over 0.6 -->
  <Compare Operator="2" Field="<ohms>" RefValue="0.6" />
</Field>
<Field … Color="(1, 0.24, 0.16, 1)">                         <!-- 3. Quest over 0.41 -->
  <Compare Operator="64">
    <Compare Operator="2" Field="<ohms>" RefValue="0.41" />
    <Compare Operator="4" Field="262151" RefValue="2" />
  </Compare>
</Field>
<Field … Color="(1, 0.24, 0.16, 1)">                         <!-- 4. Quest-Clean over 0.41 -->
  <Compare Operator="64">
    <Compare Operator="2" Field="<ohms>" RefValue="0.41" />
    <Compare Operator="4" Field="262151" RefValue="4" />
  </Compare>
</Field>
```

The trick that removes a whole layer: **anything above 0.6 is red on every profile**, because 0.6 is
already past the Quest's own 0.41 limit. So the XL needs no rule of its own and the two cancel layers
disappear with it.

Four children instead of five, and - more to the point - **no cancels, no cleaning-profile special
case, and the intent is legible**. `09`'s deferred "collapse to two layers" item is superseded by this.

### C. The one question that decides the theme tint — REOPENED, and now worth testing

At four children the ohms row cannot carry the six tints (4 + 6 = 10, over the ceiling), so it **keeps
reading white** - the compromise `07` #24 accepted.

**Since 8 is now confirmed to render, `1 default + 6 tints + 1 variant = 8` is viable.** An earlier
draft called this dead on the grounds that 8 was the untrusted ceiling; it is no longer untrusted.
So the tint can come back **if the whole warning collapses to a single variant**:

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

That is **nesting depth 4, and only depth 2 is proven.** One probe settles it, built like the
operator-64 probe: its own small control, a flat positive control beside it, registered first.
**Fallback if deep nesting fails:** drop one tint from that control and use two variants at depth 2,
so one theme loses its ohms tint instead of all six.

### D. Make the ceiling mechanical, not remembered  ✅ DONE - `tools/check-theme.py`

Both bugs this project has had were invisible on inspection. The build should refuse to ship them:

- **fail** if any control exceeds **8** children - over the inferred ceiling;
- **fail** if a control mixes tint variants with conditions, which is principle 1 as a check;
- **fail** if a condition sits in a slot past the 7th, where one more theme would drop it;
- **warn** at exactly 8 children, meaning no headroom left.

The thresholds moved while building it. An earlier draft of this section said *fail over 7, warn at
7*, which would have warned on **27 controls every single build** - all of them default-plus-six-tints,
all of them safe and deliberate. A check that cries wolf 27 times gets ignored, so the rule keys on
the thing that is actually dangerous: a *condition* near the ceiling, or tints and conditions sharing
a control. The 27 tint-only controls are silent.

Still worth adding later: a **cross-file consistency check** between the `.ecigtheme` and the `.ecig`.
They have diverged before - EScribe zeroed four `RefValue`s in one and not the other - and nothing
currently catches it.

Add to the verifier in `08`. This is the cheapest item here and prevents the recurrence of both #26
and the battery-meter defect.

### E. Normalized cold ohms

The source list offers **`Atomizer -> Coil -> Cold Ohms @ 70F`** (`15`) - resistance corrected to room
temperature. The thresholds currently compare raw cold ohms, so a cup measured on a cold morning reads
high and drifts toward a warning for no reason. Capture the field ID from Theme Designer, re-derive
both limits against it (`02`), and switch all four controls. Carried over from `09`'s deferred list.

### F. Fix or drop the live-ohms row

Session screen `(16, 104)` shows field **1048642**, which `05` records as *reads 0 when idle after boot
and 0 during the first session after power-on* (`09`, audit). Either guard it - now expressible as
`AND(not firing, value != 0)` - or give the space to something honest.

## Deliberately not in v3

- **New screens.** The puff `Chart`, Power Lock (`Usage=4`) and Theme Change (`Usage=5`) are all
  available and none has been attempted (`09`). They are additions, and v3 is about making the
  foundation safe; mixing the two makes a regression impossible to attribute.
- **A seventh color theme.** Off-board memory is at 93.6% (`06`) and images are the constraint. v3
  makes a seventh theme *safe* to add, which is the prerequisite, not the thing itself.
- **Anything needing the normalized-ohms field ID** until that ID is actually captured. E depends on
  it and should not be guessed.

## Order of work

| | Item | Needs hardware? |
|---|---|---|
| 1 | **C** - the text-over-text overlay probe | yes, one upload |
| 2 | **A** - split the battery meter | builds blind, test with the rest |
| 3 | **B** - rewrite the four warning chains (shape depends on 1) | |
| 4 | **D** - the build-time child check | no |
| 5 | **E** / **F** - normalized ohms, the live-ohms row | E needs the field ID first |
| 6 | one bench pass over everything, both themes | yes |

Note **A and D together close the audit's live defect and stop it recurring**, and neither depends on
the probe - so if the overlay answer is slow in coming, they are not blocked by it.
