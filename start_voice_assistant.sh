#!/bin/bash

# Voice Assistant Startup Script for Raspberry Pi
# This script handles all the startup requirements

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a ~/voice_assistant.log
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a ~/voice_assistant.log
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a ~/voice_assistant.log
}

log "🤖 Starting Voice Assistant on Raspberry Pi..."

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    log "✅ Virtual environment activated"
else
    error "❌ Virtual environment not found! Please run install_pi.sh first"
    exit 1
fi

# Check if Ollama is running
log "🔍 Checking Ollama service..."
if ! pgrep -x "ollama" > /dev/null; then
    log "🚀 Starting Ollama service..."
    sudo systemctl start ollama
    sleep 10  # Give Ollama time to start
    
    # Wait for Ollama to be ready
    max_attempts=30
    attempt=0
    while ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
        if [ $attempt -ge $max_attempts ]; then
            error "❌ Ollama failed to start after $max_attempts attempts"
            exit 1
        fi
        log "⏳ Waiting for Ollama to be ready... (attempt $((attempt+1))/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    log "✅ Ollama is ready"
else
    log "✅ Ollama is already running"
fi

# Check if required model is available
log "🔍 Checking if phi3.5 model is available..."
if ! ollama list | grep -q "phi3.5:3.8b-mini-instruct-q3_K_M"; then
    log "📥 Downloading phi3.5 model (this may take a while)..."
    ollama pull phi3.5:3.8b-mini-instruct-q3_K_M
    log "✅ Model downloaded successfully"
else
    log "✅ phi3.5 model is available"
fi

# Start PulseAudio for audio handling
log "🔊 Setting up audio system..."
pulseaudio --start --log-target=syslog 2>/dev/null || warning "PulseAudio may already be running"

# Set audio permissions
sudo chmod 666 /dev/snd/* 2>/dev/null || warning "Could not set audio permissions"

# Wait for audio system to initialize
sleep 3

# Check microphone
log "🎤 Checking microphone..."
if arecord -l | grep -q "card"; then
    log "✅ Audio devices detected"
else
    warning "⚠️  No audio input devices detected"
fi

# Check if Piper executable exists
if [ -f "models/piper/piper/piper" ]; then
    log "✅ Piper TTS is available"
else
    error "❌ Piper TTS not found! Please run install_pi.sh"
    exit 1
fi

# Check if Piper model exists
if [ -f "models/piper/en_US-lessac-medium.onnx" ]; then
    log "✅ Piper voice model is available"
else
    error "❌ Piper voice model not found! Please run install_pi.sh"
    exit 1
fi

# Set environment variables for optimal Pi performance
export MALLOC_ARENA_MAX=2  # Reduce memory fragmentation
export OMP_NUM_THREADS=2   # Limit OpenMP threads

log "🚀 Starting Voice Assistant..."
log "📝 Logs are being saved to ~/voice_assistant.log"
log "🛑 Press Ctrl+C to stop the assistant"

# Start the voice assistant with error handling
python3 run_voice_assistant.py 2>&1 | tee -a ~/voice_assistant.log

log "🛑 Voice Assistant stopped"
