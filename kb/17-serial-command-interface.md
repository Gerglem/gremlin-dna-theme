# 17 – The plain-text serial command interface

**The mod is a command console.** It answers plain-text commands over its USB serial port, with no EScribe involved — read resistance, temperatures, statistics and the active material, and drive the device directly. This is the scriptable control `16` set out to find, and it needs no reverse engineering: Evolv documented it.

Everything in the **Verified** table was run against this DNA 100 Color, firmware SP55.1 INT, on 2026-10-30.

---

## Connecting

The mod is a USB composite device (`13`); its second interface is a standard CDC serial port — COM4 here, on Microsoft's stock `usbser` driver. **9600 8-N-1**, assert **DTR and RTS**, terminate with **CRLF**. Replies come back CRLF-terminated.

No driver needed on Linux or a Raspberry Pi; the port is standards-compliant CDC. Evolv ships a custom Windows driver with EScribe and says Microsoft's is "of poor quality" — **this machine is using Microsoft's and it works**, but if the link ever misbehaves, that is the first thing to change.

```powershell
$sp = New-Object System.IO.Ports.SerialPort 'COM4',9600,'None',8,'One'
$sp.DtrEnable = $true; $sp.RtsEnable = $true; $sp.ReadTimeout = 400
$sp.Open(); $sp.Write("R=GET COLD`r`n"); Start-Sleep -Milliseconds 350
$sp.ReadExisting()          # -> R=0.464OHM
$sp.Close()
```

`tools/dna-query.ps1` wraps this, sends a standard read-out by default, and refuses anything that is not `LETTER=GET` unless `-AllowWrites` is passed.

## Syntax and two traps

`LETTER=ACTION`; the reply echoes the letter. `#` is a decimal number with a period separator.

**`LETTER=?` in a reply means the board has no value** — not an error. `P=GET` returns `P=?` when idle because there is no live power.

