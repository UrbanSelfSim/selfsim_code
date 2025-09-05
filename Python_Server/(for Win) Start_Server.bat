@echo off
rem %~dp0 is a special variable for the script's own directory path.
cd /d "%~dp0.."

echo Current working directory set to: %cd%
echo Starting Python server...
python Python_Server/Server.py
pause