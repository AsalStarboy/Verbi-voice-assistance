#!/bin/bash

# Audio diagnostic script for Raspberry Pi
# This script helps identify and fix audio configuration issues

echo "=== Raspberry Pi Audio Diagnostic Script ==="
echo "Date: $(date)"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "1. System Information:"
echo "   OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "   Kernel: $(uname -r)"
echo "   Architecture: $(uname -m)"
echo ""

echo "2. Audio Hardware Detection:"
echo "   USB Devices:"
lsusb | grep -i "audio\|sound\|plantronics\|headset" || echo "   No USB audio devices found"
echo ""

echo "   PCI Audio Devices:"
lspci | grep -i audio || echo "   No PCI audio devices found"
echo ""

echo "3. ALSA Configuration:"
echo "   Available playback devices:"
aplay -l 2>/dev/null || echo "   Error: Could not list playback devices"
echo ""

echo "   Available capture devices:"
arecord -l 2>/dev/null || echo "   Error: Could not list capture devices"
echo ""

echo "   Current ALSA configuration:"
if [ -f /home/pi/.asoundrc ]; then
    echo "   ~/.asoundrc exists:"
    cat /home/pi/.asoundrc | head -20
else
    echo "   No ~/.asoundrc file found"
fi
echo ""

echo "4. Audio Service Status:"
echo "   PulseAudio status:"
systemctl --user status pulseaudio 2>/dev/null || echo "   PulseAudio not running"
echo ""

echo "   JACK status:"
ps aux | grep jackd | grep -v grep || echo "   JACK not running"
echo ""

echo "5. Audio Device Testing:"
echo "   Testing default playback device:"
timeout 3 speaker-test -t sine -f 1000 -l 1 2>/dev/null && echo "   ✓ Playback test successful" || echo "   ✗ Playback test failed"
echo ""

echo "   Testing default capture device:"
timeout 3 arecord -d 1 /tmp/test_record.wav 2>/dev/null && echo "   ✓ Capture test successful" || echo "   ✗ Capture test failed"
rm -f /tmp/test_record.wav 2>/dev/null
echo ""

echo "6. Python Audio Libraries:"
python3 -c "import speech_recognition; print('   ✓ speech_recognition installed')" 2>/dev/null || echo "   ✗ speech_recognition not installed"
python3 -c "import pygame; print('   ✓ pygame installed')" 2>/dev/null || echo "   ✗ pygame not installed"
python3 -c "import pyaudio; print('   ✓ pyaudio installed')" 2>/dev/null || echo "   ✗ pyaudio not installed"
echo ""

echo "7. Process Analysis:"
echo "   Current audio-related processes:"
ps aux | grep -E "(python|arecord|aplay|pulse|jack)" | grep -v grep || echo "   No audio processes found"
echo ""

echo "8. Error Log Analysis:"
echo "   Recent ALSA errors in system log:"
journalctl --since "1 hour ago" | grep -i "alsa\|audio\|snd_" | tail -10 || echo "   No recent ALSA errors found"
echo ""

echo "=== Diagnostic Complete ==="
echo ""
echo "Recommendations:"
echo "1. If USB audio device is not detected, try replugging the device"
echo "2. If ALSA errors persist, run: sudo bash setup_audio.sh"
echo "3. If the voice assistant hangs, check for conflicting audio processes"
echo "4. Try running the voice assistant with: python3 -u run_voice_assistant.py"
echo "   (The -u flag disables output buffering for better debugging)"