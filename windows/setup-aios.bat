@echo off
rem One-time setup: choose Claude or a local model and save your API key.
cd /d "%~dp0.."
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 aios.py setup
) else (
  python aios.py setup
)
pause
