@echo off

REM Full path to midi-drums executable in venv
set "MIDDRUMS=b:\dev\github\midi-drums\.venv\Scripts\python.exe -m midi_drums"

if not exist "reaper_test" mkdir reaper_test

echo ======================================== > regen_output.txt
echo Regenerating all complete songs... >> regen_output.txt
echo Using midi-drums CLI defaults (no overrides) >> regen_output.txt
echo ======================================== >> regen_output.txt
echo. >> regen_output.txt

set DRUMMERS=bonham porcaro weckl chambers carey dee roeder hoglan rich copeland smith haake halpern peart

REM Metal - 7 styles x 14 drummers = 98 combinations
echo [Metal] >> regen_output.txt
for %%G in (doom death heavy power progressive thrash breakdown) do (
    for %%D in (%DRUMMERS%) do (
        %MIDDRUMS% --song --genre metal --style %%G --drummer %%D --output "reaper_test\metal_%%G_%%D_gm.mid" >> regen_output.txt 2>&1
        %MIDDRUMS% --song --genre metal --style %%G --drummer %%D --output "reaper_test\metal_%%G_%%D_ad2.mid" --mapping addictive_drums >> regen_output.txt 2>&1
        %MIDDRUMS% reaper export --genre metal --style %%G --drummer %%D --output "reaper_test\metal_%%G_%%D.rpp" --preset-only >> regen_output.txt 2>&1

    )
)

REM Rock - 7 styles x 14 drummers = 98 combinations  
echo [Rock] >> regen_output.txt
for %%G in (classic blues alternative progressive punk hard pop) do (
    for %%D in (%DRUMMERS%) do (
        %MIDDRUMS% --song --genre rock --style %%G --drummer %%D --output "reaper_test\rock_%%G_%%D_gm.mid" >> regen_output.txt 2>&1
        %MIDDRUMS% --song --genre rock --style %%G --drummer %%D --output "reaper_test\rock_%%G_%%D_ad2.mid" --mapping addictive_drums >> regen_output.txt 2>&1
        %MIDDRUMS% reaper export --genre rock --style %%G --drummer %%D --output "reaper_test\rock_%%G_%%D.rpp" --preset-only >> regen_output.txt 2>&1

    )
)

REM Jazz - 7 styles x 14 drummers = 98 combinations
echo [Jazz] >> regen_output.txt
for %%G in (swing bebop fusion latin ballad hard_bop contemporary) do (
    for %%D in (%DRUMMERS%) do (
        %MIDDRUMS% --song --genre jazz --style %%G --drummer %%D --output "reaper_test\jazz_%%G_%%D_gm.mid" >> regen_output.txt 2>&1
        %MIDDRUMS% --song --genre jazz --style %%G --drummer %%D --output "reaper_test\jazz_%%G_%%D_ad2.mid" --mapping addictive_drums >> regen_output.txt 2>&1
        %MIDDRUMS% reaper export --genre jazz --style %%G --drummer %%D --output "reaper_test\jazz_%%G_%%D.rpp" --preset-only >> regen_output.txt 2>&1

    )
)

REM Funk - 7 styles x 14 drummers = 98 combinations
echo [Funk] >> regen_output.txt
for %%G in (classic pfunk shuffle new_orleans fusion minimal heavy) do (
    for %%D in (%DRUMMERS%) do (
        %MIDDRUMS% --song --genre funk --style %%G --drummer %%D --output "reaper_test\funk_%%G_%%D_gm.mid" >> regen_output.txt 2>&1
        %MIDDRUMS% --song --genre funk --style %%G --drummer %%D --output "reaper_test\funk_%%G_%%D_ad2.mid" --mapping addictive_drums >> regen_output.txt 2>&1
        %MIDDRUMS% reaper export --genre funk --style %%G --drummer %%D --output "reaper_test\funk_%%G_%%D.rpp" --preset-only >> regen_output.txt 2>&1

    )
)

REM Electronic - 4 styles x 14 drummers = 56 combinations
echo [Electronic] >> regen_output.txt
for %%G in (house techno drum_and_bass dubstep) do (
    for %%D in (%DRUMMERS%) do (
        %MIDDRUMS% --song --genre electronic --style %%G --drummer %%D --output "reaper_test\elec_%%G_%%D_gm.mid" >> regen_output.txt 2>&1
        %MIDDRUMS% --song --genre electronic --style %%G --drummer %%D --output "reaper_test\elec_%%G_%%D_ad2.mid" --mapping addictive_drums >> regen_output.txt 2>&1
        %MIDDRUMS% reaper export --genre electronic --style %%G --drummer %%D --output "reaper_test\elec_%%G_%%D.rpp" --preset-only >> regen_output.txt 2>&1

    )
)

echo. >> regen_output.txt
echo ======================================== >> regen_output.txt
echo COMPLETE - All songs in reaper_test/ >> regen_output.txt
echo (14 drummers x 32 styles = 448 combos x 3 files = 1,344 total) >> regen_output.txt
echo ======================================== >> regen_output.txt
