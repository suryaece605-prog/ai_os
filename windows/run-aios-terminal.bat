@echo off
rem Opens the AI OS terminal chat on Windows. Needs Python 3 (python.org) installed.
cd /d "%~dp0.."
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 aios.py %*
) else (
  python aios.py %*
)
pause
