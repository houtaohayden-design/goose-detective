@echo off
REM build_windows.bat — one-click local build of 鹅探长 installer on Windows
REM Requirements: Python 3.11, and Inno Setup 6 (https://jrsoftware.org/isdl.php)

echo ============================================
echo   Building 鹅探长 (Goose Detective)
echo ============================================

echo [1/4] Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
if errorlevel 1 goto :error

echo [2/4] Running tests...
set QT_QPA_PLATFORM=offscreen
python -m pytest -q
if errorlevel 1 goto :error

echo [3/4] Building executable with PyInstaller...
pyinstaller goose_detective.spec
if errorlevel 1 goto :error

echo [4/4] Compiling installer with Inno Setup...
set ISCC="%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist %ISCC% (
    echo.
    echo Inno Setup not found. The standalone app is ready at: dist\GooseDetective\
    echo To build the installer, install Inno Setup 6 then re-run this script.
    echo   https://jrsoftware.org/isdl.php
    goto :done
)
%ISCC% installer\installer.iss
if errorlevel 1 goto :error

echo.
echo ============================================
echo   Done! Installer at: dist\installer\
echo ============================================
goto :done

:error
echo.
echo BUILD FAILED. See messages above.
exit /b 1

:done
pause
