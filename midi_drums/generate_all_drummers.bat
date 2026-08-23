@echo off
REM Generate rock songs for ALL drummers with AD2 mapping
REM Run: generate_all_drummers.bat (from midi-drums root)

mkdir songs 2>nul

echo ========================================
echo Generating rock songs for all drummers
echo with Addictive Drums 2 mapping
echo ========================================
echo.

set COUNTER=0
set TOTAL=16

for %%d in (bonham carey chadsmith chambers composite_doom_blues copeland dee haake halpern hoglan peart porcaro rich roeder weckl) do (
    set /A COUNTER+=1
    echo [%%COUNTER! / %TOTAL%] Generating for drummer: %%d ...

    midi-drums ^
        --song ^
        --genre rock ^
        --style classic ^
        --drummer %%d ^
        --tempo 120 ^
        --mapping addictive_drums ^
        -o songs/%%d_rock_song.mid

    echo   -> songs/%%d_rock_song.mid
    echo.
)

echo ========================================
echo All %COUNTER% songs generated!
echo Output directory: songs/
echo ========================================
pause
