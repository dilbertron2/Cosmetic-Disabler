#!/bin/bash

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3 using your package manager:"
    echo "  Debian/Ubuntu: sudo apt install python3 python3-pip python3-tk python3-venv"
    echo "  Arch: sudo pacman -S python python-pip tk"
    echo "  Fedora: sudo dnf install python3 python3-pip python3-tkinter python3-virtualenv"
    exit 1
fi

# Check if tkinter is available
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "Error: tkinter is not installed."
    echo "Please install it:"
    echo "  Debian/Ubuntu: sudo apt install python3-tk"
    echo "  Arch: sudo pacman -S tk"
    echo "  Fedora: sudo dnf install python3-tkinter"
    exit 1
fi

# Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
fi

# Activate venv
source .venv/bin/activate

# Install/update dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
    echo "✓ Dependencies installed"
fi

# Run the program
echo "Starting TF2 Cosmetic Disabler..."
python3 cosmetic_disabler.py
