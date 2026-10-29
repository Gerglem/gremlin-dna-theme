# 08 – Build Pipeline (how Gremlin is generated)

Gremlin is generated **entirely in Python**. Theme Designer is only used to inspect results and discover field IDs.

## Build kit
The build kit (Python scripts) is kept private; it isn't included in this public repo. The format and design docs here are enough to rebuild it.

**Setup in a Claude container:** unzip into `/home/claude/` (the scripts use absolute paths under `/home/claude`), then:
```bash
cd /home/claude/build && python3 assemble.py   # writes /mnt/user-data/outputs/Gremlin-v1.0.ecigtheme
```
Change the output filename in `assemble.py` (search for `Gremlin-v`) for each new version. The build writes `Gremlin-v<version>.ecigtheme`; the copy published in `../release/` is renamed to `gremlin_v1.0_theme.ecigtheme` to match the other release filenames.

## Files
| Path | Role |
|---|---|
| `theme/out.xml` | **Skeleton** theme XML — a copy of the released Gremlin theme, so the kit bootstraps from its own output. Supplies the wallpapers, the `<Normal>` colour pair, `<Fading>` and the (empty) LED block. `assemble.py` replaces the fonts, all designs, the highlight/selection/error colours, title, comments and localization. The battery-bar PNGs are read from its design 2. |
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
