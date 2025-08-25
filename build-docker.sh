#!/bin/bash
# Build script for Verbi Voice Assistant Docker

echo "🏗️ Building Verbi Voice Assistant Docker Image..."

# Build the Docker image
docker build -t verbi-voice-assistant:latest .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    echo "📦 Image: verbi-voice-assistant:latest"
    echo ""
    echo "🚀 To run the voice assistant:"
    echo "   Windows: docker-compose -f docker-compose.windows.yml up"
    echo "   Linux/macOS: docker-compose up"
else
    echo "❌ Docker build failed!"
    exit 1
fi
