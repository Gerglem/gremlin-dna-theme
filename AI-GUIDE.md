# Working with an AI assistant on this project

Everything in this repo was built with an AI assistant, and the docs are written so you can do the same: customize the theme, make TCR curves for other heaters, build profiles, or troubleshoot a chip swap.

## Step by step
1. **Pick an assistant that can work with files and run code.** Claude (with file creation/analysis) or ChatGPT (with code interpreter) both work. Theme files are zipped XML, so the assistant needs code execution to read and rebuild them.
2. **Start a new chat and upload all of the `kb/*.md` files.** Tell it to read `kb/00-README.md` first. Those files contain the theme format, DNA field IDs, design spec, calibration method, and known pitfalls.
3. **Upload the files you want changed:** a theme from `release/` or `high-contrast/files/`, a `.ecigprofile`, or a material `.csv`.
4. **Describe your setup and goal.** Include your DNA chip, firmware edition, heater, and what you want. Example prompts:
   - *"Read these files. My mod is a DNA75C on international firmware. Make me a TCR 180 material CSV for a standard V5 cup, and a matching profile."*
   - *"Using the theme format and field IDs in these docs, change the Gremlin home screen to show battery voltage instead of the session time."*
   - *"I'm doing the Thelema chip swap and the screen stays blank after power-up. Walk me through troubleshooting."*
5. **Ask for a new mini version on every build** (e.g., `gremlin_v2.2.03_theme.ecigtheme`) so you can tell builds apart and roll back.
6. **Load the file in EScribe, upload it to the mod, and test.** Send photos of the screen back to the assistant and describe what's wrong. Expect a few rounds. That's how Gremlin was built.

## Two themes
- **Gremlin - Color Themes v2.2** (`release/`): seven switchable looks.
- **Gremlin High Contrast - Large Text v1.2** (`high-contrast/`): built for low vision.
Tell the assistant which one you're changing.

## Tips
- **Check memory before uploading:** in Theme Designer, click **Space Used** with your chip selected (the DNA75C has the least room). Both numbers must be under 100%.
- **Test new fields in a small build first.** If EScribe says *"No Compatible Firmware,"* the theme uses a field your firmware doesn't support. Ask the assistant to bisect by removing suspect fields one at a time (`kb/07`).
- Field IDs marked **M** (medium confidence) in `kb/05` are inferred. Verify them on your device.
- **Be specific when reporting problems.** Say which part of the screen you mean, and include a photo.
- Keep a backup of your working setup (`File → Save` in EScribe) before uploading anything new.
- Calibrate with the swab test (`kb/02`) on your own mod. TCR values don't transfer between mods.

## Safety
Don't rely on an AI for battery or soldering decisions without verifying polarity and continuity yourself. Never let a theme or profile override your mod's battery cutoff. You're responsible for anything you do to your hardware.
