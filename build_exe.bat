@echo off
setlocal

echo Building vibe-translator.exe...
pyinstaller --onefile --windowed --name vibe-translator main.py

echo.
echo Done.
echo The exe file should be in the dist folder:
echo dist\vibe-translator.exe
echo.
pause
