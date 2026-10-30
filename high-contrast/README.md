# Gremlin High Contrast: Large Text Theme (v1.1)

A theme for Evolv DNA vape mods, made for people with low vision.

It uses large text, high contrast (white and yellow on black), and very few items on each screen.

This page explains what each file does, how to install it, and how to use the theme.

## Contents

1. What you need
2. Which file should I download?
3. How to download a file from this page
4. How to install the files
5. What each screen shows
6. Using the buttons
7. Changing your settings
8. If the screen says LOCKED
9. Tips
10. Getting help

## 1. What you need

- A mod with an **Evolv DNA color chip**: DNA75C, DNA100C, or DNA250C.
- The chip must run Evolv's **international firmware**, not the US version. This theme does not work on the US version.
- A computer (Windows or Mac) with Evolv's free **EScribe** software.
  - Download EScribe from Evolv's website: https://www.evolvapor.com/escribe
- A USB cable to connect your mod to the computer.

## 2. Which file should I download?

There are three kinds of files. You only need one of the first two.

### Option A: The full setup file (easiest)

- File: [Gremlin-High-Contrast-Full-Setup-v1.1.ecig](files/Gremlin-High-Contrast-Full-Setup-v1.1.ecig)
- What it contains: the theme **and** four ready-made profiles, all in one file.
- Choose this if you use Divine Tribe V5 XL cups or the Lightning Quest, and you want everything set up at once.
- Note: this replaces all the settings on your mod.

### Option B: The theme only

- File: [Gremlin-High-Contrast-Large-Text-v1.1.ecigtheme](files/Gremlin-High-Contrast-Large-Text-v1.1.ecigtheme)
- What it contains: only the screens, colors, and text size.
- Choose this if you want to keep your own profiles and settings. Only the look of the screen changes.

### Option C: Single profiles (optional)

A profile stores the settings for one heater: power, temperature, and session time. You can add any of these to your mod one at a time.

- [High-Contrast-Profile-V5XL-Cup.ecigprofile](files/profiles/High-Contrast-Profile-V5XL-Cup.ecigprofile)
  - Name on screen: **XL**
  - For: Divine Tribe V5 XL cups.
  - Settings: temperature control, 420°F, 36 watts, 60-second sessions.
- [High-Contrast-Profile-Lightning-Quest.ecigprofile](files/profiles/High-Contrast-Profile-Lightning-Quest.ecigprofile)
  - Name on screen: **QUEST**
  - For: the Divine Tribe Lightning Quest heater.
  - Settings: temperature control, 420°F, 25 watts, 60-second sessions.
- [High-Contrast-Profile-V5XL-Cleaning.ecigprofile](files/profiles/High-Contrast-Profile-V5XL-Cleaning.ecigprofile)
  - Name on screen: **XL CLEAN**
  - For: burning residue off a V5 XL cup.
  - Settings: 38 watts for 120 seconds. Hold the mod upside down. Let the cup cool completely afterward.
- [High-Contrast-Profile-Lightning-Quest-Cleaning.ecigprofile](files/profiles/High-Contrast-Profile-Lightning-Quest-Cleaning.ecigprofile)
  - Name on screen: **Q CLEAN**
  - For: burning residue off a Lightning Quest.
  - Settings: 35 watts for up to 45 seconds. Let it cool completely before running it again.

The temperature profiles also need a **material file**. The material file tells the mod how to read the heater's temperature.

- [dtv5xl-tcr200.csv](files/materials/dtv5xl-tcr200.csv): for the XL profile.
- [questcup-tcr125.csv](files/materials/questcup-tcr125.csv): for the QUEST profile.

## 3. How to download a file from this page

1. Select the file name to open its page.
2. Select the **Download raw file** button. On most screens it is near the top right of the file view.
3. Save the file somewhere easy to find, such as your Desktop.

If you use a screen reader, the button is labeled "Download raw file."

## 4. How to install the files

Before you start, connect your mod to your computer with the USB cable and open EScribe. EScribe should say your device is connected.

### To install the full setup file

1. In EScribe, open the **File** menu and choose **Open**.
2. Choose **Gremlin-High-Contrast-Full-Setup-v1.1.ecig**.
3. Select **Upload Settings to Device**.
4. Follow step 4 under "To add a single profile" to lock each cup's resistance.

### To install the theme only

1. Select the **Theme** tab.
2. Load **Gremlin-High-Contrast-Large-Text-v1.1.ecigtheme**.
3. Select **Upload Settings to Device**.

### To add a single profile

1. Select the **Materials** tab. Select **Import Material** and choose the matching material file:
   - **dtv5xl-tcr200.csv** for XL.
   - **questcup-tcr125.csv** for QUEST.
   - The cleaning profiles do not need a material file.
