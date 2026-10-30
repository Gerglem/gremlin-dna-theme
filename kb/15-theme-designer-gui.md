# 15 – Theme Designer: the GUI, mapped to the XML

Everything in this project is built by editing XML directly, so Theme Designer has mostly been a viewer. This maps its interface onto the file format, which matters for two reasons: it tells you what Evolv considers a first-class setting, and when something here has no XML equivalent we know about, that is a feature we have not found yet.

Built from screenshots, 2026-10-30. **Incomplete** — tabs and dialogs are added as they are seen.

---

## Window

**Menus:** File · Edit · Options · Tools · Help
**Toolbar:** New · Open · Save · Undo · Redo
**Actions:** `Apply` · `Download Theme` · `Upload Theme` · `Space Used` · a *Share Themes* link
**Tabs:** **Appearance** · **Screens** · **Indicator Light** · **Language** · **Credits**

The tabs line up with the top-level elements of `ECigTheme.xml` (`04`):

| Tab | XML |
|---|---|
| Appearance | `<Screen>` wallpapers, `<ColorScheme>`, `<UIFonts>`, `<Fading>` |
| Screens | `<UIDesigns>` |
| Indicator Light | `<UIColorSequences>` / LED track — **stripped from our releases** (`06`) |
| Language | `<Localization>` — **must stay empty** or dates force to d/M/yy (`07` #13) |
| Credits | `Author` and `<Comments>` on the root element |

`Space Used` is the memory check the release process depends on (`00`).

---

## Appearance tab

### Wallpaper — three slots

Slots 1, 2 and 3, each `Load…` / `Save…` / `None`, over the note *"Screens are 80 pixels wide and 160 pixels tall."* They are `<Screen ID="Wallpaper">`, `"Wallpaper 2"` and `"Wallpaper 3"`, each holding a base64 PNG. A `UIDesign` picks one with its `Wallpaper="n"` attribute; ours are all `Wallpaper="0"`.

### Color Scheme — the highlight colors live here, not on controls

Five rows, each a Text and a Fill swatch, three with an Opacity percentage:

| GUI row | XML element | What it does |
|---|---|---|
| Normal | `<Normal Text Background />` | Default text and background |
| Highlight Read-Only | `<HighlightDisabled … Opacity />` | A highlighted control you cannot edit |
| Highlight Selectable | `<Highlight … Opacity />` | **The selection bar.** Color Themes uses black on white; High Contrast uses black on yellow |
| Selected | `<Selection … Opacity />` | A control being edited |
| Error | `<Error Text />` | Error text; fill is not offered |

This is where the inverted highlight that every menu row depends on is configured — it is a **theme-wide** setting, not a per-control one, which is why no control carries highlight colors.

**Colors here are packed ARGB as an unsigned 32-bit decimal**, not the `(r, g, b, a)` float tuples used on controls. `4294967295` is `0xFFFFFFFF` white, `4278190080` is `0xFF000000` black. Two different color encodings in the same file — don't mix them up.

### Fonts

| GUI label | `FontStyle` | `UIFont ID` | Color Themes |
|---|---|---|---|
| Big Font | `1` | 2 | Built SemiBold 24pt |
| Normal Font | `0` | 1 | Built SemiBold 18pt |
| Small Font | `2` | 3 | Built SemiBold 13pt |

The GUI lists them Big, Normal, Small; the `FontStyle` numbers run Normal, Big, Small; the `UIFont` IDs run Normal, Big, Small. Three orderings for the same three fonts — worth re-reading whenever you touch font sizes. The sizes shown match `04` exactly, so that mapping is now confirmed from the tool and not just inferred.

### Fading

`<Fading ActiveTime IdleTime FadeInTime FadeOutTime />`, in seconds. Ours: active 30, idle 0, fade-in 1.

> **Discrepancy to resolve.** The GUI showed **Fade-out Time 0.7** while our file stores `FadeOutTime="2.97674418604651"`. Either the tool scales this value on load, or the theme open in the designer was not the one in `release/`. Don't edit fade timings by hand until this is settled.

### Miscellaneous — a setting we have no XML for

**Text Positioning: `Use pixel bounds (compatible)`**, a dropdown.

"Compatible" strongly implies a second, newer mode — presumably one that positions text by font metrics rather than by the rendered pixel bounds. Nothing in our themes' root attributes corresponds to it, so it is either stored somewhere we have not looked or only written when changed from the default.

**This is worth investigating.** Every layout in this project is built from measured glyph widths and hand-tuned control heights (`07` #9, #15), and a different positioning mode would change where text lands in its control. If the alternative mode centers text properly on its line box, some of the per-row fudging in the High Contrast layouts could go away.

---

## Not yet mapped

Screens tab · Indicator Light · Language · Credits · the condition editor and its operator list · the action editor · control property panels · Space Used · all five menus.
