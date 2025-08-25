# 🐳 Docker Deployment Guide

This guide explains how to run the Verbi Voice Assistant using Docker containers.

## 📋 Prerequisites

- Docker Desktop installed
- Docker Compose installed
- At least 4GB RAM available
- Microphone access configured

## 🚀 Quick Start

### Windows Users:
```bash
# Build the image
.\build-docker.bat

# Run the voice assistant
docker-compose -f docker-compose.windows.yml up
```

### Linux/macOS Users:
```bash
# Build the image
chmod +x build-docker.sh
./build-docker.sh

# Run the voice assistant
docker-compose up
```

## 📁 Project Structure

```
verbi-voice-assistance/
├── Dockerfile                    # Main container definition
├── docker-compose.yml          # Linux/macOS compose file
├── docker-compose.windows.yml  # Windows-specific compose file
├── docker-entrypoint.sh        # Container startup script
├── .dockerignore               # Files to exclude from build
├── build-docker.sh             # Linux/macOS build script
├── build-docker.bat            # Windows build script
└── ...
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
# Optional API keys (if you want to use cloud services)
OPENAI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
DEEPGRAM_API_KEY=your_key_here

# Local model paths (handled automatically)
PIPER_SERVER_URL=http://localhost:5150
```

### Volume Mounts
- `./piper_models:/app/piper_models` - Piper voice models
- `./audio_files:/app/audio_files` - Audio recordings
- `./.env:/app/.env` - Environment configuration

## 🎯 Services

### Voice Assistant Container
- **Image**: Built from Dockerfile
- **Purpose**: Runs the main voice assistant
- **Ports**: 8000, 5150
- **Models**: 
  - faster-whisper (STT)
  - Piper TTS (local)

### Ollama Container
- **Image**: `ollama/ollama:latest`
- **Purpose**: Runs the Phi3.5 language model
- **Port**: 11434
- **Model**: `phi3.5:3.8b-mini-instruct-q3_K_M`

## 📦 Docker Commands

### Build Image
```bash
docker build -t verbi-voice-assistant:latest .
```

### Run Single Container
```bash
docker run -it --rm \
  -v $(pwd)/piper_models:/app/piper_models \
  -v $(pwd)/audio_files:/app/audio_files \
  --device /dev/snd:/dev/snd \
  verbi-voice-assistant:latest
```

### Stop All Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f voice-assistant
docker-compose logs -f ollama
```

### Restart Services
```bash
docker-compose restart
```

## 🔊 Audio Configuration

### Windows
- Ensure Docker Desktop has access to audio devices
- May require running Docker Desktop as administrator
- Audio passthrough can be limited in containers

### Linux
- Audio devices mounted via `/dev/snd`
- PulseAudio configuration may be needed
- Consider running with `--privileged` for full audio access

### macOS
- Audio support varies by Docker version
- May require additional audio forwarding setup

## 🐛 Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs

# Rebuild image
docker-compose build --no-cache
```

### Audio Issues
```bash
# Windows: Check Docker Desktop audio settings
# Linux: Verify audio device permissions
ls -la /dev/snd/

# Test audio in container
docker exec -it verbi-voice-assistant bash
aplay -l  # List audio devices
```

### Model Download Issues
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Manual model pull
docker exec -it ollama-server ollama pull phi3.5:3.8b-mini-instruct-q3_K_M
```

### Performance Issues
- Increase Docker memory limit (6GB+ recommended)
- Use SSD storage for model files
- Ensure adequate CPU resources

## 📊 Resource Usage

| Component | RAM | Storage | CPU |
|-----------|-----|---------|-----|
| Voice Assistant | 1GB | 500MB | 1 core |
| Ollama + Phi3.5 | 2GB | 2GB | 1 core |
| Piper Models | 100MB | 65MB | - |
| **Total** | **3GB** | **2.5GB** | **2 cores** |

## 🔒 Security Notes

- Containers run with limited privileges
- Audio device access required for microphone
- No external network access needed (fully local)
- Model files downloaded only on first run

## 🚀 Production Deployment

For production use:
1. Use specific image tags instead of `latest`
2. Set up proper volume backups
3. Configure resource limits
4. Set up health checks
5. Use Docker secrets for sensitive data

## 📝 Notes

- First run will download models (~2.5GB)
- Startup time: 2-3 minutes on first run
- Subsequent starts: 30-60 seconds
- All AI processing runs locally (no internet required after setup)
