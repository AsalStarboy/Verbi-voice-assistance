# 🤖 Raspberry Pi Voice Assistant Setup Guide

## 📋 Prerequisites
- Raspberry Pi 3B+ or newer (4GB+ RAM recommended)
- MicroSD card (32GB+ recommended)
- USB microphone or USB audio adapter with microphone
- Speakers or headphones
- Internet connection for initial setup

## 🚀 One-Click Installation

### Option 1: Quick Setup (Recommended)
```bash
# Run this single command on your Raspberry Pi:
curl -fsSL https://raw.githubusercontent.com/AsalStarboy/Verbi-voice-assistance/main/quick_pi_setup.sh | bash
```

### Option 2: Manual Installation
```bash
# Clone the repository
git clone https://github.com/AsalStarboy/Verbi-voice-assistance.git
cd Verbi-voice-assistance

# Make installer executable
chmod +x install_pi.sh

# Run the installer
./install_pi.sh
```

## 📁 What Gets Installed

### System Packages
- Python 3 + pip + venv
- Audio libraries (ALSA, PulseAudio, PortAudio)
- Build tools and dependencies
- FFmpeg for audio processing

### AI Models (Downloaded Automatically)
- **Ollama**: Local LLM server
- **Phi3.5:3.8b**: Lightweight language model (2GB)
- **FastWhisper**: Local speech-to-text (base model)
- **Piper TTS**: Local text-to-speech (en_US-lessac-medium)

### Voice Assistant Components
- Complete voice assistant framework
- Optimized configuration for Pi hardware
- Auto-startup service
- Logging and monitoring

## ⚙️ Auto-Start Configuration

The installer automatically configures the voice assistant to:
- ✅ Start on boot
- ✅ Restart if it crashes
- ✅ Run in the background
- ✅ Log all activity

### Service Control Commands
```bash
# Check status
sudo systemctl status voice-assistant

# Start manually
sudo systemctl start voice-assistant

# Stop the service
sudo systemctl stop voice-assistant

# Disable auto-start
sudo systemctl disable voice-assistant

# View live logs
sudo journalctl -u voice-assistant -f
```

## 🎤 Audio Setup

### USB Microphone Setup
1. Connect USB microphone to Pi
2. Check if detected: `arecord -l`
3. Test recording: `arecord -D plughw:1,0 -d 5 test.wav`
4. Test playback: `aplay test.wav`

### Audio Configuration
The installer creates optimized audio settings in `~/.asoundrc`:
- Default device set to PulseAudio
- Automatic device detection
- Low-latency configuration

## 🔧 Performance Optimization

### Raspberry Pi Settings
The configuration is optimized for Pi hardware:
- **CPU Threads**: Limited to 2-4 based on Pi model
- **Memory**: Uses int8 quantization
- **Models**: Lightweight versions selected
- **Audio**: 16kHz mono for efficiency

### Memory Management
- Limited chat history (5 messages)
- Automatic cleanup of audio files
- Memory monitoring enabled

## 📊 System Requirements

### Minimum Specs
- **Pi Model**: Raspberry Pi 3B+
- **RAM**: 2GB (4GB recommended)
- **Storage**: 16GB (32GB recommended)
- **Audio**: USB microphone + speakers/headphones

### Performance Expectations
- **Startup Time**: ~30-60 seconds
- **Response Time**: 3-8 seconds
- **Model Loading**: First run takes 2-3 minutes
- **Memory Usage**: ~1.5-2GB during operation

## 🚨 Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Check logs
sudo journalctl -u voice-assistant -f

# Check Ollama status
sudo systemctl status ollama

# Restart everything
sudo systemctl restart ollama
sudo systemctl restart voice-assistant
```

#### 2. No Audio Input/Output
```bash
# List audio devices
arecord -l
aplay -l

# Test microphone
arecord -D plughw:1,0 -d 5 -f cd test.wav
aplay test.wav

# Restart audio
pulseaudio --kill
pulseaudio --start
```

#### 3. Ollama Model Issues
```bash
# Check available models
ollama list

# Re-download model
ollama pull phi3.5:3.8b-mini-instruct-q3_K_M

# Check Ollama logs
sudo journalctl -u ollama -f
```

#### 4. Performance Issues
```bash
# Check system resources
htop
free -h
df -h

# Monitor voice assistant
sudo journalctl -u voice-assistant -f
```

### Manual Startup (for testing)
```bash
cd ~/voice_assistant
source venv/bin/activate
./start_voice_assistant.sh
```

## 📝 Configuration Files

### Main Config: `~/voice_assistant/voice_assistant/config.py`
- Model settings
- Audio parameters
- Performance tuning

### Startup Script: `~/voice_assistant/start_voice_assistant.sh`
- Service initialization
- Health checks
- Logging setup

### Service File: `/etc/systemd/system/voice-assistant.service`
- Auto-start configuration
- User permissions
- Restart policies

## 🔄 Updates

### Update Voice Assistant
```bash
cd ~/Verbi-voice-assistance
git pull
./install_pi.sh  # Re-run installer if needed
```

### Update Models
```bash
ollama pull phi3.5:3.8b-mini-instruct-q3_K_M
```

## 📱 Usage

After installation, simply:
1. **Reboot your Pi**: `sudo reboot`
2. **Wait for startup**: ~60 seconds
3. **Start talking**: The assistant listens automatically
4. **Get responses**: AI responds through speakers

The voice assistant will:
- 🎤 Listen for your voice
- 🧠 Process with local AI (no internet needed for operation)
- 🔊 Respond with synthesized speech
- 🔄 Continue conversation with context

## 🆘 Getting Help

### Log Files
- Voice Assistant: `~/voice_assistant.log`
- System Service: `sudo journalctl -u voice-assistant`
- Ollama Service: `sudo journalctl -u ollama`

### Check Installation
```bash
# Verify all components
ls ~/voice_assistant/
ollama list
systemctl status voice-assistant
```

---
*🎉 Enjoy your local, private voice assistant on Raspberry Pi!*
