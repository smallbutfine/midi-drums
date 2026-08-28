@echo off
REM ============================================================
REM REGENERATE ALL COMPLETE SONGS - ALL DRUMMERS, ALL STYLES
REM Uses: midi_drums.api.cli --song and reaper export commands
REM Output: GM MIDI + AD2 MIDI + RPP for every combination
REM ============================================================

setlocal enabledelayedexpansion

echo ============================================================
echo REGENERATING ALL COMPLETE SONGS
echo (All drummers, all genres, all styles)
echo ============================================================
echo.

if not exist "reaper_test" mkdir reaper_test

echo [Metal genre]
for %%D in (bonham porcaro weckl chambers carey dee roeder hoglan rich copeland smith haake halpern peart) do (
    echo   Drummer: %%D
    for %%S in doom death heavy power progressive thrash breakdown do (
        set FILE=metal_%%S_%%D
        python -m midi_drums.api.cli --song --genre metal --style %%S --output "reaper_test\!FILE!!gm!.mid" --mapping gm_drums --tempo 120
        python -m midi_drums.api.cli --song --genre metal --style %%S --output "reaper_test\!FILE!!ad2!.mid" --mapping addictive_drums --tempo 120
        python -m midi_drums.api.cli reaper export --genre metal --style %%S --output "reaper_test\!FILE!.rpp" --preset-only
    )
)

echo [Rock genre]
for %%D in (bonham porcaro weckl chambers carey dee roeder hoglan rich copeland smith haake halpern peart) do (
    echo   Drummer: %%D
    for %%S in classic blues alternative progressive punk hard pop do (
        set FILE=rock_%%S_%%D
        python -m midi_drums.api.cli --song --genre rock --style %%S --output "reaper_test\!FILE!!gm!.mid" --mapping gm_drums --tempo 120
        python -m midi_drums.api.cli --song --genre rock --style %%S --output "reaper_test\!FILE!!ad2!.mid" --mapping addictive_drums --tempo 120
        python -m midi_drums.api.cli reaper export --genre rock --style %%S --output "reaper_test\!FILE!.rpp" --preset-only
    )
)

echo [Jazz genre]
for %%D in (bonham porcaro weckl chambers carey dee roeder hoglan rich copeland smith haake halpern peart) do (
    echo   Drummer: %%D
    for %%S in swing bebop fusion latin ballad hard_bop contemporary do (
        set FILE=jazz_%%S_%%D
        python -m midi_drums.api.cli --song --genre jazz --style %%S --output "reaper_test\!FILE!!gm!.mid" --mapping gm_drums --tempo 120
        python -m midi_drums.api.cli --song --genre jazz --style %%S --output "reaper_test\!FILE!!ad2!.mid" --mapping addictive_drums --tempo 120
        python -m midi_drums.api.cli reaper export --genre jazz --style %%S --output "reaper_test\!FILE!.rpp" --preset-only
    )
)

echo [Funk genre]
for %%D in (bonham porcaro weckl chambers carey dee roeder hoglan rich copeland smith haake halpern peart) do (
    echo   Drummer: %%D
    for %%S in classic pfunk shuffle new_orleans fusion minimal heavy do (
        set FILE=funk_%%S_%%D
        python -m midi_drums.api.cli --song --genre funk --style %%S --output "reaper_test\!FILE!!gm!.mid" --mapping gm_drums --tempo 120
        python -m midi_drums.api.cli --song --genre funk --style %%S --output "reaper_test\!FILE!!ad2!.mid" --mapping addictive_drums --tempo 120
        python -m midi_drums.api.cli reaper export --genre funk --style %%S --output "reaper_test\!FILE!.rpp" --preset-only
    )
)

echo.
echo ============================================================
echo COMPLETE - All songs generated in reaper_test/
echo (14 drummers x 4 genres x ~7 styles = ~390 song combinations)
echo ============================================================
