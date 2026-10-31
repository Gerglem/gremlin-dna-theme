# 16 – Driving the mod programmatically

> ## Where this stands, 2026-10-30
>
> This file is written in discovery order and is long. The conclusions, so a cold reader does not
> have to reconstruct them from the chronology:
>
> | | |
> |---|---|
> | **Reading and driving the mod** | **SOLVED.** `tools/dna-hid.py`, vendor HID, no EScribe, no COM port, no driver |
> | **The flash layout** | **SOLVED.** Evolv's own code produces it on request, no device attached - `UWB.FE(ggq)` -> `A.WIA` -> `JSL` -> `PYB.PE()` |
> | **Opening a link** | **SOLVED.** `BGQ.FE(port, vid, pid, ver, OpenConfiguration, 1, enum0) -> POT`, with the port string derived from WMI - no hand-made file |
> | **Building a Programmer** | **SOLVED.** `PYB.UE(func, n)` with **n >= 128** - the Int32 is an address whose high bit must be set |
> | **Reading the settings image** | **`AX()` times out.** The `Boolean[]` is ruled out; the version has still never actually been set (wrong type passed); HID contention with Device Monitor is the remaining suspect |
> | **Writing a config** | **Untried.** Needs the read working first, then the `dontUpload` dry run, then Jake's explicit go-ahead |
>
> **Everything before "SOLVED: the real flash layout" is the investigation that got there**, including
> several wrong turns kept on purpose. Where an older section is superseded it says so inline, but if
> an older passage and a newer one disagree, **the newer one wins.**


**Goal:** read and write the device from a command line, without EScribe's GUI in the loop — so a change can be uploaded and checked in seconds instead of by hand.

Confirmed in Windows device enumeration, 2026-10-30:

| InstanceId | What |
|---|---|
| `USB\VID_268B&PID_0433\<serial>` | USB Composite Device. **The instance ID is the board serial** - never paste one into this repo (`12`) |
| `...&MI_00` | **HID-compliant vendor-defined device** |
| `...&MI_01` | USB Serial Device (COM4) |

`268B` is Evolv, `0433` this board. Two interfaces, exposed at once as a USB composite device (`13`):

| | Interface | Status |
|---|---|---|
| **Primary** | **HID** (`MI_00`) — what EScribe uses for settings transfer | **SOLVED for read and control, 2026-10-30.** See below |
| Backup | **CDC serial** (`MI_01`, a COM port) — what the Serial Terminal talks to | Unexplored; command set unknown |

HID is the goal because it is demonstrably capable of the whole job: it is how every config this project has ever shipped reached the mod. The serial port is the fallback precisely because we do not yet know what it can do.

---

## SOLVED 2026-10-30: the HID channel is open, and it is the text protocol

`tools/dna-hid.py` reads and drives the board over HID with **no EScribe, no COM port and no driver
install** - only `pip install hidapi`. Verified against the serial baseline on the same board, same
minute:

    E=GET PRODUCT  ->  E=DNA 100 Color      R=GET COLD  ->  R=0.464OHM
    E=GET VERSION  ->  E=311105588          T=GET SP    ->  T=385.00F
                                            S=GET PUFFS ->  S=186

**Evolv's 2015 claim is literally true**: HID is serial tunneled over HID, so every command in `17`
works here unchanged.

### The framing

    report id 0x01 | magic 0xDE | length | payload | zero pad to 63 bytes

The payload is the plain-text line including its `
`, and `length` counts it: `0x0A` for
`B=4.122V
`. Reports are 63 bytes in and out with no feature reports, which matches what EScribe's
own debug log prints on every open.

Two things cost time and are worth knowing:

- **The report ID is `0x01`, not `0x00`.** A write with `0x00` is rejected by Windows and hidapi
  returns `-1` with no further explanation.
- **The board streams unsolicited reports** in the same framing - battery volts, power, temperature,
  on a loop. A read can easily return a line nobody asked for, so always match on the expected prefix.

### It also works where serial does not

`13` notes the CDC port is unusable on macOS, because the composite device needs an Interface
Association Descriptor that macOS does not support. HID has no such problem, so this is the portable
path as well as the fast one.

### Passive observation, which is the way in to the upload protocol

Windows delivers HID input reports to **every open handle**. Opening our own handle while Device
Monitor polls shows Device Monitor's replies arriving live - `W=` clock lines, `U=` USB volts and
watts, `B=-1.659A`, `C=96%`, `X=` flags. So **EScribe's session can be watched without USBPcap**, at
least in the device-to-PC direction.

That is the lever on the one unsolved piece. During an upload the device's side of the conversation is
visible for free; only the PC-to-device direction needs a real capture. Combined with a settings image
we already hold, that may be enough.

**Caveat, learned immediately:** with Device Monitor running, replies interleave and a prefix match can
grab someone else's line - a `S=GET ENERGY` came back `S=291.87F`, a temperature. **Close Device
Monitor for clean reads.**

## Calling Evolv's own uploader - the chosen route, 2026-10-30

**Decision:** push configs by calling EScribe's own upload code rather than by reimplementing the
protocol from the capture. The requirement is parity with EScribe's safety gates, and their code keeps
every gate by construction. Reimplementing means rebuilding each gate by hand and discovering the
missed one on live hardware.

### The gates to preserve

Inventory, so a hand-rolled path can be measured against it. Confirmed items are observed; the rest
are inferred from the API shape and need checking before anything is trusted.

| Gate | Evidence |
|---|---|
| **Automatic pre-upload backup** | **Confirmed.** `Backups\{GUID}6-10-30 14_43 - U - DNA 100 Color.ecig` was written by the upload run on 2026-10-30. The `U` marks an upload |
| **Device identity check** | **Confirmed in the log:** `device code 109.1, device Evolv DNA 100 Color` is resolved before the stream opens |
| **Firmware / user-mode version handshake** | **Confirmed in the log:** `Sending 'get version'` then `User mode version is 311105588`, before any transfer |
| **Per-frame CRC** | The 3-byte trailer on every transfer frame (above). Not yet verified as a CRC |
| **Differential hashing** | `CreateForDNAColor(sha1Cache)` and the 8.7 KB read back during an upload |
| **Write transaction** | `UpdateBegin(writable)` / `UpdateCommit()` / `UpdateEnd(writable)` |
| **Dry run** | `PerformUpload(ctx, progress, dontUpload)` - the third argument |

### What works now

Run **in process**, from Device Monitor's Run Script:

    FE(port, 9867, 1075, 0)   ->  A.POT          # the link opens
    Programmer.CreateForDNAColor(None)  ->  A.ECC
    ECC.Stream = pot                              # assigned, no error
    ECC.Initialize()                              # returns cleanly

The port string is `HID:` + base64 of `"<vid_decimal>'<pid_decimal>'<serial>"`, rebuilt from a live
device read and byte-identical to the one in EScribe's debug log. The third integer is the product
version and `0` is accepted.

