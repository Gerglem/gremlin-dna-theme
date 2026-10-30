# 07 – Gotchas and Lessons Learned (read before editing the theme)

## Firmware / chip behavior
1. **"No Compatible Firmware" on upload** means the theme references a field the firmware doesn't support. Find it by bisecting: build variants that remove suspect fields one at a time. Culprit found: **Heating Time Done (353173506)**.
2. **Puff Time can't be displayed.** Theme Designer saved its ID as `0`, and setting it as a Field source **crashes Theme Designer** (InvalidOperationException). On the mod, the field renders blank.
3. **Live ohms (1048642) and atomizer amps (131138) read 0** when idle after boot **and during the first session after power-on**, even while the cup is heating. **Don't use them to detect "no atomizer."** Every attempt gave false positives on the first fire. There's no field that reports atomizer presence before firing.
4. With **no atomizer**, fire still enters the session state (no power flows). The chip's own Status says "No Atomizer."
5. **Status Displayed (1048582)** is true at boot (blank text) and for about 1s after firing. A `Status` element placed **inside a conditional** rendered **blank**. Only an **unconditional `<Status/>` in its own control** shows the text ("Firing," "No Atomizer").
6. The **Status element paints an opaque background** when active, covering anything beneath it. **Labels also paint opaque backgrounds**, while Pictures with transparency don't. Overlapping controls produced missing boxes and hidden text.
7. The Status element **also shows the `Status="…"` help text** of whatever control is highlighted, and it got cut off. Strip all help-text attributes.
8. **`Status Color` works** (the reddish amber "Firing" on v0.24). The earlier blank-text failure was caused by putting it in a conditional, not by the color.
9. Built SemiBold **Small** needs **≥19px** control height for Status text, or the tops of the letters get clipped (v0.21 → v0.22 fix).
10. Fire on non-main screens = **back one level** (not home) on this firmware.
11. With **ohm lock on**, the new-coil screen **doesn't appear** when the atomizer is swapped.
12. Fields **10 and 266 are User Toggles 1 and 2**, not step-size settings (they were mislabeled early on, which is why they "did nothing"). See `05`.
13. A populated **Localization** block forces d/M/yy. Clear it for US dates.
14. Session Mode needs **international firmware**. The theme won't upload without it.

15. **Fields wrap.** A value wider than its control wraps onto a second line, and anything past the control's height is cut off. Theme Designer shows this; the local preview (`render.py`) does not. Size controls from measured glyph widths.
16. **Pure black picture pixels are drawn as transparent,** and a **full-screen (80×160) picture is not drawn at all** while firing. To take over the screen, give every other control a Hidden variant instead.
17. **Controls redraw in layers while firing.** Live (`UpdateLive`) controls repaint over static ones. A "takeover" only works if every other control hides itself and is live.
18. **The Status element paints a solid background almost constantly,** even with no message. Never overlap it with anything you want visible; give it its own row.
19. **Two memory pools.** Images and fonts use **off-board** memory; controls and condition variants use **on-board**. Check both with Theme Designer → Space Used, on the **DNA75C** (least room). Recolored images are expensive off-board; text color variants are cheap.
20. **Evolv's large font (24 px) has only ~56 characters.** It lacks I, G, E, D, L, U and more. Use it for numbers, or synthesize missing glyphs.
21. User Toggles are **not** saved in `.ecig` exports; they live on the device.

## Theme building
- Explicit `Color="(1, 1, 1, 1)"` on selectable items keeps text **white on the white highlight** (invisible). Omit the color for default white.
- White icons vanish on a white highlight, so **outline them in 1px black**.
- Fonts: render or bitmap at the target pixel size. Horizontal condensing caused blur, and "pixel-hard" thresholding at small sizes was unreadable. Evolv's own Built SemiBold.
- The ChildScreen index is **design ID − 1**, not list position.
- Keep the zip entry `ECigTheme.xml`, UTF-8 BOM, and `\r\n` inside screen XML.
- Previews: the local Python renderer (`render.py`) is approximate. Theme Designer's preview is reliable for layout. On-device photos are the final truth.
- **Don't reproduce known characters/IP in art.** The gremlin is an original creature design (not movie Gremlins).

## Tool/process
- Theme Designer: **Add Condition → measurement** lists every field by name. That list plus labeled test files is how IDs were mapped.
- The Lightning **Quest** and Lightning **Pen** cups are different heaters with different settings.
- Pico TCR values don't transfer to the DNA. Recalibrate with the swab test.
