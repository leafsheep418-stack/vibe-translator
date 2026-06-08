@echo off
setlocal

echo Building vibe-translator.exe...
python -m PyInstaller --onefile --windowed --name vibe-translator main.py

if errorlevel 1 (
    echo.
    echo Build failed.
    echo Please install build tools first:
    echo pip install -r requirements-dev.txt
    echo.
    pause
    exit /b 1
)

echo.
echo Done.
echo The exe file should be in the dist folder:
echo dist\vibe-translator.exe
echo.
pause
