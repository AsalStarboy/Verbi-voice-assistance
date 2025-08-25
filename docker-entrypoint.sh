#!/bin/bash

# Docker startup script for Verbi Voice Assistant

echo "🐳 Starting Verbi Voice Assistant in Docker..."

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama service..."
while ! curl -s http://ollama:11434/api/tags > /dev/null 2>&1; do
    sleep 2
    echo "   Waiting for Ollama..."
done

echo "✅ Ollama is ready!"

# Pull the Phi3.5 model if not present
echo "📥 Checking for Phi3.5 model..."
if ! curl -s http://ollama:11434/api/tags | grep -q "phi3.5:3.8b-mini-instruct-q3_K_M"; then
    echo "   Pulling Phi3.5 model..."
    curl -X POST http://ollama:11434/api/pull -d '{"name": "phi3.5:3.8b-mini-instruct-q3_K_M"}'
    echo "✅ Model pulled!"
else
    echo "✅ Model already available!"
fi

# Check if piper models exist
if [ ! -f "piper_models/en_US-lessac-medium.onnx" ]; then
    echo "📥 Downloading Piper voice models..."
    mkdir -p piper_models
    wget -O piper_models/en_US-lessac-medium.onnx \
        "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
    wget -O piper_models/en_US-lessac-medium.onnx.json \
        "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"
    echo "✅ Piper models downloaded!"
fi

echo "🎤 Starting Voice Assistant..."
exec python run_voice_assistant.py
