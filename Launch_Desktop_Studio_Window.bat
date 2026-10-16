@echo off
title QuantumCalc - Native Desktop Studio Window
cd /d "%~dp0"
echo Starting QuantumCalc Desktop Studio Window...
py desktop_window.py
if %ERRORLEVEL% NEQ 0 (
    python desktop_window.py
)
pause
