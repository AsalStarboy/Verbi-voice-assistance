#!/bin/bash

# Quick Pi 5 Setup - One-command installation
# Run this script on your Raspberry Pi 5

set -e

echo "🚀 Raspberry Pi 5 Voice Assistant Quick Setup"
echo "==========================================="

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Pi 5
if ! grep -q "Raspberry Pi 5" /proc/cpuinfo &> /dev/null; then
    print_warning "This script is optimized for Raspberry Pi 5. You might need adjustments for other models."
fi

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_error "Please run this script as a normal user, not root."
    exit 1
fi

# Get username for service setup
USERNAME=$(whoami)
print_status "Installing for user: $USERNAME"

# Create installation log
LOGFILE="$HOME/voice_assistant_install.log"
exec 1> >(tee -a "$LOGFILE") 2>&1

print_status "Installation log will be saved to: $LOGFILE"

# System update
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
print_status "Installing dependencies..."
sudo apt install -y \
    python3-pip \
    python3-venv \
    git \
    build-essential \
    portaudio19-dev \
    libsndfile1 \
    ffmpeg \
    cmake \
    pkg-config \
    libasound2-dev \
    pulseaudio \
    alsa-utils \
    wget \
    curl

# Clone repository if not exists
print_status "Setting up voice assistant..."
if [ ! -d "$HOME/Verbi-voice-assistance" ]; then
    git clone https://github.com/AsalStarboy/Verbi-voice-assistance.git "$HOME/Verbi-voice-assistance"
else
    cd "$HOME/Verbi-voice-assistance"
    git pull origin main
fi

cd "$HOME/Verbi-voice-assistance"

# Make scripts executable
chmod +x install_pi.sh start_voice_assistant.sh setup_service.sh

# Create virtual environment
print_status "Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
print_status "Installing Python packages..."
pip install --upgrade pip wheel setuptools
pip install -r requirements_pi.txt

# Install Ollama
if ! command -v ollama &> /dev/null; then
    print_status "Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
    sudo systemctl enable ollama
    sudo systemctl start ollama
    print_status "Waiting for Ollama service to start..."
    sleep 10
fi

# Download Ollama model
print_status "Downloading AI model (this may take a while)..."
ollama pull phi3.5:3.8b-mini-instruct-q3_K_M

# Set up audio
print_status "Configuring audio..."
sudo usermod -a -G audio $USERNAME

# Create systemd service
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/voice-assistant.service > /dev/null << EOF
[Unit]
Description=Voice Assistant Service
After=network.target sound.target ollama.service
Wants=network.target sound.target
Requires=ollama.service

[Service]
Type=simple
User=$USERNAME
Group=audio
WorkingDirectory=$HOME/Verbi-voice-assistance
Environment=HOME=$HOME
Environment=USER=$USERNAME
Environment=XDG_RUNTIME_DIR=/run/user/$(id -u)
Environment=PULSE_RUNTIME_PATH=/run/user/$(id -u)/pulse
Environment=PATH=$HOME/Verbi-voice-assistance/venv/bin:$PATH

# Pi 5 Specific Optimizations
Environment=MALLOC_ARENA_MAX=2
Environment=OMP_NUM_THREADS=4
Environment=PYTHONUNBUFFERED=1

# Startup delay to ensure all services are ready
ExecStartPre=/bin/sleep 10

# Health check and start
ExecStart=$HOME/Verbi-voice-assistance/start_voice_assistant.sh

Restart=always
RestartSec=10

# Resource limits optimized for Pi 5
CPUQuota=80%
MemoryMax=3G

StandardOutput=append:/var/log/voice-assistant.log
StandardError=append:/var/log/voice-assistant.log

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable voice-assistant
sudo systemctl start voice-assistant

# Create log file and set permissions
sudo touch /var/log/voice-assistant.log
sudo chown $USERNAME:$USERNAME /var/log/voice-assistant.log

# Final setup
print_status "Creating completion marker..."
touch ~/.voice_assistant_installed

echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
print_status "Voice Assistant has been installed and configured for Raspberry Pi 5"
print_status "The service will start automatically on boot"
print_status "Current Status:"
sudo systemctl status voice-assistant
echo ""
print_warning "For the changes to take full effect, please reboot your Pi:"
print_warning "sudo reboot"
echo ""
print_status "After reboot, the voice assistant will start automatically"
print_status "Check status with: sudo systemctl status voice-assistant"
print_status "View logs with: sudo journalctl -u voice-assistant -f"
print_status "Live log file: /var/log/voice-assistant.log"