**Out of process this still fails.** `FE` throws `NullReferenceException` before touching its
arguments - its IL calls `DOT.get_GE` first, a static EScribe populates at startup. Passing a real
`CSH` (HidSharp's `OpenConfiguration`, public parameterless constructor) does not help. Reconstructing
that startup graph through obfuscated types is not worth it while the in-process route works.

### Why `UserModeVersion` stays null, and what it means

After `Initialize()` the version is still `None`. Reading the IL explains it:

- `get_UserModeVersion` is 7 bytes - it only reads the field `OCC.KE`.
- `Initialize()` is 36 bytes of wiring (`LWC.EE`, `OCC.get_SM`, `VTC.XE`, `new DDY`, `TCC.set_RM`). It
  does **not** perform a handshake.
- **Nothing in `DEScribe.Upload` writes that field** - only the four `set_UserModeVersion` overloads
  exist, and no caller.

So the Programmer is a transport object, and **`DEScribe.Core` is the orchestrator**: it sends
`get version`, sets `UserModeVersion` on the Programmer, takes the backup and brackets the transfer
with the `*** START UPLOADING SETTINGS ***` markers. That orchestration *is* where the gates live,
which is exactly the layer we want to call.

**Next target: `VYB.PerformUpload` in `DEScribe.Core`** - the one method found whose name survived
obfuscation at that layer. Map its parameters, then drive it with `dontUpload` set.

> Note when scanning: `AX` is a very common obfuscated method name, so an IL scan for callers of the
> Programmer's `AX` returns two dozen false positives. Match on the distinctive names instead.

## The upload architecture, mapped 2026-10-30

Four probe runs in Device Monitor plus IL reading. The shape is now clear, and it says why the direct
route failed.

### What fails, and why

`AX()` - the read side - throws `NullReferenceException` for every combination of arguments tried:
null progress monitor, each of Evolv's three concrete monitors (`A.FMQ`, `A.BTQ`, `A.PMW+RXW`, all
with parameterless constructors), and three shapes of the `bool[]`. The stack frame is `at (Object )`,
obfuscated, but it confirms the throw is **inside** `AX`, not in argument marshalling.

The cause is almost certainly **the Programmer has no layout**:

- `OCC` carries a field `IE : LogicalLayout`, exposed as the settable property `NM`.
- `Programmer.CreateForDNAColor` never sets it - its IL builds a `WOC` holding the `NHW` cache, three
  delegates, and hands off to an external constructor.
- `ECC..ctor(Int32, ZOC, JOC, ROC)` stores four fields and no layout.

So a Programmer built the way we were building it is **not usable** - it has a transport but no map of
the flash it is talking about. That is exactly the piece that must not be guessed.

### The missing layer: `A.PYB` in `DEScribe.Core`

This is the settings-document-and-device model, and it owns everything we were missing:

| Member | Reading |
|---|---|
| `PE()` -> `LogicalLayout` / `NE(LogicalLayout)` | get and set the flash map |
| `NE(PagingMethod, Int32, Int32, Int32, Boolean)` | **builds a region** - the layout is assembled here |
| `KE()` -> `Dictionary` / `SE(Dictionary)` | the settings values |
| **`UE(Func<>, Int32)` -> `OCC`** | **returns a fully configured Programmer** |
| `ctor(GGQ, Object, Nullable<T>)` | needs a `GGQ`, not yet identified |

**`PYB.UE(...)` is the correct factory**, not `Programmer.CreateForDNAColor`. Going through it means
the layout comes from Evolv's own code for this board, which was the whole point of choosing this
route over reimplementing the protocol.

### Corrections to earlier entries

- `VYB` is **not** an orchestrator. It derives from `ECC`, so it is a Programmer subclass. Useful only
  because parameter names survived there: `PerformUpload(Object context, IProgressMonitor progress,
  Boolean dontUpload)`, `UpdateBegin(Boolean writable)`.
- `ZSO.SGE` / `ZSO.PGE` in `DEScribe.UI` are 36-byte factories, not the upload and download entry
  points they looked like.
- `QMQ` from `HLF.XK()` does **not** implement `NHW`, so it is not the SHA-1 cache argument. The only
  implementor is `A.DHW`, which does have a parameterless constructor.

### The construction chain, traced 2026-10-30

All of this came from reflection and IL alone, with the device idle. It is the recipe for getting a
Programmer that actually has a layout.

    .ecig root element  ->  GGQ  ->  DWB.JSL(?, ggq, null)  ->  PYB  ->  PYB.UE(func, int)  ->  OCC

| Step | Detail |
|---|---|
| `A.GGQ` | `DimensionEngineering.Common`. Two public constructors: `(Int32, Int32, DDT)` and **`(XElement)`**. Carries two ints (`LE`, `VE`) and a `DDT` |
| The XML it parses | **Every `.ecig` opens with `<DESabertooth Device="109" Version="1" SWVersion="1.3.77.0">`** - and the debug log calls this board *device code 109.1*. So `GGQ` is the board identity, and it is sitting in our own config files |
| `DWB.JSL(Object, GGQ, Nullable<T>)` -> `PYB` | the only constructor of a `PYB` in `DEScribe.Core` |
| `FWB.get_DE()` -> `PYB` | an instance accessor - the likely home of EScribe's live document |
| `PYB.UE(Func<>, Int32)` -> `OCC` | the configured Programmer |

`DESabertooth` is a leftover from Dimension Engineering's motor-controller line, which is also why
Device Monitor's scripting API can drive Sabertooth hardware (`14`). The settings container is shared
across their products.

**This is the path to try next**, and it needs no new capture: build a `GGQ` from a `.ecig` root,
get a `PYB`, take the Programmer from `UE()`, and only then call `AX()`.

### What the captured payload is, and is not

Decoding work on `tools/samples/hid-upload-capture.log`, 2026-10-30:

- **It is not the settings image.** Six candidate decodings - raw, 8-into-7 LSB and MSB first,
  high-bit-group (sysex style), and the two per-frame variants - were searched for `DTv5XL`,
  `QuestCup`, `Gremlin`, `Clean`, `Nickel`, `Watts`. **No hits in any of them.**
- **It is not hashes either**, which was the earlier guess. Entropy is **5.38 bits/byte**; a hash
  stream over a 7-bit alphabet would sit near 7.0. The data is structured.
- The **first data byte carries only 2.61 bits of entropy**, so there is a small opcode alphabet
  there - `0x72` dominates, then `0x5b`, `0x5e`, `0x77`, `0x2f`.
- 204 of 207 frames are distinct; the only repeats are four one-byte `3a` frames.
- No two-byte periodicity: odd and even positions have near-identical distributions, so it is not a
  simple value/tag interleave.

Conclusion: the device-to-PC half is a structured command and response stream, not bulk content. The
image itself goes the other way, which a passive HID handle cannot see.

### Building the chain offline - how far that gets

Tried with no device involved, loading the assemblies and feeding a real `.ecig`:

- **`GGQ` is reachable**; the type loads and both constructors are visible.
- **`DWB` is abstract**, so `DWB.JSL` - the only `PYB` constructor - cannot be called without finding a
  concrete subclass. That is the current wall for an out-of-process build.