2. Make sure the material appears under **Materials on Device**. If it does not, select it and press the arrow button to move it there.
3. Select the **General** tab, choose an empty profile slot, select **Load Profile**, and choose the profile file.
4. Attach your heater while it is **cold**, at room temperature. Select **Measure Ohms**, then check **Locked**.
5. Select **Upload Settings to Device**.

Step 4 matters. The mod uses the cold reading to work out the temperature. A reading taken on a warm heater makes the mod run too hot.

## 5. What each screen shows

### Home screen

![Home screen. From top: MENU and battery 87 percent, a battery bar, profile name XL, live temperature 420 degrees in large yellow numbers, SET 420 degrees, and a blank status line.](images/home-screen.png)

From top to bottom:

1. **MENU** on the left, and the **battery percentage** on the right.
   - Below 15 percent, the percentage and the battery bar turn **red**.
2. A **battery bar**.
3. The **profile name**, for example XL. Long names use two lines.
4. The **current temperature**, in very large yellow numbers.
5. **SET** and your **set temperature**. This item is selected when the mod wakes up, so you can adjust it right away.
6. A **status line** for warnings, such as "No Atomizer" or "Battery Low."

### While firing

![Firing screen. The word TEMP, the live temperature in large yellow numbers, and the word FIRING in an orange box.](images/firing-screen.png)

When the mod is heating, the whole screen changes to show only:

- **TEMP** and the current temperature, very large.
- **FIRING**, in an orange box.

When heating stops, the home screen returns.

### Menu

![Menu screen. TEMP with 420 degrees, WATTS with 36 watts, LIGHT with 10, and BACK.](images/menu-screen.png)

- **TEMP**: your set temperature.
- **WATTS**: the power limit.
- **LIGHT**: screen brightness, from 1 to 10. Set it to 10 for the brightest screen.
- **BACK**: returns to the home screen.

### Lock screen

![Lock screen. LOCKED in yellow, then FIRE 5X TO UNLOCK, then BATTERY and 87 percent.](images/lock-screen.png)

When the mod is locked, the screen says **LOCKED** and tells you how to unlock it: **press the fire button 5 times quickly.** It also shows the battery percentage.

### New coil screen

![New coil screen. NEW COIL question, YES, NO, and MEASURE.](images/new-coil-screen.png)

This screen appears if you attach a different heater while the resistance lock is off.

- **YES**: this is a new heater.
- **NO**: this is the same heater. NO is selected by default, for safety.
- **MEASURE**: reads the heater again.

## 6. Using the buttons

The mod has four buttons:

- **Fire** (the large top button): starts heating. Press it again to stop. In the menu, it goes back.
- **Up** (top of the three small buttons): moves the selection up.
- **Select** (middle small button): selects or edits the highlighted item.
- **Down** (bottom small button): moves the selection down.

The selected item has a **solid yellow bar** with black text.

To change a value:

1. Use **Up** or **Down** to highlight it.
2. Press **Select**. The bar turns **white**. You are now editing.
3. Use **Up** or **Down** to change the value.
4. Press **Select** again to save.

## 7. Changing your settings

### On the mod

- **Set temperature**: on the home screen, or in the menu under TEMP.
- **Profile**: on the home screen, highlight the profile name and press Select. Then use Up or Down to switch.
- **Power and brightness**: in the menu.

### In EScribe, on your computer

Everything else uses standard settings. You can change these in EScribe:

- **Session length**: General tab, Session Mode, Time.
- **Battery cutoff**: Mod tab, Battery. We suggest 3.0 volts.
- **Profile names**: General tab, Name.
- **Auto-lock and the unlock button sequence.**
- **Clock settings.**

## 8. If the screen says LOCKED

The mod locks itself so it can't fire by accident.

- **To unlock:** press the **fire button 5 times quickly**.
- **To lock it yourself:** press the fire button 5 times quickly.
- **Auto-lock:** the full setup file turns auto-lock **off**, so the mod only locks when you lock it. If you installed the theme only, your mod may still lock itself after a few minutes of not being used. To turn that off, open EScribe, find the lock settings, and set Auto Lock to off. Then select Upload Settings to Device.

## 9. Tips

- **Keep profile names short.** About 8 letters fit on one line, and longer names use two lines. Examples: XL, QUEST, XL CLEAN.
- **Turn brightness up to 10** in the menu for the clearest screen.
- **No Atomizer** means the mod cannot detect the heater. Check that the heater is screwed on fully.
- **Firing with no heater attached is safe.** The mod sends no power. The status line shows "No Atomizer."
- **Back up first.** Before uploading anything new, save your current setup in EScribe with File, then Save.

## 10. Getting help

For questions or problems, open an issue on this project's GitHub page.

For setup, materials, and calibration details, see the main Gremlin guides in this repository.

The theme is free to use and share.
