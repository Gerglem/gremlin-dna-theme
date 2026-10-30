# 17 – The plain-text serial command interface

**The mod is a command console.** It answers plain-text commands over its USB CDC serial port, with no EScribe involved. This is the direct, scriptable control of the device that `16` set out to find.

Verified on this DNA 100 Color, firmware SP55.1 INT, 2026-10-30.

---

## Connecting

The mod enumerates as a USB composite device (`13`); the second interface is a standard CDC serial port (COM4 on this machine, Microsoft's stock `usbser` driver). **9600 8-N-1**, assert DTR and RTS, terminate commands with **CRLF**. Replies come back terminated the same way.

No driver install on Linux — the port is standards-compliant CDC. On Windows the EScribe install provides it.

From PowerShell, no extra tooling needed:

```powershell
$sp = New-Object System.IO.Ports.SerialPort 'COM4',9600,'None',8,'One'
$sp.DtrEnable = $true; $sp.RtsEnable = $true; $sp.ReadTimeout = 400
$sp.Open()
$sp.Write("R=GET COLD`r`n")
Start-Sleep -Milliseconds 350
$sp.ReadExisting()          # -> R=0.464OHM
$sp.Close()
```

`tools/dna-query.ps1` in this repo wraps that.

## Syntax

`LETTER=ACTION`, and the reply echoes the same letter: `R=GET COLD` → `R=0.464OHM`.

**`LETTER=?` means the board has no value for that query** — not an error, and not an unknown command. `P=GET` returns `P=?` when idle because there is no live power to report.

**An unrecognised command gets no reply at all.** This is the trap that cost an afternoon: `?`, `help`, `dir` and friends were sent to this port and returned *nothing*, which read as a dead channel. The port was fine; the words were not commands (`07` #26).

---

## Verified on this board

Queries only. Everything below was run and its reply recorded.

| Command | Reply | Notes |
|---|---|---|
| `E=GET PRODUCT` | `E=DNA 100 Color` | |
| `E=GET VERSION` | `E=311105588` | The same number EScribe's debug log calls the user-mode version |
| `E=GET SERIAL` | *(the device serial)* | **Keep out of the repo** (`12`) |
| `E=GET MANUFACTURER` | `E=?` | Not populated |
| `B=GET` | `B=4.158V` | Pack voltage |
| `B=GET CELLS` | `B=1` | Cell count |
| `B=GET CELL 1` | `B=4.158V` | |
| `C=GET%` | `C=98%` | Charge percentage |
| **`R=GET`** / `R=GET COLD` | `R=0.464OHM` | **The locked cold resistance** |
| `R=GET STATIC` | `R=0.004OHM` | Fixed contact resistance |
| `R=GET LIVE` | `R=?` | Only meaningful while firing |
| `R=GET TYPE` | `R=1` | |
| **`T=GET COLD`** | `T=69.28F` | **The temperature cold ohms was measured at** — matches `ColdResistance2 Fahrenheit` in the saved profile exactly |
| `T=GET SP` | `T=385.00F` | Temperature setpoint |
| `T=GET BOARD` | `T=82.99F` | Board temperature |
| `T=GET ROOM` | `T=74.80F` | Room temperature |
| `T=GET` | `T=?` | Live temperature, idle |
| `P=GET SP` | `P=36.00W` | Power setpoint |
| `P=GET`, `V=GET`, `I=GET` | `?` | Live values, idle |
| `U=GET V` | `U=5.119V` | USB voltage |
| **`M=GET`** | `M=1` | **Active profile, 1-based** — independently confirms the numbering the theme conditions rely on (`05`) |
| `S=GET PUFFS` | `S=176` | |
| `S=GET TIME` | `S=4202.73S` | Total fire time |
| `S=GET ENERGY` | `S=23111.27MWH` | |
| `S=GET LASTPOWER` | `S=18.60W` | |
| `S=GET LASTTEMP` | `S=375.73F` | |
| `X=GET BUTTONS` | `X=0` | Button state bitmap |
| `X=GET MODE` | `X=0` | |
| `X=GET SCREEN` | `X=0.000` | |
| `X=GET TIMER` | `X=4870.68S` | Uptime |
| `W=GET` | `W=2026-10-30,21:31:53,2026-10-30,14:31:53,00010,UP` | Clock: UTC, local, then flags |

No reply at all, so unsupported on this board: `E=GET HARDWARE`, `R=GET NOMINAL`, `T=GET AIR`, `U=GET`, `U=GET A`, `X=GET BANDGAP`, `C=GET`.

## Not tested here — these change the device

Documented by the community and **not run**, because they write rather than read:

- `F=#S` — **fires the device** for # seconds
- `P=#W`, `T=#C` / `T=#F`, `T=OFF`, `T=MONITOR`
- `M=#` — switch profile (1–8)
- `U=#A` — USB current limit, 0 disables charging
- `V=#V`, `I=#A` — limits, **not retained across a power cycle**
- `S=RESET`, `X=RESET`

Treat all of these as live controls on a battery device. `F=` in particular fires the coil.

---

## What this unlocks

**Threshold testing without hardware gymnastics.** `R=GET COLD` reads the value the replace warning keys on, so the whole warning can be checked by reading the real number instead of inferring from the screen. If a write command can set it, the thresholds can be swept outright (`09`).

**The data the replace thresholds lack.** They rest on one observed failure (`02`). `R=GET COLD` plus `S=GET PUFFS` is exactly the pair worth logging — wear tracks use, not calendar time — and both come from one script with no GUI.

**A board temperature answer.** `T=GET BOARD` and `T=GET ROOM` both read, which settles the readability half of the question raised in `09`. Whether the chip warns on its own is still open.

**Cross-checks on what the theme sees.** `M=GET` confirms profiles are 1-based, and `T=GET COLD` matches the saved profile's measurement temperature — so this interface can verify the values a theme is reading, independently of the screen.

## Sources

The command set is community-documented, not official: <https://github.com/hobbyquaker/dna-commands> and the Evolv forum thread *Plain Text Serial commands*. The table above is what **this** board actually answered, which is the part to trust.
