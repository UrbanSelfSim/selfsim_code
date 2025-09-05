@echo off
echo.
echo ==========================================================
echo            Automatic Environment Installer
echo ==========================================================
echo.
echo Checking for Python environment...
echo.

python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo X Error: Python not found on this system.
    echo   Please install Python from https://www.python.org/downloads/ first.
    echo   (Important: During installation, be sure to check the "Add Python to PATH" option!)
    goto :end
)

echo - Python environment found!
echo.
echo Entering Python server directory...
cd python_server
echo.
echo Installing necessary Python libraries (e.g., Flask)...
echo This may take a few minutes. Please be patient.
echo.

pip install -r requirements.txt

echo.
echo - All libraries installed successfully!
echo.
echo ==========================================================
echo     You can now close this window and run "2_Start_Server.bat"
echo ==========================================================
echo.

:end
pause