#!/bin/bash

# One-click setup script for Voice Assistant on Raspberry Pi
# This script installs all dependencies and sets up the service

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Voice Assistant One-Click Setup ===${NC}"
echo "This script will install all dependencies and set up the voice assistant"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo -e "${RED}Please run this script as a normal user, not root${NC}"
    exit 1
fi

# Get username for service setup
USERNAME=$(whoami)
echo -e "${GREEN}Installing for user: $USERNAME${NC}"

# Create log file
LOGFILE="$HOME/voice_assistant_setup.log"
exec 1> >(tee -a "$LOGFILE") 2>&1

echo "Installation log will be saved to: $LOGFILE"

# 1. System Updates
echo -e "${GREEN}=== Updating System Packages ===${NC}"
sudo apt update && sudo apt upgrade -y

# 2. Install System Dependencies
echo -e "${GREEN}=== Installing System Dependencies ===${NC}"
sudo apt install -y \
    python3-pip \
    python3-venv \
    git \
    build-essential \
    portaudio19-dev \
    python3-pyaudio \
    libsndfile1 \
    ffmpeg \
    cmake \
    pkg-config \
    libasound2-dev \
    pulseaudio \
    alsa-utils \
    wget \
    curl \
    flac \
    libespeak1

# 3. Audio Setup
echo -e "${GREEN}=== Configuring Audio ===${NC}"
sudo usermod -a -G audio $USERNAME
pulseaudio --start

# 4. Python Virtual Environment
echo -e "${GREEN}=== Setting up Python Environment ===${NC}"
python3 -m venv venv
source venv/bin/activate

# 5. Upgrade pip and install wheel
echo -e "${GREEN}=== Upgrading pip and installing wheel ===${NC}"
pip install --upgrade pip wheel setuptools

# 6. Install Python Packages
echo -e "${GREEN}=== Installing Python Packages ===${NC}"
pip install \
    SpeechRecognition>=3.10.0 \
    pyaudio>=0.2.11 \
    pydub>=0.25.1 \
    numpy>=1.21.0,\<1.25.0 \
    scipy>=1.7.0,\<1.11.0 \
    soundfile>=0.12.1 \
    sounddevice>=0.4.6 \
    faster-whisper>=1.0.0 \
    ollama>=0.1.7 \
    requests>=2.28.0 \
    piper-tts>=1.2.0 \
    colorama>=0.4.6 \
    python-dotenv>=1.0.0 \
    pygame>=2.1.0 \
    psutil>=5.9.0 \
    httpx>=0.24.0

# 7. Install Ollama
echo -e "${GREEN}=== Installing Ollama ===${NC}"
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.ai/install.sh | sh
    sudo systemctl enable ollama
    sudo systemctl start ollama
    echo "Waiting for Ollama service to start..."
    sleep 10
fi

# 8. Download AI Model
echo -e "${GREEN}=== Downloading AI Model (this may take a while) ===${NC}"
ollama pull phi3.5:3.8b-mini-instruct-q3_K_M

# 9. Create Systemd Service
echo -e "${GREEN}=== Creating Systemd Service ===${NC}"
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
Environment=MALLOC_ARENA_MAX=2
Environment=OMP_NUM_THREADS=4
Environment=PYTHONUNBUFFERED=1

ExecStartPre=/bin/sleep 10
ExecStart=$HOME/Verbi-voice-assistance/start_voice_assistant.sh

Restart=always
RestartSec=10

StandardOutput=append:/var/log/voice-assistant.log
StandardError=append:/var/log/voice-assistant.log

[Install]
WantedBy=multi-user.target
EOF

# 10. Setup Log File
sudo touch /var/log/voice-assistant.log
sudo chown $USERNAME:$USERNAME /var/log/voice-assistant.log

# 11. Enable and Start Service
echo -e "${GREEN}=== Enabling and Starting Service ===${NC}"
sudo systemctl daemon-reload
sudo systemctl enable voice-assistant
sudo systemctl start voice-assistant

# 12. Test Audio Setup
echo -e "${GREEN}=== Testing Audio Setup ===${NC}"
echo "Testing microphone..."
arecord -d 2 test.wav
echo "Playing back test recording..."
aplay test.wav
rm test.wav

# Final Setup
echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo "Voice Assistant has been installed and configured"
echo -e "${YELLOW}Current Status:${NC}"
sudo systemctl status voice-assistant
echo ""
echo -e "${YELLOW}Important Commands:${NC}"
echo "- Check status: sudo systemctl status voice-assistant"
echo "- View logs: sudo journalctl -u voice-assistant -f"
echo "- Stop service: sudo systemctl stop voice-assistant"
echo "- Start service: sudo systemctl start voice-assistant"
echo "- Restart service: sudo systemctl restart voice-assistant"
echo ""
echo -e "${GREEN}Please reboot your Raspberry Pi to complete the setup:${NC}"
echo "sudo reboot"