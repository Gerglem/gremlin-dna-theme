# 08 – Build Pipeline (how Gremlin is generated)

Gremlin is generated **entirely in Python**. Theme Designer is only used to inspect results and discover field IDs.

## Build kit
The build kit (Python scripts) is kept private; it isn't included in this public repo. The format and design docs here are enough to rebuild it.

**Setup in a Claude container:** unzip into `/home/claude/` (the scripts use absolute paths under `/home/claude`), then:
```bash
cd /home/claude/build && python3 assemble.py   # writes /mnt/user-data/outputs/Gremlin-v1.0.ecigtheme
```
Change the output filename in `assemble.py` (search for `Gremlin-v`) for each new version. The build writes `Gremlin-v<version>.ecigtheme`; the copy published in `../release/` is renamed to `gremlin_v<version>_theme.ecigtheme` to match the other release filenames.

## Files
| Path | Role |
|---|---|
| `theme/out.xml` | **Skeleton** theme XML — a copy of the released Gremlin theme, so the kit bootstraps from its own output. Supplies the wallpapers, the `<Normal>` color pair, `<Fading>` and the (empty) LED block. `assemble.py` replaces the fonts, all designs, the highlight/selection/error colors, title, comments and localization. The battery-bar PNGs are read from its design 2. |
| `deftheme/deffont{0,1,2}.xml` | Evolv Built SemiBold font XML (Normal 18 / Big 24 / Small 13), extracted from the default `.ecig` |
| `build/build.py` | XML helpers: `ctl()`, `field()`, `label()`, `picture()`, `toggle()`, `meter()`, `design()`, `b64img()`, `line()`. `color=None` omits the color. |
| `build/screens.py` | Main, lock, and new-coil screens. Assets: battery bar plus a red-outline variant (`LOWBAR_XML`), `outline()`, gremlin image, icons |
| `build/menus.py` | MENU/PROFILE/PREHEAT/DISPLAY/LOCK/INFO/CLOCK. Row helpers: `row_field`, `row_toggle`, `row_link`, `row_back`. ON/OFF images. Layout: `RH=15`, `Y0=21` |
| `build/assemble.py` | Puts it together: fonts → designs 1–3 → strip UsageFlags 128 from non-main designs → strip explicit white and help `Status=` → ColorScheme (highlight/selection/error) → title/author/comments → rebuild `<UIDesigns>` with menus (IDs 4–10) → clear Localization → zip |
| `icons/px.py` | 12×12 pixel-art icon grids (`ICONS`: info, sun, replay, gear, lock_on, lock_off, cold, live, ohm), `icon(name,color)`, `tile(icon,label,w,h)` |
| `icons/mk.py` | 3×5 pixel font `F` + `label()` used for the tile captions |
| `mock.py` | Loads the Built fonts for rendering text into images (`text()`, `tw()`) |
| `render.py` | Approximate screen previewer: `render(xml_path, '2' or 'id5', scale, active=(field ids…))` → PIL image |
| `theme/fontlib.py, gen.py, gen2.py` | Font tooling: decode font XML, generate bitmap fonts from TTF (used during the font experiments) |
| `gremlin/draw.py`, `gremlin_head.png` | Original gremlin pixel art (60×44) |

## v2.x additions (Color Themes and High Contrast)
The private kit (the maintainer keeps `gremlin-build-kit-v2.1.zip`; verified to rebuild both released themes byte-for-byte) adds:
| Path | Role |
|---|---|
| `build/skins.py` | Palettes (`PAL`), `SKINS` (theme name → User Toggle field), `COLOR_SKINS`, `skinned()` and `skinned_img()` that append one Compare-gated variant per theme, `add_cmp()` |
| `build/screens_skinned.py` | Themed home and lock screens: battery bars per theme, icon and gremlin recolors, FIRING box, LOW BATTERY banner |
| `build/menus.py` | Menus; titles and dividers themed via `_sktitle` / `_sktline`; THEMES screen (design ID 11) |
| `hc/fonts.py` | High Contrast fonts: Built 24 (missing glyphs synthesized from Built 18 ×4/3), Built 24 ×1.5 for temperatures only, Built 18 |
| `hc/build_hc.py` | Whole High Contrast theme in one script (4 screens) |

Commands: `cd build && python3 assemble.py` (Color Themes) and `cd hc && python3 build_hc.py` (High Contrast). Both strip LED color sequences and clear Localization.

**Without the kit:** `04`, `05`, `06`, `10`, `11` plus a released `.ecigtheme` (unzip it; every screen is base64 XML) are enough to rebuild or edit by hand.

## Testing and device tools (`../tools/`)

None of these are part of the build; they are how a build gets checked.

