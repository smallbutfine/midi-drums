@echo off
REM Generate complete multi-section songs using midi_drums CLI --song command
REM Output: GM MIDI, AD2 MIDI, and REAPER RPP files for all genres/styles

set "OUTPUT_DIR=reaper_test"
mkdir "%OUTPUT_DIR%" 2>nul

echo ================================================
echo CHAMELEON DRUMMER - Complete Song Generation
echo Using midi_drums.api.cli --song command
echo ================================================
echo.

for %%G in (metal rock jazz funk) do (
    for %%S in classic doom death heavy blues alternative swing bebop fusion shuffle pfunk do (
        echo [%%G/%%S]...
        
        REM GM MIDI export
        python -m midi_drums.api.cli --song ^
            --genre %%G ^
            --style %%S ^
            --output "%OUTPUT_DIR%/%%G_%%S_song_gm.mid" ^
            --mapping gm_drums ^
            --tempo 120
        
        REM AD2 MIDI export
        python -m midi_drums.api.cli --song ^
            --genre %%G ^
            --style %%S ^
            --output "%OUTPUT_DIR%/%%G_%%S_song_ad2.mid" ^
            --mapping addictive_drums ^
            --tempo 120
            
        REM REAPER RPP export (preset-only mode)
        python -m midi_drums.api.cli reaper export ^
            --genre %%G ^
            --style %%S ^
            --output "%OUTPUT_DIR%/%%G_%%S_song.rpp" ^
            --preset-only
        
        echo   [OK] %%G_%%S (GM/AD2/RPP generated)
    )
    echo.
)

echo ================================================
echo DONE! All songs in: %OUTPUT_DIR%\
echo ================================================
