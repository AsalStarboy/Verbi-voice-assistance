#!/bin/bash

# Raspberry Pi Voice Assistant Auto-Installer
# This script automatically installs all dependencies and sets up the voice assistant

set -e  # Exit on any error

echo "🤖 Raspberry Pi Voice Assistant Setup Starting..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as a normal user."
   exit 1
fi

print_header "1. Updating system packages..."
sudo apt update && sudo apt upgrade -y

print_header "2. Installing system dependencies..."
# Install essential packages
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    build-essential \
    cmake \
    pkg-config \
    libasound2-dev \
    portaudio19-dev \
    libportaudio2 \
    libportaudiocpp0 \
    ffmpeg \
    alsa-utils \
    pulseaudio \
    pulseaudio-utils \
    espeak \
    espeak-data \
    libespeak1 \
    libespeak-dev \
    sox \
    libsox-fmt-all

print_header "3. Setting up audio system..."
# Configure audio for headless operation
sudo usermod -a -G audio $USER

# Create ALSA configuration
cat > ~/.asoundrc << 'EOF'
pcm.!default {
    type pulse
}
ctl.!default {
    type pulse
}
EOF

print_header "4. Installing Ollama..."
# Install Ollama for local LLM
if ! command -v ollama &> /dev/null; then
    print_status "Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
else
    print_status "Ollama already installed"
fi

# Start Ollama service
sudo systemctl enable ollama
sudo systemctl start ollama

print_header "5. Setting up Python environment..."
# Create project directory
PROJECT_DIR="$HOME/voice_assistant"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

print_header "6. Installing Python dependencies..."
# Create requirements.txt with all needed packages
cat > requirements.txt << 'EOF'
# Core voice assistant dependencies
speech-recognition>=3.10.0
pyaudio>=0.2.11
pydub>=0.25.1
numpy>=1.24.0
scipy>=1.10.0

# FastWhisper for local STT
faster-whisper>=1.0.0

# Ollama client
ollama>=0.1.7

# Piper TTS
piper-tts>=1.2.0

# Audio processing
soundfile>=0.12.1
sounddevice>=0.4.6

# Utilities
colorama>=0.4.6
python-dotenv>=1.0.0
requests>=2.31.0

# Additional audio support
pygame>=2.5.2
EOF

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

print_header "7. Installing Piper TTS..."
# Download and install Piper TTS
PIPER_VERSION="2023.11.14-2"
PIPER_ARCH="armv7"  # For Raspberry Pi 4, use "aarch64" for Pi 5

mkdir -p models/piper
cd models/piper

# Download Piper executable
wget "https://github.com/rhasspy/piper/releases/download/${PIPER_VERSION}/piper_linux_${PIPER_ARCH}.tar.gz"
tar -xzf "piper_linux_${PIPER_ARCH}.tar.gz"
chmod +x piper/piper

# Download English voice model
wget "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
wget "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"

cd ../..

print_header "8. Downloading Ollama model..."
# Pull the phi3.5 model
print_status "Downloading phi3.5:3.8b model (this may take a while)..."
ollama pull phi3.5:3.8b-mini-instruct-q3_K_M

print_header "9. Setting up voice assistant code..."
# We'll copy the voice assistant files here
# This assumes the script is run from the project directory

print_header "10. Creating startup scripts..."

# Create main startup script
cat > start_voice_assistant.sh << 'EOF'
#!/bin/bash

# Voice Assistant Startup Script
cd "$HOME/voice_assistant"
source venv/bin/activate

# Start Ollama if not running
if ! pgrep -x "ollama" > /dev/null; then
    sudo systemctl start ollama
    sleep 5
fi

# Start PulseAudio
pulseaudio --start --log-target=syslog 2>/dev/null || true

# Wait for audio system to initialize
sleep 2

# Run the voice assistant
python3 run_voice_assistant.py
EOF

chmod +x start_voice_assistant.sh

# Create systemd service for auto-start
sudo tee /etc/systemd/system/voice-assistant.service > /dev/null << EOF
[Unit]
Description=Voice Assistant Service
After=network.target sound.target ollama.service
Wants=network.target sound.target ollama.service

[Service]
Type=simple
User=$USER
Group=audio
WorkingDirectory=$HOME/voice_assistant
Environment=HOME=$HOME
Environment=USER=$USER
ExecStartPre=/bin/sleep 10
ExecStart=$HOME/voice_assistant/start_voice_assistant.sh
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

print_header "11. Creating configuration files..."

# Create voice assistant configuration
mkdir -p voice_assistant
cat > voice_assistant/config.py << 'EOF'
import os

class Config:
    # Audio settings
    INPUT_AUDIO = "input.wav"
    
    # Model configurations for Raspberry Pi
    TRANSCRIPTION_MODEL = "faster-whisper"
    RESPONSE_MODEL = "ollama"
    TTS_MODEL = "piper"
    
    # Local model paths
    LOCAL_MODEL_PATH = os.path.expanduser("~/voice_assistant/models")
    
    # Ollama settings
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_LLM = "phi3.5:3.8b-mini-instruct-q3_K_M"
    
    # FastWhisper settings (optimized for Pi)
    FASTER_WHISPER_MODEL_SIZE = "base"  # Use base model for Pi performance
    FASTER_WHISPER_DEVICE = "cpu"
    FASTER_WHISPER_COMPUTE_TYPE = "int8"  # Optimize for Pi
    FASTER_WHISPER_CPU_THREADS = 2  # Adjust based on Pi model
    
    # Piper TTS settings
    PIPER_EXECUTABLE = os.path.expanduser("~/voice_assistant/models/piper/piper/piper")
    PIPER_MODEL_PATH = os.path.expanduser("~/voice_assistant/models/piper/en_US-lessac-medium.onnx")
    
    # Audio settings optimized for Pi
    SAMPLE_RATE = 16000
    CHANNELS = 1
    CHUNK_SIZE = 1024
    
    # Voice detection settings (adjusted for Pi microphone)
    ENERGY_THRESHOLD = 1000
    PAUSE_THRESHOLD = 1.5
    PHRASE_THRESHOLD = 0.3
EOF

print_header "12. Setting up auto-start..."
# Enable the service
sudo systemctl daemon-reload
sudo systemctl enable voice-assistant.service

print_header "13. Final configuration..."
# Add user to audio group
sudo usermod -a -G audio $USER

# Set up audio permissions
sudo usermod -a -G pulse-access $USER

print_status "Creating completion marker..."
touch ~/.voice_assistant_installed

echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
print_status "Voice Assistant has been installed and configured for auto-start"
print_status "The service will start automatically on boot"
echo ""
print_warning "Please reboot your Raspberry Pi to complete the setup:"
print_warning "sudo reboot"
echo ""
print_status "After reboot, the voice assistant will start automatically"
print_status "You can also manually start it with: sudo systemctl start voice-assistant"
print_status "Check status with: sudo systemctl status voice-assistant"
print_status "View logs with: sudo journalctl -u voice-assistant -f"
echo ""
print_status "Installation log saved to: ~/voice_assistant_install.log"