| Tool | What it does |
|---|---|
| `dna-hid.py` | Read and drive the mod over the vendor HID interface. Needs `pip install hidapi`. Works where the serial port does not, notably macOS (`16`, `17`) |
| `dna-query.ps1` | The same read-out over the USB serial port |
| `dna-stream.ps1` | Captures the 64 Hz CSV stream (switch EScribe to CSV first) |
| `make-bench-config.py` | Builds a throwaway `.ecig` that pre-locks a chosen resistance on each profile. **The only way to exercise the replace warning**, since published configs ship cold ohms 0 (`12`). Do not fire on one; do not commit one |
| `check-theme.py` | **Structural gate. Run before any release.** Fails a build where any control exceeds the child ceiling of 8 (`07` #26, measured), or paints explicit white on a selectable control, where the highlight makes it invisible (`07`). Warns at exactly 8 children, where a seventh color theme would break the control. Reads both `.ecigtheme` and `.ecig`; verified to fail `v1.2.06` and pass `v1.2.07` |
| `probe_pyb.py` | Inert IronPython probe for Device Monitor. Hunts a live `PYB` via **static** fields and properties. **Run 2026-10-30: type found, no live instance** - which rules out a static route, not a live object (`09`) |
| `probe_pyb3.py` | The follow-up, and the one to run. Walks instance fields from **live objects only** (`Application.OpenForms`), so no static constructor can fire (`07` #28). Interruptible - honours `Script.ShouldStop` - and gives up after 20 s. **Open a config in EScribe first** |
| `probe_contention.py` | Borrows the link Device Monitor already holds instead of opening a second handle, and gives `AX` a real progress monitor. Closes nothing |
| `probe_read3.py` | Walks the Programmer's whole type chain with `DeclaredOnly` so inherited private members show, sets `UserModeVersion` as the `Int32` it actually is, and makes one `AX` attempt |
| `probe_read2.py` | The read, second attempt: dumps every property on the Programmer, sets `UserModeVersion` by hand, and retries `AX` with a properly shaped `Boolean[]`. Capped at two attempts, since each timeout costs bench time |
| `probe_ue_sweep.py` | Tries `UE`'s `Int32` across all 256 byte values and reports what `NDY` is. Passes a null `Func`, so it cannot reach the device |
| `probe_address.py` | Hunts the invalid `address` that stops `UE`: reads each memory area's fields, lists `DDY`'s constructors, and retries `JSL` with a correctly marshalled document. Device-free |
| `probe_pyb_state.py` | Why `PYB.UE` throws before it uses the link. Dumps the `PYB`'s members and retries `JSL` with a real document as its first argument. Device-free |
| `probe_read.py` | **Step 3, and the first that needs the mod.** Opens a link, builds a Programmer that carries the layout, `Initialize()`, then `AX()` to download the settings image. Read-only: no `PerformUpload`, no write, no erase |
| `probe_programmer.py` | Step 2: `PYB.UE(...)` for a Programmer that **carries** the layout - the thing `CreateForDNAColor` could never produce. Opens no link, assigns no Stream, calls nothing on the device |
| `probe_layout.py` | **The payoff, and it worked (`16`).** Builds a `GGQ` from an `.ecig` root, asks `UWB.FE` for the right `DWB`, calls `JSL` for a `PYB` and dumps `PE()` - the real flash map. Exercises the upload-path objects but opens no link and uploads nothing; the mod need not be connected |
| `probe_dwb3.py` | The 25 subclasses turned out to be stateless, so this checks **properties** for the device code and looks for a **dispatcher** that hands out the right `DWB`. Calls getters, filtered and bounded; device-free |
| `probe_dwb2.py` | Identifies **which** concrete `DWB` subclass is the DNA100C, by constructing each and reading its fields for device code 109. **Constructs types** - less inert than the others, bounded and device-free; see its header |
| `probe_dwb.py` | **The current line of attack.** Three probes failed to find a live `PYB` because the script host cannot see EScribe's document at all; this asks instead whether a **concrete subclass of `DWB`** exists, which would let a `PYB` be built from our own `.ecig`. Metadata only - no value reads, no invokes |
| ~~`probe_pyb2.py`~~ | **Deleted.** It froze EScribe by reading every static field in the assemblies, which runs every type initializer (`07` #28) |
| `probe_open_link.py` | The proven recipe for opening a device link from inside EScribe and attaching it to a Programmer (`16`). Reads the port string from `dna-port.txt` |
| `samples/` | A real puff recording, and the device-to-PC half of a settings upload |

## Common changes
- **Move or resize a home element:** edit its `ctl(x,y,w,h, …)` in `screens.py`.
- **Add a menu row:** add `row_field/row_toggle/row_link` in `menus.py` (rows are 0-based, max ~8 per page with BACK).
- **Add a screen:** add a design string to `menus.NEW` with the next ID, and link to it with `ChildScreen Screen="<ID-1>"`.
- **New field:** find its ID (see `05`). If unsure, ship a small test build first. **An unsupported field blocks upload.**
- **Colors:** controls use float RGBA strings. ColorScheme uses ARGB ints (`0xAARRGGBB` as decimal).
- **Preview:** `python3 -c "import sys;sys.path.insert(0,'/home/claude');import render;render.render('build/gremlin.xml','2',scale=5).save('x.png')"`. Update `render.SAMPLE` with field → sample text.

## Profile and material generation
- **Profiles:** zip `ECigProfile.xml` (see `03`). Helper code is in the session history; trivial to regenerate.
- **Material CSV for TCR t:** see `02`.

## Reproducibility
Rebuilding an unchanged source tree gives a theme that is **not** byte-identical to the previous build: Pillow re-encodes every PNG, so the base64 payloads shift. Decoded pixels and all non-image XML are identical. Compare decoded images, not bytes.

## Process that worked
1. Make the change → build `Gremlin-v<next>.ecigtheme` → render a preview → present the file.
2. Upload it to the mod, test, and photograph the screen.
3. Bisect when something fails (test builds that remove one variable at a time).
