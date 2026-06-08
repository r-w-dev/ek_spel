@echo off
REM Save current directory and change to script's location
pushd "%~dp0"

@echo off
REM Check if virtual environment exists, if not, create it
if not exist "venv_wkspel\" (
    echo Creating virtual environment...
    python -m venv venv_wkspel

    echo Activating environment and installing wkspel...
    call .\venv_wkspel\Scripts\activate
    python -m pip install pip -U
    pip install https://github.com/r-w-dev/ek_spel/archive/refs/heads/main.zip
) else (
    echo Activating virtual environment...
    call .\venv_wkspel\Scripts\activate
)

REM Set the database connection string using the full path to the current directory
set "CONNECTION_STRING=sqlite:///%~dp0wkspel2026.db"
echo CONNECTION_STRING is set to: %CONNECTION_STRING%

REM Remove existing database file if it exists
if exist "wkspel2026.db" (
    echo Removing existing database...
    del wkspel2026.db
)

echo Initializing database...
REM Create the database tables
wkspel create

echo Loading schedule and forms...
REM Run wkspel load using --source_file="%~1" and --source_forms="%~2"
wkspel load --source_file="%~1" --source_forms="%~2"

echo Update scores
wkspel update --source_file="%~1"

REM Restore the original directory
popd
pause
