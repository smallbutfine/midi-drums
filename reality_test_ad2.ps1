# Reality test: Generate songs with all drummers using AD2 mapping + Reaper export
$drummers = @("bonham", "carey", "chambers", "copeland", "dee", "haake", "halpern", "hoglan", "peart", "porcaro", "rich", "roeder", "smith", "weckl")
$outputDir = "output/reality_test_ad2"

# Create output directory if it doesn't exist
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

Write-Host "=== REALITY TEST: AD2 Songs + Reaper Export ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Generate all drummer songs with AD2 mapping
Write-Host "Step 1: Generating rock songs for all drummers (AD2 mapping)" -ForegroundColor Yellow
foreach ($drummer in $drummers) {
    $i = $drummers.IndexOf($drummer) + 1
    $filename = "$outputDir\$($drummer)_rock_ad2.mid"
    Write-Host "[$i/$($drummers.Count)] Generating: $drummer ..." -ForegroundColor Yellow
    
    & uv run midi-drums --song --genre rock --style classic --tempo 120 --drummer $drummer --mapping addictive_drums --output $filename 2>&1 | ForEach-Object { $_.ToString() }
    
    if (Test-Path $filename) {
        $size = (Get-Item $filename).Length
        Write-Host "   ✓ $filename ($([math]::Round($size/1KB, 1)) KB)" -ForegroundColor Green
    } else {
        Write-Host "   ✗ FAILED" -ForegroundColor Red
    }
}

# Step 2: Test Reaper export with one drummer (Bonham as representative)
Write-Host ""
Write-Host "Step 2: Testing Reaper project generation (bonham rock)" -ForegroundColor Yellow
$reaperFile = "$outputDir/bonham_reaper.rpp"
& uv run midi-drums generate --genre rock --style classic --drummer bonham --mapping addictive_drums --tempo 120 --output $reaperFile --midi 2>&1 | ForEach-Object { $_.ToString() }

if (Test-Path $reaperFile) {
    $size = (Get-Item $reaperFile).Length
    Write-Host "   ✓ Reaper project: $reaperFile ($([math]::Round($size/1KB, 1)) KB)" -ForegroundColor Green
} else {
    Write-Host "   ✗ Reaper export failed" -ForegroundColor Red
}

# Step 3: Test without explicit song flag (should still work)
Write-Host ""
Write-Host "Step 3: Testing --song flag standalone (carey rock)" -ForegroundColor Yellow
$standaloneFile = "$outputDir/carey_standalone.mid"
& uv run midi-drums --song --drummer carey --mapping addictive_drums --tempo 120 --output $standaloneFile 2>&1 | ForEach-Object { $_.ToString() }

if (Test-Path $standaloneFile) {
    $size = (Get-Item $standaloneFile).Length
    Write-Host "   ✓ Standalone output: $standaloneFile ($([math]::Round($size/1KB, 1)) KB)" -ForegroundColor Green
} else {
    Write-Host "   ✗ FAILED" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Reality test complete ===" -ForegroundColor Cyan
Write-Host "Output directory: $outputDir" -ForegroundColor Yellow
Write-Host ""
Write-Host "Files generated:" -ForegroundColor Yellow
Get-ChildItem $outputDir -File | Select-Object Name, @{Name="Size (KB)"; Expression={[math]::Round($_.Length/1KB, 1)}} | Format-Table -AutoSize
