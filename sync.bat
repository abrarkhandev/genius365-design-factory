@echo off
REM Genius365 Design Factory - Windows installer/updater.
REM Double-click this file, or run  .\sync.bat  in a terminal.
REM It runs sync.ps1 with the execution-policy bypass so Windows does not block it.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0sync.ps1"
echo.
pause
