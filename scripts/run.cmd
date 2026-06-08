@echo off
REM Set current directory to the script's location
cd /d "%~dp0"

@echo off
REM Check if virtual environment exists, if not, create it
if not exist "venv_wkspel\" (
    echo Creating virtual environment...
    python -m venv venv_wkspel

    echo Activating environment and installing wkspel...
    call .\venv_wkspel\Scripts\activate
    pip install https://github.com/r-w-dev/ek_spel/archive/refs/heads/main.zip
) else (
    echo Activating virtual environment...
    call .\venv_wkspel\Scripts\activate
)

@echo off
REM Set the database connection string
set CONNECTION_STRING=sqlite:///wkspel2026.db

REM Remove existing database file if it exists
if exist "wkspel2026.db" (
    echo Removing existing database...
    del wkspel2026.db
)

echo Initializing database...
REM Create the database tables
wkspel create

echo Loading schedule and forms...
REM Load the Excel schedule and the forms from the 'invullijsten' directory
REM Filename: wk-2026-speelschema.xlsx
REM Dir: invullijsten
wkspel load --source_file=..\programma\wk-2026-speelschema.xlsx --source_forms=..\invullijsten\2026

echo Setup complete.
pause
