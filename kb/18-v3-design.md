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

### 1. Cosmetic and functional variants never share a control

This is the real lesson of both bugs this project has had. A warning has to be the **last** matching
variant to beat a tint, and last is exactly where truncation happens - so every warning on a tinted
control sits on the ceiling by construction.

> **Rule: a control carries tints, or it carries conditions. Not both.**
> Where both are wanted, split them into two controls over the same rectangle, ordered by `ZOrder`,
> and keep each one small.

The payoff is that **adding a seventh color theme can never again silently kill a warning** - the
failure mode that is currently live on the battery meter.

### 2. Conditions are written as conditions

With `AND` and `OR` available, intent goes in the file instead of in a chain whose meaning has to be
reconstructed by simulating it. Every layered-cancel construction in `v2` is a workaround for a tool
limitation that turned out not to exist.

## Changes, in the order they should be built

### A. Split the battery meter — fixes a live defect

The only functional variant above position 5 in the whole theme is the low-battery red, at **child 8
of 8** on both the home and session screens (`09`, audit). In `v1.0` it was child 2 of 2.

Leave the seven tint `Meter`s where they are. Move the red `Picture` to its own control over the same
rect at the next `ZOrder`, with a default `<Hidden/>` ahead of it:

```xml
<Control Location="(0, 0)" Size="(80, 7)" ZOrder="1">   <!-- unchanged: default + 6 tints -->
<Control Location="(0, 0)" Size="(80, 7)" ZOrder="2">
  <Hidden />
  <Picture …><Compare Operator="3" Field="65537" RefValue="15" /></Picture>
</Control>
```

Two children, **no new images** - the child is already a `Picture`. Largest control in the theme drops
from 8 to 7. Do this one first; it is the only change that fixes something currently broken-or-nearly.

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

### C. The one question that decides the theme tint

At four children the ohms row still cannot carry the six tints (4 + 6 = 10, over the ceiling), so it
**keeps reading white** - the compromise `07` #24 accepted.

Getting the tint back needs the warning down to **one** variant, which means folding the two Quest
rules together with an `OR` inside the `AND`:

```xml
<Compare Operator="64">
  <Compare Operator="2" Field="<ohms>" RefValue="0.41" />
  <Compare Operator="65">
    <Compare Operator="4" Field="262151" RefValue="2" />
    <Compare Operator="4" Field="262151" RefValue="4" />
  </Compare>
</Compare>
```

That is **nesting depth 3, and only depth 2 is proven.** One probe settles it, built the same way as
the operator-64 probe - its own 2-child control, a flat positive control alongside, registered before
running. **Worth doing before B is cut**, because the answer changes B from four children to two and
decides whether that row is tinted.

### D. Make the ceiling mechanical, not remembered

Both bugs this project has had were invisible on inspection. The build should refuse to ship them:

- **fail** the build if any control exceeds **7** children,
- **warn** at exactly 7,
- **fail** if a control mixes tint variants with non-tint conditions, which is principle 1 as a check.

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
| 1 | **C** - the depth-3 nesting probe | yes, one upload |
| 2 | **A** - split the battery meter | builds blind, test with the rest |
| 3 | **B** - rewrite the four warning chains (shape depends on 1) | |
| 4 | **D** - the build-time child check | no |
| 5 | **E** / **F** - normalized ohms, the live-ohms row | E needs the field ID first |
| 6 | one bench pass over everything, both themes | yes |

Note **A and D together close the audit's live defect and stop it recurring**, and neither depends on
the probe - so if the depth-3 answer is slow in coming, they are not blocked by it.
