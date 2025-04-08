@echo off
:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not added to PATH.
    echo Please install Python and try again.
    pause
    exit /b 1
)

:: Install required packages
echo Installing required Python packages...
pip install -r requirements.txt

:: Check if pip installation was successful
if %ERRORLEVEL% neq 0 (
    echo Failed to install required packages.
    pause
    exit /b 1
)

:: Run the Python script
echo Running final.py...
python final.py

:: Pause so the user can see the output
pause