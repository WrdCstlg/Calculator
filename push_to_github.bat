@echo off
title Push QuantumCalc to GitHub (WrdCstlg)
cd /d "%~dp0"

echo ======================================================================
echo    PUSH QUANTUMCALC TO GITHUB (https://github.com/WrdCstlg/Calculator)
echo ======================================================================
echo.

git status
echo.
echo Attempting to push main branch to origin...
git push -u origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ======================================================================
    echo  NOTE: Remote repository 'Calculator' not found on GitHub under WrdCstlg!
    echo ======================================================================
    echo  To create the repository:
    echo  1. Visit: https://github.com/new
    echo  2. Repository name: Calculator
    echo  3. Choose Public or Private
    echo  4. Do NOT initialize with README / .gitignore (we already have them)
    echo  5. Click 'Create repository'
    echo.
    echo  Once created on GitHub, press any key to push your code!
    echo ======================================================================
    pause
    git push -u origin main
)

echo.
echo [✓] Done! Repository pushed to https://github.com/WrdCstlg/Calculator
pause
