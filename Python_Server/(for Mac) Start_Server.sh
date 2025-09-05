#!/bin/bash
# This ensures the script changes to its own directory before running.
cd "$(dirname "$0")/.."

echo "Current working directory set to: $(dirname "$0")/..
echo "Starting Python server..."
python3 Python_Server/Server.py