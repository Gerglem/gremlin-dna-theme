# Capture the DNA's 50 Hz serial CSV stream.
#
# Enable it first in EScribe: Research tab -> Serial Output -> CSV (Excel),
# then upload settings to the device. See kb/17.
#
# This only listens. It writes nothing to the mod.
#
#   .\dna-stream.ps1 -Seconds 10
#   .\dna-stream.ps1 -Seconds 60 -Out puffs.csv

param(
    [string] $Port = "COM4",
    [int]    $Seconds = 10,
    [string] $Out,
    [int]    $Baud = 9600
)

$ErrorActionPreference = "Stop"

if (-not ([System.IO.Ports.SerialPort]::GetPortNames() -contains $Port)) {
    Write-Output "$Port not present."
    exit 1
}

$sp = New-Object System.IO.Ports.SerialPort $Port, $Baud, "None", 8, "One"
$sp.Handshake = "None"
$sp.DtrEnable = $true
$sp.RtsEnable = $true
$sp.ReadTimeout = 500
$sb = New-Object System.Text.StringBuilder

try {
    $sp.Open()
    Start-Sleep -Milliseconds 200
    $sp.DiscardInBuffer()
    Write-Output "listening on $Port for $Seconds s (nothing is being sent)"
    $deadline = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $deadline) {
        if ($sp.BytesToRead -gt 0) {
            [void]$sb.Append($sp.ReadExisting())
        } else {
            Start-Sleep -Milliseconds 20
        }
    }
} finally {
    if ($sp.IsOpen) { $sp.Close() }
}

$text  = $sb.ToString()
$lines = $text -split "`r?`n" | Where-Object { $_ -ne "" }

Write-Output ""
Write-Output "captured $($text.Length) bytes, $($lines.Count) lines"
if ($lines.Count -eq 0) {
    Write-Output "nothing arrived - is Serial Output set to CSV and uploaded?"
    exit 0
}

$rate = [math]::Round($lines.Count / $Seconds, 1)
Write-Output "approx $rate lines/second (50 expected)"
Write-Output ""
Write-Output "--- first 3 lines ---"
$lines | Select-Object -First 3 | ForEach-Object { Write-Output "  $_" }
Write-Output "--- last line ---"
Write-Output "  $($lines[-1])"
Write-Output ""
Write-Output "columns in the last line: $(($lines[-1] -split ',').Count)"

if ($Out) {
    $lines | Set-Content -Path $Out -Encoding utf8
    Write-Output ""
    Write-Output "written to $Out"
}
