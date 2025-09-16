#!/bin/bash

# Audio configuration script for USB headset on Raspberry Pi
# Run this if you have audio issues

echo "=== USB Headset Audio Setup for Raspberry Pi ==="

# List audio devices
echo "Available audio capture devices:"
arecord -l

echo ""
echo "Available audio playback devices:"
aplay -l

echo ""
echo "Checking for USB audio devices..."
lsusb | grep -i audio

# Find USB audio card number
USB_CARD=$(arecord -l | grep -i usb | head -1 | sed 's/card \([0-9]\).*/\1/')

if [ -n "$USB_CARD" ]; then
    echo ""
    echo "Found USB audio device at card $USB_CARD"
    
    # Create .asoundrc for USB headset
    cat > ~/.asoundrc << EOF
pcm.!default {
    type hw
    card $USB_CARD
}
ctl.!default {
    type hw
    card $USB_CARD
}
EOF
    
    echo "Created ~/.asoundrc configuration file"
    echo "USB headset (card $USB_CARD) set as default audio device"
    
    # Test recording
    echo ""
    echo "Testing microphone (3 seconds)..."
    timeout 3s arecord -f cd test.wav
    
    if [ -f test.wav ]; then
        echo "Testing playback..."
        aplay test.wav
        rm -f test.wav
        echo "Audio test completed successfully!"
    else
        echo "Recording test failed. Check your USB headset connection."
    fi
    
else
    echo "No USB audio device found. Please check your headset connection."
    echo "Available cards:"
    cat /proc/asound/cards
fi

echo ""
echo "Audio configuration complete."
echo "If you still have issues, try:"
echo "1. Unplug and reconnect your USB headset"
echo "2. Run: pulseaudio --kill && pulseaudio --start"
echo "3. Reboot your Raspberry Pi"