> **Trap 1: an unrecognised command gets no reply at all.** `?`, `help` and `dir` were sent to this port and returned nothing, which read as a dead channel for most of a day. The port was fine; those are not commands (`07` #26).

> **Trap 2: `T=?` is not a query — it turns temperature protection OFF.** The one command that looks like a question and is actually a write. `tools/dna-query.ps1` refuses it, since it does not match `LETTER=GET`.

---

## Verified on this board

### Identity and capabilities

| Command | Reply |
|---|---|
| `E=GET MFR` | `E=Evolv` |
| `E=GET PRODUCT` | `E=DNA 100 Color` |
| `E=GET VERSION` | `E=311105588` — the user-mode version EScribe's debug log prints |
| `E=GET SERIAL` | *(device serial — keep out of this repo, `12`)* |

`E=GET FEATURE <n>`, counting up until `E=?`, enumerates what the board supports. This one answers **14**:

```
1 PC      power control          8  TC:M     temperature control, materials
2 St      long-term statistics   9  TC:M:H   ... with heating
3 L                              10 St:TP    temp-protected puff stats
4 NS                             11 PH       preheat
5 TM                             12 EC:V
6 DN                             13 W        clock
7 TC      temperature control    14 M        profiles
```

`L`, `NS`, `TM`, `DN` and `EC:V` are undocumented by the community list; meanings unknown.

### The ones that matter here

| Command | Reply | Why it matters |
|---|---|---|
| **`R=GET`** / `R=GET COLD` | `R=0.464OHM` | **The locked cold resistance** — the value the replace warning keys on (`02`) |
| **`T=GET MATERIAL`** | `T=DTv5XL` | **The active material by name.** Confirms which TCR curve is live, which nothing else exposes without reading the config |
| **`T=GET COLD`** | `T=69.28F` | The temperature cold ohms was measured at — matches `ColdResistance2 Fahrenheit` in the saved profile exactly |
| **`M=GET`** | `M=1` | Active profile, **1-based** — independently confirms the numbering every per-cup condition relies on (`05`) |
| `R=GET STATIC` | `R=0.004OHM` | Fixed contact resistance |
| `R=GET GROUND` | `R=0.000OHM` | |
| `T=GET SP` / `P=GET SP` | `T=385.00F` / `P=36.00W` | Setpoints |
| `T=GET BOARD` / `T=GET ROOM` | `T=82.93F` / `T=74.76F` | Answers the readability half of the board-temperature question (`09`) |
| `V=GET SP` / `I=GET SP` | `V=9.000V` / `I=30.000A` | Limits |
| `B=GET` / `B=GET CELLS` / `C=GET%` | `B=4.157V` / `B=1` / `C=98%` | Battery |
| `U=GETV` / `U=GETI` / `U=GETP` | `U=5.122V` / `U=0.009A` / `U=0.042W` | USB. **No space** after `GET` |
| `I=GET OFFSET` | `I=0.104A` | |
| `X=GET SCRNDISC` | `X=80` | Screen width in pixels |
| `X=GET TIMER` | `X=4979.88S` | Uptime |
| `W=GET` | `W=2026-10-30,21:31:53,2026-10-30,14:31:53,00010,UP` | UTC, local, flags |

Live-only, so `?` while idle: `P=GET`, `T=GET`, `V=GET`, `I=GET`, `R=GET LIVE`, `C=GET`, `X=GET METER`, `V=GET DEVICE`.

No reply at all on this board: `E=GET HARDWARE`, `R=GET RAW`, `R=GET NOMINAL`, `R=GET NOMINAL TEMP`, `R=GET SAMPLE TIME`, `T=GET AIR`, `T=GET NOMINAL ROOM`, `P=GET SAMPLE`, `X=GET BANDGAP`.

### Statistics have a grammar

`S=GET [when] [what] THING`, where **when** is `DEVICE` (lifetime), `LAST` (previous puff) or blank (since reset), and **what** is `MEAN`, `SD` or blank (total). `MEAN` and `SD` cannot combine with `LAST`. Things: `ENERGY`, `POWER`, `TEMP`, `PEAK TEMP`, `TIME`, `PUFFS`, `TEMP PUFFS`, plus `S=GET RESETS`.

On DNA Color the standard deviation divides by N; on earlier boards by N−1.

| Command | Reply |
|---|---|
| `S=GET PUFFS` / `S=GET DEVICE PUFFS` | `S=176` / `S=183` |
| `S=GET TEMP PUFFS` | `S=176` — every puff hit temperature protection |
| `S=GET MEAN POWER` / `S=GET SD POWER` | `S=27.33W` / `S=8.55W` |
| `S=GET MEAN TEMP` | `S=290.64F` |
| `S=GET LAST POWER` / `S=GET LAST TIME` | `S=18.60W` / `S=50.34S` |
| `S=GET LAST PEAK TEMP` | `S=391.26F` |
| `S=GET DEVICE ENERGY` | `S=23144.58MWH` |
| `S=GET RESETS` | `S=1` |

## Protocol rules, from Evolv

**Serialize. One query, wait for the reply, then the next.** Do not pipeline: the board will not send a
reply until its send buffer is empty, so batching gains nothing and can deadlock - its receive buffer
fills while it waits to finish sending to you. Replies are **FIFO with no correlation id**, so three
`B=GET CELL n` in a row come back as three bare values in order and you must track which is which.

Evolv says no inter-command delay is needed and Device Monitor uses none; **substantially more than 30
queries per second** is achievable. One community implementation nonetheless found ~5 ms between
batches reduced dropped replies, and `E=GET *` in particular wanting ~50 ms. If replies go missing,
that is the knob.

**EScribe can be connected at the same time.** It talks over HID and leaves the CDC serial port free,
which is why the query tool works with EScribe open.

### The CSV stream — tested, and it is a MODE SWITCH

**EScribe -> Research tab -> Serial Output Format** has exactly two values:

| Setting | What the port does |
|---|---|
| **Plain Text Serial** | The command console everything above describes. The default |
| **CSV (Excel)** | A continuous data stream. **Commands get no reply at all** |

They are **mutually exclusive** - verified by sending `R=GET COLD` while streaming and receiving only
more stream. Choose one. Changing it requires **Upload Settings to Device**.

> **That upload does *not* clear cold ohms**, contrary to what this file first claimed. Verified by
> round-tripping the setting and re-reading: the cup stayed locked at 0.464 throughout. What clears
> cold ohms is uploading one of **our published `.ecig` files**, because those ship
> `EvolvWDColdOhms = 0` deliberately (`12`). Changing a setting in EScribe uploads the config EScribe
> already holds, which carries the device's own measured values. Same button, two different
> operations.
>
> The last-puff buffer *is* cleared: `S=GET LAST TIME` and `S=GET LAST PEAK TEMP` returned values
> before the upload and `?` after, while the stored resistance survived.

#### What the stream looks like

```
t,Voltage,Current,Power,Ohms,Temp,Battery
0.01562,,,,,,4.15137
0.03125,,,,,,4.15204
```

Seven columns, and the **header is re-emitted periodically** rather than only once, so a parser should
expect it mid-stream. Idle, only `t` and `Battery` carry values; the other five fill during a puff.

**The rate is 64 Hz, not 50.** Timestamps advance by exactly 0.015625 s, which is 1/64. Evolv's forum
post says 50 Hz, and the Research tab's own **Recording Rate** read 16 Hz during this capture - so that
field governs the internal recording for charts, not the serial stream. Measured 515 lines in 8
seconds.

#### The rest of the Research tab

- **Data Acquisition:** Recording Rate (Hz), Initial Recording Rate (Hz, for a given number of
  seconds), Recording Probability (%), Serial Output Format.
- **Experimental Setup:** Puff Limit, Energy Limit, Time Limit, Return By - all Disabled here. These
  look like automatic cut-offs for unattended test runs.
- **Research Seal:** Apply / Break / Check, plus Reset Statistics. The seal is the `Research -> Sealed`
  measurement in `05` - a tamper indicator for a device under study.

#### Still to do

**Capture a puff.** Idle, the stream carries almost nothing. One fire would show what Voltage, Current,
Power, Ohms and Temp look like at 64 Hz - and `Ohms` sampled through a puff is the clearest view of
coil behaviour available anywhere in this project, worth far more than the cold reading alone.

`tools/dna-stream.ps1` captures and reports the rate, column count and a sample.
### What the feature keys mean

From Evolv: `PC` power commands, `TC` temperature commands, `St` long-term statistics, `FG` fuel
gauging (so `C=GET` works), `S:n` multi-cell with max n, `M` profiles. They exist so a device can
advertise a restricted or extended feature set, and tools adapt - something advertising only `PC` will
never be asked for a temperature.

This board reports `FG` **not** at all and `C=GET` returns `?`, while `C=GET%` works - consistent with
a single-cell board without full fuel gauging.

## Writes — documented, not run here

These change the device. **`F=` fires the coil.**

| Command | Effect |
|---|---|
| `F=#S` | **Fires** for # seconds |
| `P=#W` | Power setpoint |
| `T=#F` / `T=#C` | Temperature limit |
| `T=?` | **Turns temperature protection off** |
| `T=MONITOR` | No control, but temperature still measured and readable |
| `M=#` | Switch profile, 1–8 |
| `U=#A` | USB current limit; `0` disables charging |
| `V=#V` / `I=#A` | Voltage and current limits — **not retained across a power cycle** |
| `S=RESET` / `X=RESET` | Reset statistics / device |

---

## What serial cannot reach

- **Per-profile settings.** Asked directly on the Researcher Forum in 2018 - material, preheat power,
  punch and time, per profile - and **Evolv never answered**, across two prompts over three months.
  Taken with their statement that settings bake to an encrypted binary (`16`), treat it as absent.
  `M=#` switches which profile is active; nothing edits what a profile contains.
- **Relative adjustment.** Setpoints are absolute only. There is no "current watts + 10" or "+10%";
  read with `P=GET SP`, compute, then set the new absolute value.
- **Themes and configs.** Encrypted binary upload, EScribe only (`16`).

## What this unlocks

**The data the replace thresholds lack.** They rest on a single observed failure (`02`). `R=GET COLD` with `S=GET PUFFS` is the pair to log — wear tracks use, not calendar time — and `tools/dna-query.ps1 -Csv` appends exactly that.

**Checking a theme against ground truth.** `T=GET MATERIAL`, `M=GET` and `R=GET COLD` report what the firmware believes, independently of what a screen draws. When a conditional variant misbehaves, this distinguishes "the condition is wrong" from "the value is not what I assumed" — which is precisely the ambiguity that cost a day on the replace warning (`07` #25).

**Scripted test loops.** `M=#` to switch profile and `T=#F` to move a setpoint make it possible to sweep states and watch the screen, without rebuilding a theme per case.

## Sources

- Evolv's own list, Researcher Forum, *Plain Text Serial commands* (James, 2017) — the authority for the grammar and the statistics rules.
- <https://github.com/hobbyquaker/dna-commands> — community list, broader but partly unverified; several of its entries get no reply here.
- **ECigStats** is why the `E` and `S` command sets exist: Evolv's cloud puff-statistics service speaks them, and EScribe's "Internet Sync" feeds it. James published a C# client library for its API in 2017. Not useful here, but it explains why device identity and lifetime statistics are first-class commands while profile contents are not.
- <https://github.com/eucalyhome/dnainfo> — a Raspberry Pi project reading a DNA over this interface in Python, confirming it works outside Windows.

The verified table above is what **this** board answered, which is the part to trust.
