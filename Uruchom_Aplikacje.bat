@echo off
title Trainer App v1.0 - Uruchamianie...
echo ======================================================
echo    URUCHAMIANIE APLIKACJI TRAINER PRO
echo ======================================================
echo.

cd /d "%~dp0"

:: Skip Streamlit onboarding/email prompt
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
set STREAMLIT_SERVER_HEADLESS=true

echo [1/2] Sprawdzanie srodowiska...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Blad: Python nie jest zainstalowany lub nie ma go w PATH.
    pause
    exit /b
)

python -c "import streamlit, pandas, gspread" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Instalowanie brakujacych bibliotek...
    python -m pip install -r requirements.txt --quiet
)

echo [2/2] Startowanie serwera...
echo.
echo ======================================================
echo    Aplikacja otworzy sie zaraz w przegladarce.
echo    Adres: http://localhost:8501
echo    NIE ZAMYKAJ tego okna!
echo ======================================================
echo.

:: Otwarcie przegladarki
start "" http://localhost:8501

:: Uruchomienie streamlit (uzywa config.toml dla portu)
python -m streamlit run main.py

if %errorlevel% neq 0 (
    echo.
    echo [!] Blad startu aplikacji.
    pause
)
