@echo off
rem Opens the AI OS window on Windows. Needs Python 3 (python.org) installed.
cd /d "%~dp0.."
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 aios_gui.py
) else (
  python aios_gui.py
)
if errorlevel 1 (
  echo.
  echo Could not start AI OS. Install Python 3 from python.org and tick "Add Python to PATH".
  pause
)
