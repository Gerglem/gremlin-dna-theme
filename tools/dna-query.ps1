# Query an Evolv DNA board over its USB CDC serial port.
#
# The mod answers plain-text commands of the form LETTER=ACTION. See
# kb/17-serial-command-interface.md for the verified command table.
#
# This script sends READ-ONLY queries. It refuses anything that looks like a
# write, because the same interface can fire the coil and change limits.
#
#   .\dna-query.ps1                          # a standard read-out
#   .\dna-query.ps1 -Command 'R=GET COLD'    # one query
#   .\dna-query.ps1 -Command 'S=GET PUFFS','R=GET COLD' -Csv log.csv
#   .\dna-query.ps1 -Port COM7 -AllowWrites -Command 'M=2'
#
# Find the port with: [System.IO.Ports.SerialPort]::GetPortNames()

param(
    [string]   $Port = "COM4",
    [string[]] $Command,
    [string]   $Csv,
    [int]      $Baud = 9600,
    [int]      $WaitMs = 350,
    [switch]   $AllowWrites
)

$ErrorActionPreference = "Stop"

# A query starts LETTER=GET. Anything else writes something.
# Note C=GET% is a query too, so do not require whitespace after GET.
function Test-ReadOnly([string]$c) {
    return $c -match '^[A-Z]=GET'
}

$DEFAULT = @(
    'E=GET PRODUCT', 'E=GET VERSION',
    'M=GET',
    'R=GET COLD', 'R=GET STATIC',
    'T=GET COLD', 'T=GET SP', 'T=GET BOARD', 'T=GET ROOM',
    'P=GET SP',
    'B=GET', 'B=GET CELLS', 'C=GET%',
    'S=GET PUFFS', 'S=GET TIME', 'S=GET ENERGY',
    'S=GET LASTPOWER', 'S=GET LASTTEMP',
    'X=GET TIMER'
)

if (-not $Command -or $Command.Count -eq 0) { $Command = $DEFAULT }

if (-not $AllowWrites) {
    $bad = $Command | Where-Object { -not (Test-ReadOnly $_) }
    if ($bad) {
        Write-Output "Refusing to send, these are not read-only queries:"
        $bad | ForEach-Object { Write-Output "  $_" }
        Write-Output ""
        Write-Output "This interface can fire the coil (F=#S) and change limits."
        Write-Output "Pass -AllowWrites if you mean it."
        exit 1
    }
}

if (-not ([System.IO.Ports.SerialPort]::GetPortNames() -contains $Port)) {
    Write-Output "$Port not present. Ports: $(([System.IO.Ports.SerialPort]::GetPortNames()) -join ', ')"
    exit 1
}

$sp = New-Object System.IO.Ports.SerialPort $Port, $Baud, "None", 8, "One"
$sp.Handshake   = "None"
$sp.DtrEnable   = $true      # CDC devices often stay quiet without these
$sp.RtsEnable   = $true
$sp.ReadTimeout = 400

$rows = @()
try {
    $sp.Open()
    Start-Sleep -Milliseconds 250
    $sp.DiscardInBuffer()

    foreach ($c in $Command) {
        $sp.Write($c + "`r`n")
        Start-Sleep -Milliseconds $WaitMs
        $reply = ""
        if ($sp.BytesToRead -gt 0) {
            $reply = $sp.ReadExisting().Trim()
        }
        if ($reply -eq "") { $reply = "(no reply - unsupported command)" }
        $rows += [pscustomobject]@{ Command = $c; Reply = $reply }
        "{0,-18} {1}" -f $c, $reply
    }
} finally {
    if ($sp.IsOpen) { $sp.Close() }
}

if ($Csv) {
    # append, with a timestamp, so repeated runs build a history
    $stamp = (Get-Date).ToString("s")
    $out = $rows | ForEach-Object {
        [pscustomobject]@{ When = $stamp; Command = $_.Command; Reply = $_.Reply }
    }
    $exists = Test-Path $Csv
    $out | Export-Csv -Path $Csv -NoTypeInformation -Append:$exists
    Write-Output ""
    Write-Output "appended $($out.Count) rows to $Csv"
}
