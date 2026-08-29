@echo off
REM generate_ardour_songs.bat — Generate MIDI for Ardour/Mixbus integration
REM Produces GM (gm_drums) and AD2 (addictive_drums) mapping MIDI files
REM No .rpp generation (Ardour uses .ardourproj, not REAPER's format)

setlocal enabledelayedexpansion

REM Full path to midi-drums executable in venv
set "MIDDRUMS=b:\dev\github\midi-drums\.venv\Scripts\python.exe -m midi_drums"

if not exist "ardour_test" mkdir ardour_test

echo ======================================== > ardour_gen_output.txt
echo Generating all complete songs for Ardour/Mixbus >> ardour_gen_output.txt
echo Using midi-drums CLI defaults (no overrides) >> ardour_gen_output.txt
echo MIDI formats: GM (gm_drums) + AD2 (addictive_drums) >> ardour_gen_output.txt
echo ======================================== >> ardour_gen_output.txt
echo. >> ardour_gen_output.txt

set DRUMMERS=bonham porcaro weckl chambers carey dee roeder hoglan rich copeland smith haake halpern peart

REM Metal - 7 styles x 14 drummers = 98 combinations each format
echo [Metal] >> ardour_gen_output.txt
for %%G in (doom death heavy power progressive thrash breakdown) do (
    for %%D in (!DRUMMERS!) do (
        echo   metal/%%G/%%D ...
        %MIDDRUMS% --song --genre metal --style %%G --drummer %%D --output "ardour_test\metal_%%G_%%D_gm.mid" >> ardour_gen_output.txt 2>&1
        %MIDDRUMS% --song --genre metal --style %%G --drummer %%D --output "ardour_test\metal_%%G_%%D_ad2.mid" --mapping addictive_drums >> ardour_gen_output.txt 2>&1
    )
)

REM Rock - 7 styles x 14 drummers = 98 combinations each format
echo [Rock] >> ardour_gen_output.txt
for %%G in (classic blues alternative progressive punk hard pop) do (
    for %%D in (!DRUMMERS!) do (
        echo   rock/%%G/%%D ...
        %MIDDRUMS% --song --genre rock --style %%G --drummer %%D --output "ardour_test\rock_%%G_%%D_gm.mid" >> ardour_gen_output.txt 2>&1
        %MIDDRUMS% --song --genre rock --style %%G --drummer %%D --output "ardour_test\rock_%%G_%%D_ad2.mid" --mapping addictive_drums >> ardour_gen_output.txt 2>&1
    )
)

REM Jazz - 7 styles x 14 drummers = 98 combinations each format
echo [Jazz] >> ardour_gen_output.txt
for %%G in (swing bebop fusion latin ballad hard_bop contemporary) do (
    for %%D in (!DRUMMERS!) do (
        echo   jazz/%%G/%%D ...
        %MIDDRUMS% --song --genre jazz --style %%G --drummer %%D --output "ardour_test\jazz_%%G_%%D_gm.mid" >> ardour_gen_output.txt 2>&1
        %MIDDRUMS% --song --genre jazz --style %%G --drummer %%D --output "ardour_test\jazz_%%G_%%D_ad2.mid" --mapping addictive_drums >> ardour_gen_output.txt 2>&1
    )
)

REM Funk - 7 styles x 14 drummers = 98 combinations each format
echo [Funk] >> ardour_gen_output.txt
for %%G in (classic pfunk shuffle new_orleans fusion minimal heavy) do (
    for %%D in (!DRUMMERS!) do (
        echo   funk/%%G/%%D ...
        %MIDDRUMS% --song --genre funk --style %%G --drummer %%D --output "ardour_test\funk_%%G_%%D_gm.mid" >> ardour_gen_output.txt 2>&1
        %MIDDRUMS% --song --genre funk --style %%G --drummer %%D --output "ardour_test\funk_%%G_%%D_ad2.mid" --mapping addictive_drums >> ardour_gen_output.txt 2>&1
    )
)

REM Electronic - 4 styles x 14 drummers = 56 combinations each format
echo [Electronic] >> ardour_gen_output.txt
for %%G in (house techno drum_and_bass dubstep) do (
    for %%D in (!DRUMMERS!) do (
        echo   elec/%%G/%%D ...
        %MIDDRUMS% --song --genre electronic --style %%G --drummer %%D --output "ardour_test\elec_%%G_%%D_gm.mid" >> ardour_gen_output.txt 2>&1
        %MIDDRUMS% --song --genre electronic --style %%G --drummer %%D --output "ardour_test\elec_%%G_%%D_ad2.mid" --mapping addictive_drums >> ardour_gen_output.txt 2>&1
    )
)

echo. >> ardour_gen_output.txt
echo ======================================== >> ardour_gen_output.txt
echo Done! All MIDI files in ardour_test/ >> ardour_gen_output.txt
echo Usage in Mixbus: Tools → Scripts → Load Script → ardour/create_song_sections.lua >> ardour_gen_output.txt
echo Or import manually via Media → Import Audio/MIDI Files >> ardour_gen_output.txt
echo ======================================== >> ardour_gen_output.txt
