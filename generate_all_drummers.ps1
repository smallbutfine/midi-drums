# Generate rock songs for ALL drummers with AD2 mapping
$drummers = @("bonham", "carey", "chadsmith", "chambers", "composite_doom_blues", "copeland", "dee", "haake", "halpern", "hoglan", "peart", "porcaro", "rich", "roeder", "weckl")
$outputDir = "output/all_drummers_rock_ad2"

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

Write-Host "=== Generating rock songs for all drummers with AD2 mapping ===" -ForegroundColor Cyan
Write-Host ""

foreach ($drummer in $drummers) {
    $i = $drummers.IndexOf($drummer) + 1
    $filename = "$outputDir\$($drummer)_rock_ad2.mid"
    Write-Host "[$i/$($drummers.Count)] Generating: $drummer ..." -ForegroundColor Yellow
    
    # Run with logging suppressed, capture exit code
    $errorAction = $ErrorActionPreference
    $ErrorActionPreference = 'Stop'
    try {
        & uv run midi-drums --song --genre rock --style classic --tempo 120 --drummer $drummer --mapping addictive_drums --output $filename 2>$null
        $success = $LASTEXITCODE -eq 0
    } catch {
        $success = $false
    } finally {
        $ErrorActionPreference = $errorAction
    }
    
    if (Test-Path $filename) {
        $size = (Get-Item $filename).Length
        Write-Host "   -> $filename ($size bytes)" -ForegroundColor Green
    } else {
        Write-Host "   -> FAILED" -ForegroundColor Red
    }
    Write-Host ""
}

Write-Host "=== Done ===" -ForegroundColor Green
Write-Host "Output directory: $outputDir" -ForegroundColor Cyan
