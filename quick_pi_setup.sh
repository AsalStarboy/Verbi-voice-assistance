#!/bin/bash

# Quick Pi Setup - Copy voice assistant files and run installer
# Run this script on your Raspberry Pi

set -e

echo "🚀 Raspberry Pi Voice Assistant Quick Setup"
echo "==========================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_header "Installing git..."
    sudo apt update
    sudo apt install -y git
fi

print_header "1. Cloning voice assistant repository..."
cd ~
if [ -d "Verbi-voice-assistance" ]; then
    print_status "Repository already exists, updating..."
    cd Verbi-voice-assistance
    git pull
else
    git clone https://github.com/AsalStarboy/Verbi-voice-assistance.git
    cd Verbi-voice-assistance
fi

print_header "2. Making installer executable..."
chmod +x install_pi.sh

print_header "3. Running full installation..."
./install_pi.sh

print_status "Quick setup complete! The full installer is now running."
