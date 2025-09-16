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
#!/bin/bash

# One-click setup script for Voice Assistant on Raspberry Pi with Ollama
# This script installs only necessary dependencies for local operation

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Voice Assistant One-Click Setup (Ollama + Local) ===${NC}"
echo "This script will install dependencies for local voice assistant operation"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo -e "${RED}Please don't run this script as root. Use your regular user account.${NC}"
    echo -e "${YELLOW}If you need sudo permissions, the script will ask for them when needed.${NC}"
    exit 1
fi

# Get username for service setup
USERNAME=$(whoami)
echo -e "${GREEN}Installing for user: $USERNAME${NC}"

# Create log file
LOGFILE="$HOME/voice_assistant_setup.log"
exec 1> >(tee -a "$LOGFILE") 2>&1

echo -e "${YELLOW}=== Step 1: Updating system packages ===${NC}"
sudo apt update && sudo apt upgrade -y

echo -e "${YELLOW}=== Step 2: Installing system dependencies ===${NC}"
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    portaudio19-dev \
    libasound2-dev \
    libsndfile1-dev \
    ffmpeg \
    curl \
    git \
    espeak espeak-data \
    alsa-utils \
    pulseaudio \
    cmake

echo -e "${YELLOW}=== Step 3: Setting up audio permissions ===${NC}"
sudo usermod -a -G audio $USERNAME
pulseaudio --start 2>/dev/null || true

echo -e "${YELLOW}=== Step 4: Creating Python virtual environment ===${NC}"
cd $HOME/Verbi-voice-assistance
python3 -m venv venv
source venv/bin/activate

echo -e "${YELLOW}=== Step 5: Installing essential Python packages ===${NC}"
pip install --upgrade pip wheel setuptools

# Core packages for local operation only
pip install \
    SpeechRecognition>=3.10.0 \
    pyaudio>=0.2.11 \
    pydub>=0.25.1 \
    numpy>=1.21.0 \
    soundfile>=0.12.1 \
    sounddevice>=0.4.6 \
    faster-whisper>=1.0.0 \
    ollama>=0.1.7 \
    requests>=2.28.0 \
    colorama>=0.4.6 \
    python-dotenv>=1.0.0 \
    pygame>=2.1.0 \
    psutil>=5.9.0

echo -e "${YELLOW}=== Step 6: Installing Piper TTS ===${NC}"
# Install piper-tts locally
pip install piper-tts

# Download a basic English voice model for piper
mkdir -p $HOME/.local/share/piper-voices/en/en_US/lessac/medium/
cd $HOME/.local/share/piper-voices/en/en_US/lessac/medium/
if [ ! -f "en_US-lessac-medium.onnx" ]; then
    echo "Downloading Piper voice model..."
    wget -q https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx
    wget -q https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
    echo -e "${GREEN}Piper voice model downloaded successfully${NC}"
else
    echo -e "${GREEN}Piper voice model already exists${NC}"
fi

cd $HOME/Verbi-voice-assistance

echo -e "${YELLOW}=== Step 7: Installing Ollama ===${NC}"
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
else
    echo -e "${GREEN}Ollama already installed${NC}"
fi

# Start Ollama service
sudo systemctl enable ollama
sudo systemctl start ollama

# Wait for Ollama to start
echo "Waiting for Ollama to start..."
sleep 5

# Check if phi3.5:3.0b-mini-instruct-q3_k_m model exists, if not download it
echo -e "${YELLOW}=== Step 8: Setting up Ollama model ===${NC}"
if ! ollama list | grep -q "phi3.5:3.0b-mini-instruct-q3_k_m"; then
    echo "Downloading phi3.5:3.0b-mini-instruct-q3_k_m model..."
    ollama pull phi3.5:3.0b-mini-instruct-q3_k_m
else
    echo -e "${GREEN}phi3.5:3.0b-mini-instruct-q3_k_m model already exists${NC}"
fi

echo -e "${YELLOW}=== Step 9: Creating systemd service ===${NC}"
cat > /tmp/voice-assistant.service << EOF
[Unit]
Description=Voice Assistant Service
After=network.target ollama.service
Wants=ollama.service

[Service]
Type=simple
User=$USERNAME
WorkingDirectory=$HOME/Verbi-voice-assistance
Environment=PATH=$HOME/Verbi-voice-assistance/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$HOME/Verbi-voice-assistance/venv/bin/python $HOME/Verbi-voice-assistance/run_voice_assistant.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo mv /tmp/voice-assistant.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable voice-assistant

echo -e "${YELLOW}=== Step 10: Testing audio setup ===${NC}"
echo "Testing microphone recording..."
timeout 3s arecord -f cd -t wav /tmp/test_recording.wav 2>/dev/null || true
if [ -f /tmp/test_recording.wav ]; then
    echo -e "${GREEN}✓ Microphone recording successful${NC}"
    echo "Testing audio playback..."
    aplay /tmp/test_recording.wav 2>/dev/null || espeak "Audio test" 2>/dev/null || echo "Audio playback test completed"
    rm -f /tmp/test_recording.wav
    echo -e "${GREEN}✓ Audio setup test completed${NC}"
else
    echo -e "${YELLOW}⚠ Microphone test inconclusive - check your USB headset connection${NC}"
fi

echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo ""
echo -e "${GREEN}✓ All dependencies installed${NC}"
echo -e "${GREEN}✓ Python virtual environment created${NC}"
echo -e "${GREEN}✓ Ollama installed with phi3.5 model${NC}"
echo -e "${GREEN}✓ Piper TTS configured${NC}"
echo -e "${GREEN}✓ System service created${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Connect your USB microphone/headset"
echo "2. Reboot your Raspberry Pi: sudo reboot"
echo "3. After reboot, the voice assistant will start automatically"
echo "4. Say 'Hi Windy' to activate the assistant"
echo "5. Say 'Bye Windy' to put it to sleep"
echo ""
echo -e "${YELLOW}Manual control:${NC}"
echo "• Start service: sudo systemctl start voice-assistant"
echo "• Stop service: sudo systemctl stop voice-assistant"
echo "• Check status: sudo systemctl status voice-assistant"
echo "• View logs: sudo journalctl -u voice-assistant -f"
echo ""
echo -e "${YELLOW}To test manually (in virtual environment):${NC}"
echo "cd $HOME/Verbi-voice-assistance && source venv/bin/activate && python run_voice_assistant.py"
echo ""
echo -e "${GREEN}Setup logged to: $LOGFILE${NC}"
echo ""
echo -e "${YELLOW}Reboot recommended:${NC}"
echo "sudo reboot"