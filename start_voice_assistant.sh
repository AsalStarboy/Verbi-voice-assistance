#!/bin/bash

# SPEED OPTIMIZED Voice Assistant Startup Script for Raspberry Pi
# Fast startup with minimal checks for immediate response

cd "$(dirname "$0")"

echo "🚀 Fast Starting Windy Voice Assistant..."

# Quick venv activation
source venv/bin/activate 2>/dev/null || { echo "❌ No venv found"; exit 1; }

# Pre-load Ollama model in background for instant first response
ollama run phi3.5:3.0b-mini-instruct-q3_k_m "Ready" > /dev/null 2>&1 &

# Set optimal performance environment variables
export PYTHONUNBUFFERED=1          # No buffering for faster output
export MALLOC_ARENA_MAX=2           # Reduce memory fragmentation
export OMP_NUM_THREADS=1            # Single thread for Pi efficiency
export PYTHONOPTIMIZE=1             # Enable Python optimizations

# Quick audio setup
pulseaudio --start 2>/dev/null &

echo "⚡ Launching (optimized for SPEED)..."

# Start with Python optimizations enabled
python3 -O run_voice_assistant.py

echo "� Voice Assistant stopped."
