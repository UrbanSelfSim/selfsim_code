#!/bin/bash
echo "=========================================================="
echo "           Automatic Environment Installer"
echo "=========================================================="
echo ""
echo "Checking for Python3 environment..."
echo ""

if ! command -v python3 &> /dev/null
then
    echo "X Error: Python3 not found on this system."
    echo "   Please install Python from https://www.python.org/downloads/ first."
    exit 1
fi

echo "- Python3 environment found!"
echo ""
echo "Entering Python server directory..."
# This ensures the script can be run from anywhere.
cd "$(dirname "$0")/python_server"
echo ""
echo "Installing necessary Python libraries (e.g., Flask)..."
echo "This may take a few minutes. Please enter your password if prompted."
echo ""

pip3 install -r requirements.txt

echo ""
echo "- All libraries installed successfully!"
echo ""
echo "=========================================================="
echo "    You can now close this window and run '2_start_server.sh'"
echo "=========================================================="
echo ""
read -p "Press any key to exit..."