> PowerShell trap worth recording: a helper that catches `GetTypes()` failures must unwrap to the real
> `ReflectionTypeLoadException`. Catching the bare `$_.Exception` yields a wrapper with no `.Types`,
> the helper silently returns null, and types look absent when they are not. This produced one
> completely wrong "GGQ NOT FOUND" result.

### The layout is assembled piecemeal, not declared

`DWB.RSL(PYB, IEnumerable<>, Int32, Int32, GYB)` is 50 bytes of IL and adds **one** region:

    ldsfld   PagingMethod.ReadOnly
    ldc.i4   32915   (0x8093)
    call     YUB.XE
    ldc.i4   32919   (0x8097)
    call     YUB.XE
    callvirt PYB.NE
    call     Enumerable.ToArray
    callvirt PYB.RE

So regions are built from **feature IDs resolved through `YUB.XE`**, not from hard-coded offsets, and
the full map is accumulated across several call sites. That rules out lifting a static table out of
the assembly - and it is a second, independent reason not to hand-build a `LogicalLayout`: the real
one is derived per config, not fixed per board.

**The practical consequence:** the layout has to come from a live `PYB`. `tools/`-side work cannot
produce it. `tools/probe_pyb.py` (inert) hunts EScribe's own statics for a live `PYB` or `FWB`
and dumps `PE()` - region sizes, device offsets, paging and read-only flags. That one report would
settle the whole question.

### Measured 2026-10-30: the script host cannot see EScribe's document

Four probe runs settle the "get a live `PYB`" route. With `System.Windows.Forms` loaded explicitly -
Device Monitor's IronPython host does **not** reference it by default, which made two earlier runs
blind rather than negative - `Application.OpenForms` contains **exactly one form: Device Monitor's
own window.** The main EScribe window is not there, so the open document is not reachable.

