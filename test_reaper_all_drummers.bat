@echo off
REM Generate Reaper projects + MIDI for ALL drummers (standard + AD2)
mkdir reaper_test 2>nul
set COUNTER=0
set TOTAL=30

echo ========================================
echo Reaper export test — all drummers
echo Standard MIDI + AD2 mapping
echo ========================================
echo.

for %%d in (bonham carey chadsmith chambers composite_doom_blues copeland dee haake halpern hoglan peart porcaro rich roeder weckl) do (
    REM --- Standard MIDI (EZDrummer3) ---
    set /A COUNTER+=1
    echo [%COUNTER! / %TOTAL%] Reaper: %%d (standard)...
    uv run midi-drums ^
        reaper export ^
        --genre rock ^
        --style classic ^
        --drummer %%d ^
        --tempo 120 ^
        --complexity 0.5 ^
        --humanization 0.3 ^
        -o "reaper_test/%%d.rpp" ^
        --midi "reaper_test/%%d.mid" 2>&1 | findstr /V "^==="
    if exist "reaper_test\%%d.rpp" ( for %%f in ("reaper_test\%%d.rpp") do echo   .rpp : OK (!%%~zf bytes) ) else ( echo   .rpp : MISSING! )
    if exist "reaper_test\%%d.mid"  ( for %%f in ("reaper_test\%%d.mid")  do echo   .mid : OK (!%%~zf bytes) ) else ( echo   .mid : MISSING! )

    REM --- AD2 MIDI ---
    set /A COUNTER+=1
    echo [%COUNTER! / %TOTAL%] Reaper: %%d (AD2)...
    uv run midi-drums ^
        reaper export ^
        --genre rock ^
        --style classic ^
        --drummer %%d ^
        --tempo 120 ^
        --complexity 0.5 ^
        --humanization 0.3 ^
        --mapping addictive_drums ^
        -o "reaper_test/%%d_ad2.rpp" ^
        --midi "reaper_test/%%d_ad2.mid" 2>&1 | findstr /V "^==="
    if exist "reaper_test\%%d_ad2.rpp" ( for %%f in ("reaper_test\%%d_ad2.rpp") do echo   .rpp : OK (!%%~zf bytes) ) else ( echo   .rpp : MISSING! )
    if exist "reaper_test\%%d_ad2.mid"  ( for %%f in ("reaper_test\%%d_ad2.mid")  do echo   .mid : OK (!%%~zf bytes) ) else ( echo   .mid : MISSING! )
    echo.
)

echo ========================================
echo Done! All %COUNTER% exports complete
echo Output: reaper_test/
echo ========================================
pause
