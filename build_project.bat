@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo  Nuitka Automated Build Script (UV + Win10 + MinGW)
echo ===================================================

:: 1. Ensure UV environment exists and activate it
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] .venv folder not found. Please create your uv environment first.
    exit /b 1
)
echo [1/4] Activating uv virtual environment...
call .venv\Scripts\activate.bat

:: 2. Install/Update Nuitka and ordering dependencies
echo [2/4] Ensuring Nuitka and dependency constraints are met...
uv pip install -U nuitka zstandard

:: 3. Setup MinGW compiler preferences for Nuitka
:: Setting this forces Nuitka to automatically download and configure its isolated MinGW64
set NUITKA_FORCE_MINGW=1

:: 4. Start Nuitka compilation
echo [3/4] Starting project compilation...
echo This might take several minutes depending on project size.

python -m nuitka ^
    --standalone ^
    --mingw64 ^
    --assume-yes-for-downloads ^
    --include-data-dir=data=data ^
    --follow-imports ^
    --output-dir=build_output ^
    --remove-output ^
    main.py

if %ERRORLEVEL% equ 0 (
    echo [4/4] SUCCESS: Compilation finished flawlessly.
    echo Check the 'build_output\main.dist' directory for your application.
) else (
    echo [ERROR] Nuitka compilation failed. Check the error log above.
    exit /b %ERRORLEVEL%
)

pause
