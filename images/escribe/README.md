# EScribe and Theme Designer screen captures

Reference captures from the 2026-10-30 mapping session, kept because the GUI is the only
documentation Evolv provides for most of this and the findings in `../../kb/15` were read off these.

Every file here was viewed and checked for the board serial number and any identifying content before
being committed (`../../kb/12`).

## Theme Designer

| File | What it shows |
|---|---|
| `escribe-td-appearance-tab.png` | Appearance tab - wallpaper slots, Color Scheme, the three font slots, Fading, Text Positioning |
| `escribe-td-screens-special-usage-dropdown.png` | Screens tab with **Special Usage open: None, Lock Screen, Main Screen, New Atomizer, Power Lock, Theme Change** - all six. Also shows the `Screenshot` button |
| `escribe-td-control-field.png` | Field panel, plus the control dropdown listing a screen's tree |
| `escribe-td-control-memo.png` | Memo panel - a multi-line Label |
| `escribe-td-control-chart.png` | Chart panel - `Time Bars` is its only setting |
| `escribe-td-control-toggle.png` | Toggle panel - per-control On/Off images with their own Load/Save/Actions |
| `escribe-td-setting-dialog.png` | The **Setting** dialog both Source buttons open: Field, Decimal Places, Zeros, Step Size, Swap up/down, Don't show units, Selectable |
| `escribe-td-setting-field-source-list.png` | The Field source list open - the catalog `kb/15` reconstructs |
| `escribe-td-setting-decimal-places.png` | Decimal Places: Automatic, 0-4 |
| `escribe-td-condition-math-menu.png` | Condition editor **math menu** - the full function list including `if()`, `known()`, `unknown()`, `discretize()` |
| `escribe-td-condition-and-expression.png` | A condition written as an expression: `Cold Ohms > 0.4 and Profile = 1` |
| `escribe-td-condition-field-to-field.png` | Attempting `Atomizer -> Temperature > Miscellaneous -> Board Temperature` |
| `escribe-td-condition-must-be-a-number.png` | …and its rejection: **"Must be a number!"** - the right-hand side of a comparison must be a literal |

## EScribe

| File | What it shows |
|---|---|
| `escribe-general-tab-upload-button.png` | General tab and **Upload Settings to Device**; profile fields, Coil material, Cold Ohms with its Locked box |
| `escribe-research-tab.png` | Research tab - Data Acquisition and Experimental Setup |
| `escribe-research-serial-output-format.png` | **Serial Output Format** open: *Plain Text Serial* and *CSV (Excel)* are mutually exclusive |

## Not committed

One capture from the session is deliberately excluded: a file-open dialog that listed personal folder
names. It is in the private archive only, alongside the device photographs from the bench tests, at
`../../../escribe-screenshot-archive/` (outside this repository).
