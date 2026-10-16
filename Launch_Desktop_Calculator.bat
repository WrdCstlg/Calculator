@echo off
title QuantumCalc - Native Desktop Calculator
cd /d "%~dp0"
echo Starting QuantumCalc Desktop Calculator...
py desktop_calculator.py
if %ERRORLEVEL% NEQ 0 (
    python desktop_calculator.py
)
pause