| Probe | What it searched | Result |
|---|---|---|
| `probe_pyb.py` | static fields/properties of type `PYB`/`FWB` in `DEScribe.Core` | type found, 0 live |
| ~~`probe_pyb2.py`~~ | every static field in every assembly | **froze EScribe** (`07` #28), deleted |
| `probe_pyb3.py` run 1 | instance fields from live roots | blind - no WinForms reference |
| `probe_pyb3.py` run 2 | same, WinForms loaded | 1 form (Device Monitor's own), 296 objects, **0 live** |

The globals the host does expose are no help: `ECig` and `Device` are the **same** object (`A.OJA`),
the device interface rather than a document, and `Directories` / `UI` / `Script` are small host
helpers (`A.ARO`, `A.JRO`, `A.SDO`).

**So the blocker named above is not "we have not looked hard enough" - it is structural.** Hunting a
live `PYB` from a Device Monitor script cannot work.

### The remaining in-process route: build a `PYB` rather than find one

The chain needs a `PYB`; it does not care where one came from. `DWB.JSL(?, ggq, null)` is the only
constructor, and it was written off because **`DWB` is abstract** - but nobody looked for a
**concrete subclass**. If one exists, a `PYB` can be built from one of our own `.ecig` files, no
open document required, which would also make the whole thing work headlessly.

`tools/probe_dwb.py` asks that, plus whether `DEScribe.UI` is even loaded in the script host.
**Metadata only** - `BaseType`, `IsAbstract`, `GetConstructors`, `GetParameters` - no value reads and
no invokes, so no static constructor can fire.

If there is no concrete `DWB` either, the in-process route is exhausted and the fallback is the USB
capture: the device-to-PC half is already decoded (`tools/samples/hid-upload-capture.log`) and only
the PC-to-device direction is missing.

### Probe 4 result, 2026-10-30: the chain is unblocked in principle

`tools/probe_dwb.py`. Two findings, either of which would have been worth the run.

**1. `DWB` has 44 subclasses and about 25 are concrete, every one with a parameterless constructor.**
All in `DEScribe.Branding.Evolv`, named in the same obfuscated three-letter style (`JYA`, `DYA`,
`MHA`, `LHA`, `NHA`, `RHA`, `XIA`, `LIA`, `FIA`, `CIA`, `WIA`, `KIA`, `PIA`, `UIA`, `ZIA`, `MKA`,
`AKA`, `BKA`, `TKA`, `WKA`, `YKA`, `IKA`, `SKA`, `TPA`, `YPA`). The count and the branding namespace
both say **one per board model** - the DNA product line is about that size.

`16` called the chain blocked because `DWB` is abstract and `JSL` is its only `PYB` constructor.
**That was true and is no longer the obstacle.** `JSL` is an *instance* method
(`JSL(Object, GGQ, Nullable<T>) -> PYB`, `static=False`), so it needs a `DWB` instance - and there
are two dozen to choose from, each costing nothing to construct.

**2. `GGQ` is a struct with a `ctor(XElement)`.** The board identity can be built directly from the
root element of one of our own `.ecig` files - `<DESabertooth Device="109" Version="1">`, the *device
code 109.1* EScribe's own log prints. Nothing has to be reverse-engineered to produce it.

So the route is now:

    .ecig root --ctor(XElement)--> GGQ
    concrete DWB subclass --ctor()--> dwb
    dwb.JSL(null, ggq, null) --> PYB
    pyb.PE() --> LogicalLayout     <- the real flash map
    pyb.UE(func, int) --> OCC      <- a Programmer that HAS that layout

### Also measured: we are inside EScribe, and `DEScribe.UI` is loaded

`process: EScribe`, and `DEScribe.UI present: True`. So the main window **is** in this process - it
simply is not in `Application.OpenForms` as seen from the script host, which points at thread
affinity rather than a process boundary. Worth knowing, but **it no longer matters**: building a
`PYB` needs no document at all, which is strictly better than finding one. It would also work with
nothing open.

### The open question, and it is now a small one

**Which of the ~25 concrete subclasses is the DNA100C?** Metadata alone will not say. `tools/probe_dwb2.py`
constructs each one and reads its **instance fields** looking for the device code 109 or a product
string, which identifies the right class by evidence rather than by guessing at an obfuscated name.

That probe crosses a line the previous four did not: it **instantiates** types. That is no longer
metadata-only. Two things make it proportionate - these are branding descriptors with parameterless
constructors, which is about as inert as a constructor gets, and **nothing in it touches the mod**,
so the worst realistic outcome is another EScribe restart (`07` #28). It deliberately **does not call
`JSL`**; that is the next step and belongs in its own run once the right class is known.

### Probe 5 result: the 25 subclasses are **stateless**

All 25 constructed without a single failure - so those constructors are inert in fact, not just in
theory, which is worth knowing before anything heavier is tried. But **none has a simple instance
field**. The board identity is not stored on the `DWB`.

That leaves two possibilities, and `tools/probe_dwb3.py` tests both in one run:

- **a property returning a constant** - the natural idiom for a stateless descriptor, and the first
  thing it checks;
- **a dispatcher elsewhere** that maps a device code or a `GGQ` to the right subclass. Part 2 looks
  for one by metadata: any method returning a `DWB`/`XWB`, or taking a `GGQ`. If that exists, the
  subclass never needs identifying by hand - we ask for the right one.

If neither turns anything up, the remaining option is to call `JSL` on each of the 25 with our own
`GGQ` and keep whichever returns a usable `PYB` - crude, but decisive, and still device-free.

### Probe 6 result: the dispatcher exists. The chain is fully resolved

The 25 subclasses have no simple **properties** either - they are behaviour-only. But part 2 found
the two pieces that make that irrelevant, both in `DEScribe.Core`:

| | |
|---|---|
| **`UWB.FE(GGQ) -> DWB`**, *static* | **the dispatcher.** Hand it a board identity, get the right subclass back |
| `UWB.BE(Guid) -> DWB`, static | a second lookup, by GUID |
| **`DWB.DSL(GGQ) -> Boolean`** | *"do I handle this board?"* - presumably what `FE` uses, and an independent cross-check |

**So none of the 25 has to be identified by hand.** Every one of them also carries `EPL`, `XPL` and
`MPL`, all taking a `GGQ` - the per-board behaviour the subclasses exist for.

The chain, complete and with nothing left inferred:

    XElement("<DESabertooth Device='109' Version='1'/>")  -> GGQ    ctor(XElement)
    UWB.FE(ggq)                                           -> DWB    static
    dwb.JSL(None, ggq, None)                              -> PYB
    pyb.PE()                                              -> LogicalLayout

`tools/probe_layout.py` runs exactly that and dumps the regions. It is the first probe to exercise
the upload-path objects, and still **opens no link, builds no Programmer, uploads nothing** - `PE()`
reads a map, it does not apply one. **The mod need not even be plugged in.**

If `JSL(None, ...)` rejects the null first argument, that argument is the settings document and the
fix is to pass one - which we can build, since `GGQ` already comes from our own file.

## SOLVED 2026-10-30: the real flash layout, from Evolv's own code

`tools/probe_layout.py`. Every step of the chain worked on the first run, with the mod not involved
at all.

    GGQ from <DESabertooth Device="109" Version="1" />   -> A.GGQ  [109.1]
    UWB.FE(ggq)                                          -> A.WIA
    DSL(ggq) true for exactly one subclass               -> WIA    (agrees)
    dwb.JSL(None, ggq, None)                             -> A.PYB
    pyb.PE()                                             -> LogicalLayout

**The DNA100C's board class is `A.WIA`**, and it was identified two independent ways: the dispatcher
returned it, and `DSL(ggq)` came back true for **exactly one** of the 25 concrete subclasses - the
same one. The `GGQ` printed its own identity as `[109.1]`, which matches EScribe's debug log, so the
board identity built from our own `.ecig` root is right.

**`JSL` accepted `None` as its first argument**, so a settings document is not needed to obtain a
`PYB` or its layout. That was the open worry and it is answered.

### The layout

    PCSize      5,341,184
    PCSizeUsed    200,448

| Region | Size | Device offset | PC offset | Read-only | Hash whole | Chunk |
|---|---|---|---|---|---|---|
| 0 | 101,888 | `0x000000` | `0x000000` | no | no | 1024 |
| 1 | 256 | `0x018E00` | `0x018E00` | no | no | 1024 |
| 2 | 98,304 | `0x500000` | `0x500000` | no | no | 1024 |

`101,888 + 256 + 98,304 = 200,448`, exactly `PCSizeUsed` - the three regions account for the whole
used image, so nothing is missing from the map.

Reading it against what the project already knows: region 2 is 96 KB at `0x500000`, which is the
**off-board** space `06` tracks at 93.6% for images and fonts; region 0 is ~99.5 KB of on-board
settings and controls; region 1 is a 256-byte block of its own. All three are writable and hashed in
1 KB chunks, which is consistent with the differential hashing gate in the inventory below.

**This is the thing `16` said must never be hand-built**, because the map is derived per config from
feature IDs rather than declared per board. It no longer has to be: Evolv's own code produces it on
request, in-process, with no device attached.

### What that changes

The v3.0 blocker is gone. Writing a config is no longer a research problem - the remaining work is
engineering, and the next piece is `PYB.UE(Func<>, Int32) -> OCC`, which returns a Programmer that
*has* this layout. That is the object `16` found could not be built correctly before.

### Where the line is now

Everything up to here has been device-free: no link opened, nothing written, the mod not even
required to be plugged in. **The next steps are not.** In order of increasing commitment:

1. **Still safe** - feed a real `.ecig` document to `JSL` instead of `None` and compare layouts. It
   tests the "derived per config" claim directly, and still writes nothing.
2. **Still safe** - call `PYB.UE(...)` for a Programmer. Until a stream is attached it talks to
   nothing.
3. **Touches the device** - attach a link (`tools/probe_open_link.py` has the proven recipe) and run
   `PerformUpload(ctx, progress, dontUpload=True)`, the vendor's own dry run.
4. **Writes to flash** - the same call with `dontUpload` false.

Steps 1 and 2 are mine to do. **Steps 3 and 4 need Jake to say so explicitly**, and 4 is the first
thing in this entire effort that can brick the mod. The safety gates inventoried in this file -
pre-upload backup, device identity check, firmware handshake, per-frame CRC, differential hashing,
the write transaction - all live above this layer and are the reason for going through Evolv's code
rather than around it.

### Step 2 result: `UE` wants a connection factory, so the device-free path ends here

`PYB.UE(Func<A.POT>, Int32) -> OCC`. **`A.POT` is the HID link object** - what
`probe_open_link.py`'s `FE(port, vid, pid, 0)` returns - so the `Func` is a factory the Programmer
calls to get a connection. Passing `None` for it threw, from inside the Programmer's own setup:

    ArgumentOutOfRangeException: Parameter name: address
       at A.DDY..ctor(Byte, NDY) / A.TCC.Initialize() / A.SRB.EE / A.PYB.UE

Consistent with the null delegate rather than with the `Int32`, which was swept over 0, 1 and 109
with the same result. `PYB.KE()` returned a 4-entry dictionary, so the `PYB` itself is real and
populated.

**So a Programmer cannot be obtained without a link.** That is the boundary: everything up to the
layout is device-free, the Programmer is not.

`tools/probe_read.py` is the step-3 experiment - and it is a **read**, not the `dontUpload` dry run.
The dry run validates the plan it is given rather than whether that plan fits the board, and needs a
context object nobody has identified; a read exercises the same chain - link, Programmer, layout,
transfer - and cannot write. `Initialize()` sends `get version`; `AX()` is the download half, the
same thing EScribe does for *Download Settings from Device*. **No `PerformUpload`, no write, no
erase.**

### Step 3 run 1: the link opens, but `UE` fails before it uses it

    A. build the PYB            OK    GGQ [109.1] -> WIA -> PYB
    B. find the device          OK    4 USB entries, port string 36 chars (from WMI)
       open the link            OK    FE(String, Int32, Int32, Int32, CSH, Int32, IGI)
                                      FE(port, 9867, 1075, 0) -> A.POT
    C. PYB.UE(factory, 0..3)    FAIL  ArgumentOutOfRangeException: address

**The link is up.** `BGQ.FE` takes **seven** arguments, not four - an earlier attempt searched for a
4-parameter overload and reported "not found" after getting everything else right. `CSH` and `IGI`
are HidSharp types found by reflection, because the assembly loads under its own name but its
*types* are obfuscated - which is also why `from HidSharp import ...` fails outright.

**The port string no longer needs a hand-made file.** WMI (`Win32_PnPEntity`, skipping the `MI_`
interface children) gives the composite parent's serial, and the string comes out at the same 36
characters the old `dna-port.txt` held. The serial stays in memory (`12`).

**`UE` is the remaining blocker, and the Func is not the cause.** It throws the *same*
`ArgumentOutOfRangeException("address")` whether it is handed a null delegate or one returning a
live `POT`, so it fails before the factory is ever called. The stack is

    A.DDY..ctor(Byte address, NDY) <- A.TCC.Initialize() <- A.SRB.EE <- A.PYB.UE

so a `Byte` address is computed from something and comes out invalid. The `Int32` is innocent too -
0, 1, 2, 3, 109 and the version all give the identical error.

That leaves the PYB's own state. The suspect is **`JSL`'s first argument, which we pass as `None`**:
`PE()` returns a layout without it, because the flash map is per board, but `UE` builds a Programmer
and may need the settings document the null is standing in for.

`tools/probe_pyb_state.py` tests exactly that - it dumps every member of `PYB`, reads `KE()`, and
rebuilds with `None`, an `XElement` and an `XDocument` as the first argument, trying `UE` after each.
Device-free.

### The PYB's anatomy, read out 2026-10-30

`probe_pyb_state.py`. Useful even though it did not unblock `UE`.

**`KE()` returns four named memory areas**, each a `WYB`:

    'EEPROM'    ''    'KERNEL'    'FLASH'

while `PE()` reports **three** regions. One of those keys is the **empty string** - a nameless area
that has no counterpart in the layout. A Byte constructor rejecting an `address` is exactly what an
unpopulated area would cause, so that is the current suspect.

**The `PYB`'s own fields**, which say what state it carries and what a fully-built one would have:

| | |
|---|---|
| `YE : GGQ` | the board identity we supplied |
| `FE : LogicalLayout` | the flash map |
| `HE : Object` | almost certainly `JSL`'s first argument - the one we pass as null |
| `AE : Func<>` | a stored delegate, with a setter of its own in `ZE(Func<>)` |
| `CE`, `TE : Dictionary<>` | settings |
| `QE`, `WE : UInt32`, `IE : Nullable<>`, `OE : GYB` | |

Worth noting `ZE(Func<>) -> Void` exists separately from `UE`'s `Func` parameter, and
`NE(LogicalLayout)` / `NE(PagingMethod, Int32, Int32, Int32, Boolean)` can set or build the layout -
so a PYB can be furnished after construction, not only through `JSL`.

**A false lead corrected:** passing a real document to `JSL` failed with *"expected object, got
NoneType"*. That is IronPython complaining about the **call shape**, not .NET rejecting the
argument - a Python list was being handed where a typed `Object[]` was needed. The retry uses an
explicitly sized `Array[Object]`.

`tools/probe_address.py` reads every `WYB`'s fields to find the bad address, lists `DDY`'s
constructors, and retries `JSL` properly marshalled.

### Two hypotheses killed, 2026-10-30

**The memory map is not malformed.** `KE()`'s four areas are start/end pairs that tile the layout
exactly, so the nameless one is simply the settings block between EEPROM and KERNEL:

| Area | Range | Size | Layout region |
|---|---|---|---|
| `EEPROM` | `0x000000`..`0x000600` | 1,536 | region 0, with the next |
| `''` | `0x000600`..`0x018E00` | 100,352 | 101,888 together |
| `KERNEL` | `0x018E00`..`0x018F00` | 256 | region 1 |
| `FLASH` | `0x500000`..`0x518000` | 98,304 | region 2 |

**`JSL` does not want a document either.** Given a non-null first argument it **returns null** - it
does not throw - so `JSL(None, ggq, None)` is the correct call and the earlier *"expected object,
got NoneType"* was only ever an IronPython marshalling error of mine, not a signal about the
argument. The `PYB` we already build is the right one.

**What that leaves.** `DDY..ctor(Byte address, NDY)` - and the parameter is a **`Byte`**, so valid
values are 0..255, while every address in the map above is far larger. So `address` is not a memory
offset; it is a small identifier. `UE`'s `Int32` is the only thing we control that could reach it,
and only six values have been tried.

`tools/probe_ue_sweep.py` tries all 256 and reports what `NDY` is - if it is an enum, its names may
say what kind of address this is. It passes a **null** `Func`, so even a `UE` that succeeds cannot
reach the device.

If every value gives the identical error, the Int32 is not the address and the bad one is computed
inside `TCC.Initialize` from `PYB` state not yet identified - in which case the next lead is
`SRB.EE` / `TCC`, not `UE`.

## SOLVED 2026-10-30: `UE`'s Int32 is an address whose high bit must be set

A clean split, from sweeping all 256 values with a null `Func`:

    0 .. 127     ArgumentOutOfRangeException: address
    128 .. 255   -> A.ECC        a Programmer, every time

**Bit 7 must be set.** That matches the `0x8093` / `0x8097` constants this file already recorded in
`DWB.RSL`'s IL, passed to `YUB.XE` - addresses in this system carry a `0x80` prefix. The six values
tried before the sweep - 0, 1, 2, 3, 109 and the version - were all on the wrong side of the line,
which is why the error never moved and why it looked like PYB state rather than an argument.

`NDY`, `DDY`'s second argument, is an enum with two members: **`GE`** and **`EE`** - the same two
names the memory areas use for their start and end offsets. So `DDY(Byte address, NDY which)`
appears to identify *an endpoint of a memory area*, which fits an address that is an identifier
rather than an offset.

**So a Programmer can now be built**, and the chain is complete on paper:

    .ecig root -> GGQ -> UWB.FE -> DWB -> JSL -> PYB -> UE(func, >=128) -> OCC

What is still unverified is whether that `OCC` **carries the layout** - the thing
`CreateForDNAColor` never set and the reason `AX()` threw every way it was tried. `probe_read.py`
now builds with 128, 129, 160 and 255, compares the layout each returns, and only then opens a link
for `Initialize()` and `AX()`.

### Step 3 run 2: a Programmer with a live link, and the read times out

    A. build the PYB                 OK
    B. port string from WMI          OK   36 chars
       BGQ.FE(port, 9867, 1075, 0)   OK   -> A.POT
    C. UE(factory, 128)              OK   -> A.ECC
       does it carry the layout?     unknown - see below
    D. Initialize()                  OK   returned, no exception
       UserModeVersion               None
    E. AX(IProgressMonitor, Boolean[])   TimeoutException

**`A.ECC` is the Programmer**, built with a factory returning our live link. Everything up to and
including that now works end to end from a standing start, with no EScribe document involved.

**`UserModeVersion = None` is expected, not a failure.** This file established by IL reading that
`Initialize()` is 36 bytes of wiring and performs **no handshake**; `DEScribe.Core` is the
orchestrator that sends `get version` and then *sets* the property, and nothing in `DEScribe.Upload`
ever writes it. So the Programmer is talking to a board whose version it does not know - a plausible
reason for a transfer to hang, and the first thing the next run tests.

**The layout question is still open, and that is a defect in the probe, not a result.** The check
looked for properties named `NM`, `IE` and `FE` and skipped any that did not exist *silently*, so an
empty section means "none of those three names matched", not "no layout". `probe_read2.py` dumps
**every** property on the Programmer instead.

**`AX(IProgressMonitor, Boolean[])`** - the second argument was passed as null. If it selects which
regions to transfer, null may mean "nothing" or be dereferenced into a malformed request. The next
run passes a `Boolean[3]` of `True`, matching the three regions in the layout.

One more candidate worth keeping in mind: this file already warns that **a second HID handle makes
replies interleave**, and the probe runs inside Device Monitor, which is itself polling the board.
If the version and the flags both fail to explain the timeout, contention is the next suspect.

**At most two `AX` attempts per run from now on** - each timeout costs real wall-clock time on the
operator's bench.

### Step 3 run 3: flags ruled out; two of my own errors corrected

    Programmer: A.ECC        Stream = POT        UserModeVersion = None
    set UserModeVersion      FAILED  UInt32 cannot convert to Nullable<Int32>
    AX(None, Boolean[3] all true)    TimeoutException
    AX(None, Boolean[0])             TimeoutException

**Genuinely ruled out: `AX`'s `Boolean[]`.** Both a full array and an empty one time out
identically, so the null passed in run 2 was never the cause.

**Two things that read like findings and were not.**

1. *"`UserModeVersion` could not be set."* It is a **`Nullable<Int32>`** and I passed a `UInt32`,
   so the conversion was rejected and **the version was never actually set.** The leading
   hypothesis - that the Programmer hangs because it does not know what it is talking to - remains
   completely untested.
2. *"The Programmer exposes no layout."* The dump showed only `Stream` and `UserModeVersion`, which
   I read as the layout being absent. It is not evidence: **`GetProperties` does not return
   non-public members inherited from a base class**, and `A.ECC` derives from `OCC`, which is
   exactly where this file found `IE : LogicalLayout` exposed as `NM`. The dump was an artefact of
   how I asked for it.

`tools/probe_read3.py` corrects both - it walks the full type chain with `DeclaredOnly` at each
level so inherited private members appear, sets the version as an `Int32`, and calls `Initialize()`
**after** the version rather than before, since the handshake is what we are standing in for. **One
`AX` attempt**, because each timeout costs bench time.

If it still times out with the version genuinely set, the last suspect is **HID contention**: the
probe runs inside Device Monitor, which polls the board itself, and this file already records that a
second handle makes replies interleave.

### Where this leaves a push — SUPERSEDED, kept for the reasoning

> **Overtaken 2026-10-30 by the section above.** Its second branch - *"or by constructing one once
> `GGQ` is identified"* - is exactly what happened, so the conclusion below ("further away than it
> looked") no longer holds. The warning about hand-building a `LogicalLayout` stands and is the
> reason the vendor route was worth the effort.

**Further away than it looked, and deliberately not attempted.** Driving `PerformUpload` with a
hand-built `LogicalLayout` would mean inventing region sizes, device offsets and paging for live
flash. `dontUpload` does not protect against that: it validates the plan it is given, not whether the
plan is right for this board. And it would bypass the gates rather than keep them, which is the
opposite of the requirement.

The honest next step is to obtain a live `PYB` - either from EScribe's object graph inside Device
Monitor, or by constructing one once `GGQ` is identified - and take the Programmer from `UE()`. Then
`AX()` should work, and a real read validates the whole chain before any write is considered.

## The settings transfer, captured 2026-10-30

One real `Upload Settings to Device` was watched from a second HID handle while EScribe did the work.
Sample kept at `tools/samples/hid-upload-capture.log` (device-to-PC only; telemetry stripped, scanned
for identifying strings).

**The transfer rides the same channel as the text protocol.** There is no separate endpoint and no
second magic for the bulk data - which is why it was nearly missed.

### Frame layout

    01 | DE | outer_len | F8 2B | inner_len | <inner_len bytes> | 3 bytes
     ^    ^                ^                                       ^
     |    |                sub-protocol marker                     trailer, CRC-shaped
     |    same magic as the text protocol
     report id

`outer_len = inner_len + 6`, with **no exceptions across 207 frames**. Text frames carry ASCII in the
same `0xDE` envelope; transfer frames carry `F8 2B` and then binary. **A reader that keys only on the
magic byte sees transfer frames as text and destroys them** - that mistake cost one capture.

### The payload is 7-bit encoded

Across 8,768 payload bytes and every trailer, **not one byte is >= 0x80**: 124 distinct values,
maximum `0x7F`. That is the usual packing for tunnelling binary over a channel that reserves the high
bit, so the real image has to be unpacked 8 bytes of 7 bits to 7 bytes before it will mean anything.

### What the burst looks like

| | |
|---|---|
| Control frame first | `01 01 00 00 00 67 ...` - magic `0x01`, not `0xDE`, and `0x67` = 103 |
| Then | 207 transfer frames, 8,768 payload bytes |
| Duration | 6.3 s, matching the ~7 s upload in EScribe's own debug log (`13`) |
| Frame sizes | clustered 40-47 bytes, with four 1-byte frames and one 7-byte |

Note this is **8.7 KB travelling device-to-PC during an upload**. That is consistent with the
differential uploader found by reflection: the Programmer reads region hashes back to decide which
chunks actually need writing. So much of this burst is likely hash material, not settings.

### What is still missing

- **The PC-to-device direction.** A passive HID handle sees input reports only. That half needs
  USBPcap, and it is the half that carries the image being written.
- **The command semantics.** Frame-leading bytes repeat heavily (`0x72` 82 times, then `0x5b`, `0x5e`,
  `0x77`, `0x2f`), which looks like an opcode field worth mapping.
- **What `0x67` counts.** 103 against 207 frames is suggestively close to half.

## What is and is not reachable - settled by Evolv, 2015

From Evolv staff on the Researcher Forum, and it bounds this whole document:

- **All operation and monitoring is reachable** over the plain-text interface. "Anything you can do in
  Device Monitor is a wrapper for command line commands." That part is done, in `17`.
- **Settings and themes are not.** "Loading firmware is encrypted, and the settings bake to a binary
  file for upload." So a `.ecig` cannot be pushed to the mod by any text command - uploading a theme
  needs EScribe, or the HID path below, and the binary format is not published.
- **The HID interface is serial tunneled over HID**, and "that is totally standard". So a CLI over HID
  would speak the *same plain-text commands*, not a separate binary protocol. That is a far smaller
  job than the obfuscated-assembly route suggested, and it is the portable one: on macOS the CDC port
  does not work at all (the composite device needs an Interface Association Descriptor, which macOS
  does not support), while HID-tunneled serial works everywhere.

**So the goal splits in two.** Reading and driving the device: solved, see `17`. Uploading a config:
still requires EScribe or a reverse-engineered binary format, and no amount of serial work changes
that.

## The promising route: call Evolv's own code

EScribe is **.NET**, and its assemblies load and reflect fine from the local install (`%APPDATA%\Evolv\EScribe Suite`). That means the transfer logic can potentially be *called* rather than reimplemented — no protocol reverse engineering, and correctness comes free because it is the vendor's own implementation.

> **Load from the local install, not a copy on a mapped drive.** .NET refuses assemblies from a network location with `0x80131515`; a Google Drive letter counts as remote. This cost a confusing failure before the local path was tried.

### What has been found

`DEScribe.Upload.dll` → `DEScribe.Upload.Programmer`, with two static factories:

```
OCC CreateForDNA(NHW sha1l96Cache)
OCC CreateForDNAColor(NHW sha1Cache)        <- our board family
```

The returned object carries the device link. Most of the assembly is obfuscated (types named `A.OCC`, `A.TOC`), but the members that matter kept their names:

| Member | Reading |
|---|---|
| `Initialize()` | Bring the link up |
| `UserModeVersion` | Matches the `User mode version is …` line in EScribe's debug log, which is how we know this object really is the device connection |
| `Stream` | The underlying device stream |
| `UpdateBegin(bool writable)` / `UpdateCommit()` / `UpdateEnd(bool writable)` | A transaction around a settings change. The `writable` flag is the read/write switch |
| `PrepareUpload(DoUploadPrepareCallback)` → context | Builds an upload |
| `PerformUpload(context, IProgressMonitor, bool dontUpload)` | Executes it — **note the `dontUpload` dry-run flag** |
| `AX(IProgressMonitor, bool[])` → `TOC` | Unidentified; the shape suggests the download/read side |

### Resolved 2026-10-30 by reflection - three of the four

Still inert: nothing below has been executed, only enumerated.

**1. `NHW` is an interface, so we supply it.** `A.NHW` in `DimensionEngineering.Common.dll` has a null
base type and no constructors, and exactly two members:

    byte[] AE(byte[], Nullable<T>)
    void   FE(byte[], int, int, out byte[])

That is a SHA-1 cache contract - the uploader hashes each region so it can skip chunks that have not
changed. We do not need to find an instance: implement the interface, or try `null`. The parameter is
even named `sha1Cache` in `CreateForDNAColor`, which is the one name the obfuscator left alone.

**2. The device link is `OCC.Stream`, type `A.POT`, and it is settable** (`CanWrite = True`). So the
programmer does not have to discover the device - we can open one and assign it.

**3. The opener is `A.BGQ.FE(String, Int32, Int32, Int32, CSH, Int32, IGI) -> POT`** in
`DimensionEngineering.Common.dll`. A string path followed by VID/PID-shaped integers: a HID open by
device path. The path is the one Windows reports, `HID\VID_268B&PID_0433&MI_00\...`.

**4. Reading is `AX(IProgressMonitor, bool[]) -> TOC`,** and `TOC` takes `ctor(byte[])` / `ctor(int)`,
so it wraps a settings image. `OX(int)` and `WX(int, int)` also return `byte[]` and look like
region/range reads.

**Still unknown:** whether any of it runs outside EScribe's process and licensing. That is now the
single open question, and the read path answers it without risking a write.

### The memory model, which came out unobfuscated

`DEScribe.Upload` has exactly four public, unobfuscated types - the intended API:

| Type | Shape |
|---|---|
| `Programmer` | The two factories |
| `Layout.LogicalLayout(IEnumerable<LogicalRegion>)` | `Regions`, **`PCSize`**, **`PCSizeUsed`** |
| `Layout.LogicalRegion(method, size, deviceOffset, pcOffset, noCache, hashWholeRegion, hashChunkSize, tag, readOnly)` | One flash region |
| `Layout.PagingMethod(isPaged, pageSize, minipageSize, sectorSize)` | With named presets: `ReadOnly`, `EEPROM`, `AtmelSAMD21`, **`NuvotonM480`**, `STM32F3`, `STM32H5` |

Two things fall out of this.

**`PCSize` / `PCSizeUsed` is what the Space Used dialog reports** - the memory percentage every release
is checked against (`00`). If the read path works, that number becomes a scriptable check instead of a
dialog someone has to open.

**The board is a Nuvoton M480 family part**, on the evidence of the preset list and the DNA Color
generation - worth confirming, not yet confirmed.

And the design is a **differential uploader**: regions are hashed, and only changed chunks go over the
wire. That explains the SHA-1 cache, and it means an upload is not a blind whole-image write.

### Tested 2026-10-30, in and out of process

Device plugged in and confirmed `Present: True` on all four interfaces; serial baseline
`DNA 100 Color`, cold ohms 0.464, setpoint 385F, 186 puffs.

**`CreateForDNAColor(null)` works.** The SHA-1 cache may be null, so question 1 is closed twice over.
It returns an **`A.ECC`** - so `OCC` is the base and `ECC` the DNA Color implementation - with
`Stream = null` and `UserModeVersion = null`, waiting for a link.

**`HLF.XK()` is not a device list.** It returns an `A.QMQ` holding two empty byte arrays and
`XE = 256`, and `HLF.GK()` also returns 256. That is the hash chunk size, and `QMQ` is the SHA-1 chunk
cache itself. At the time this read as *"`CreateForDNAColor(HLF.XK())` is the intended call"*; **that is
superseded** - the Programmer must come from `PYB.UE(...)` so it carries a layout, and
`CreateForDNAColor` does not set one. What stands is the identification of `QMQ` as the SHA-1 chunk
cache and `XE = 256` as the chunk size. `GK()` is not a device count as its shape suggested.

**`HLF.AS` is null even inside Device Monitor**, with the mod connected and live. So the static
current-device slot is not what Device Monitor's own connection uses, and finding the live link means
looking at the script host's `ECig` object instead.

**Out of process the device layer is simply not initialized** - `HLF.AS` throws. Nothing here works
from a standalone script without reconstructing EScribe's startup through obfuscated code.

### `BVF` is the board registry

`A.BVF` is a sealed class with **16 static instances** - against 17 firmware folders in the install
(`13`), so very nearly one per supported board. Each carries two fields:

| Field | Type | What |
|---|---|---|
| `IE` | `A.CSH` | wraps `Dictionary<A.WSH, object>` from **HidSharp** - that is HidSharp's `OpenConfiguration` / `OpenOption` pair |
| `KE` | `A.VLF` | an enum board code. Values seen: `3`, `131`, `195`, `259`, `1027`, `2051`, `2179` - every one with low byte `0x03` |

Which instance is the DNA 100 Color is not yet known; they are distinguishable only by that code.

### EScribe's HID transport is HidSharp, and that changes the shape of the problem

`HidSharp, Version=2.6.4.0` ships in the install (`HidSharp.dll`, plus `HidSharp.Net.dll` and
`HidSharp.NordicDfu.dll` for the Bluetooth boards). It is **open source**, so although Evolv obfuscated
their copy in place, the library itself is public and documented.

That means `A.BGQ.FE(String, Int32, Int32, Int32, CSH, Int32, IGI) -> POT` is a thin wrapper over
"open this HID device path with these options", and **we never need Evolv's transport code**. A
standalone client can open `MI_00` with stock HidSharp from NuGet, or Python `hid` / `pywinusb`.

What is *not* solved by that is the **protocol** carried over the HID reports. Evolv's 2015 statement
says HID is serial tunneled over HID, which would mean the same `LETTER=ACTION` text we already drive
on COM4 (`17`) - and that gives us nothing new, because text cannot carry a settings image. EScribe
plainly moves binary settings across the same link, so either the tunnel carries more than text or the
upload uses its own report. **That question is now the crux, and it is the one thing reflection cannot
answer.** It needs a capture.

### The next experiment: read, not write — CORRECTED 2026-10-30

> **Step 2 below was wrong and following it reproduces the original failure.**
> `Programmer.CreateForDNAColor` returns a Programmer with **no layout**, which is precisely why
> `AX()` threw `NullReferenceException` every way it was tried (see *What fails, and why*). The
> Programmer has to come from `PYB.UE(...)`, so that it carries the layout `PE()` now gives us.

The read path exercises the entire chain - open HID, attach the stream, `Initialize()`, pull an
image - with nothing written to the device. Corrected order:

1. build the `PYB` with no device involved: `GGQ(XElement)` -> `UWB.FE(ggq)` -> `JSL(None, ggq, None)`
2. **`pyb.UE(func, int)` -> `OCC`** - a Programmer that *has* the layout. **Not**
   `Programmer.CreateForDNAColor`, which is the layout-less one
3. `BGQ.FE(hidPath, ...)` -> `POT`, and assign it to `OCC.Stream`
4. `OCC.Initialize()`, then read `UserModeVersion` - if it matches the `User mode version is ...` line
   in EScribe's debug log, the link is genuinely up
5. `OCC.AX(progress, flags)` -> `TOC`, and compare its bytes against a `.ecig` downloaded by EScribe

A successful read answers the licensing question, proves the HID path, and costs nothing if it fails.
Only then is `PerformUpload(ctx, progress, dontUpload: true)` worth trying.

**The device must be plugged in.** Checked 2026-10-30: all four Evolv interfaces read `Present: False`
with the mod unplugged, so step 1 has nothing to open.

---

## Risk boundary

Enumerating types and reading properties is inert. **Calling the upload path is not.** This is the component that writes firmware and settings to a battery-powered device; a wrong call could leave the mod unbootable.

So:

- **Reading is fair game** — `Initialize()`, `UserModeVersion`, enumeration, and anything that only observes.
- **Writing needs a deliberate decision each time**, and `PerformUpload`'s `dontUpload` flag should be exercised first. Treat a successful dry run as the gate for a real one.
- **Have a recovery path open before the first write.** EScribe's automatic backups (`13`) hold a config from before every upload, and firmware images for this board sit in `Firmware/DNA 100 Color/`.

---

## The Serial Terminal talks to the mod, not to COM4

A correction to the assumption in `13`. The Serial Terminal's **Connect** dialog lists three devices:

- **Gremlin** - the mod itself, named for its loaded theme
- Communications Port (COM1)
- USB Serial Device (COM4)

So it is not only a COM-port terminal: it connects to the **DNA directly**, and that is what the window
titled *Serial Terminal - Gremlin* with "Connected." was attached to. Which also explains why a
listen-only probe of COM4 heard nothing - the mod's command channel is not that port.

The dialog also offers **Rename...** and **Identify**, plus a *Wiring Information* link. **Identify
toggles the mod's display on and off** - a device command with an unmistakable effect, issued from
EScribe over its own link.

That matters more than it looks. It is a **known command with an observable result**, which is the
ideal thing to hunt for when working out a protocol: trigger it repeatedly and whatever changes in the
traffic is the command. If the HID route needs a USB capture, Identify is the signal to capture.

### Tested 2026-10-30: the Gremlin connection answers nothing either

Serial Terminal connected to **Gremlin**, status "Connected." Sent `?`, `help`, `hello`, `dir`, `ls`,
`/`, `/help`, `/?` and an empty line. Every one appeared in the Data pane; **none produced a reply**.

**Resolved:** the View menu has **Local Echo** and it was **on**, so every one of those lines was
EScribe echoing. The mod sent nothing at all - not even an error - and that test said nothing about
the device.

**The display mode is worth knowing about.** View -> Display offers **Text, Decimal, Hexadecimal**
**and CSV**; when seen set to CSV the Send button reads "View CSV". That was the operator experimenting rather than the state during the test, so it does **not** explain the silence - but anything the mod
emits that is not plain text would still be invisible in Text mode. Before concluding this channel is
dead: **turn Local Echo off, set Display to Hexadecimal**, and watch while the mod is idle, while
buttons are pressed, and while it fires.

Either way the text-console idea is finished, for both COM4 and this connection. **The HID protocol is
the remaining road**, and `Identify` - which visibly toggles the mod's display - is the command to
trigger while capturing.

The Serial Terminal's **Scripting** menu is still unopened and is the last cheap thing in this corner.

### What to try next, in EScribe's own UI

Cheaper and safer than writing raw bytes: connect the Serial Terminal to **Gremlin** and use its
**Command** box. A bare `?` or `help` costs nothing and may print the command set outright. The window
also has its own **Scripting** menu, unmapped, which may already be the structured interface this whole
effort is looking for.

### SOLVED 2026-10-30: COM4 is the command console

**Everything in this section's earlier conclusions was wrong, and the error was ours.** COM4 returned
nothing to `?`, `help`, `dir` and friends, and that was read as a dead channel - possibly a path to
external serial hardware rather than to the mod.

It is the mod's command console. The commands are `LETTER=ACTION`, and **an unrecognised command draws
no reply at all**, so every probe looked like silence. With real syntax the board answers immediately:

```
R=GET COLD     ->  R=0.464OHM
E=GET PRODUCT  ->  E=DNA 100 Color
M=GET          ->  M=1
```

**This is the goal of this document, reached.** Full detail, the verified command table and the
`tools/dna-query.ps1` helper are in `17`. What follows below is kept for the record of how the HID
route was scoped, which is still the right path for *writing* a config - but for reading the device
and driving it, the serial console is the answer and needs no reverse engineering at all.

## The serial fallback

COM4 is a standard CDC port (9600 8-N-1, Microsoft's `usbser`), so `System.IO.Ports.SerialPort` reaches it from PowerShell with no extra tooling — confirmed available on this machine. A listen-only probe is written and waiting on the mod being plugged in; it asserts DTR and RTS, which CDC devices often require before they say anything, and writes nothing.

If the port turns out to be a text console, it may be the shorter path to a working CLI regardless of the HID work. Its **Scripting** menu in the Serial Terminal hints that Evolv already exposes something structured over it.

---

## Other options, weighed

- **USB capture** (USBPcap/Wireshark) of EScribe doing a real transfer would reveal the HID protocol exactly, without fighting obfuscation. Heavier setup, but it is the method that cannot fail.
- **Reimplementing HID from scratch** in Python needs a package (`hidapi` or `pywinusb`); none is installed, and pip is available. Only worth it once the protocol is known.
- **Device Monitor's Python** (`14`) already gives live read *and write* of running values, but it is GUI-bound, so it does not reach the goal on its own.
