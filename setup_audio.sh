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
    #!/bin/bash

# Audio setup script for Raspberry Pi with USB headset
# Fixes ALSA configuration issues and JACK server problems

echo "Setting up audio configuration for USB headset..."

# Stop any running audio services that might interfere
sudo killall -9 jackd 2>/dev/null || true
sudo killall -9 pulseaudio 2>/dev/null || true

# List available audio devices
echo "Available audio devices:"
aplay -l
arecord -l

# Detect USB audio device
USB_CARD=$(aplay -l | grep -i "usb\|plantronics\|headset" | head -1 | cut -d: -f1 | cut -d' ' -f2)
if [ -z "$USB_CARD" ]; then
    echo "No USB audio device found, using card 1 as default"
    USB_CARD=1
else
    echo "Found USB audio device at card $USB_CARD"
fi

# Create improved ALSA configuration
sudo tee /home/pi/.asoundrc << EOF
# Default ALSA configuration for USB headset
defaults.pcm.card $USB_CARD
defaults.ctl.card $USB_CARD

pcm.!default {
    type asym
    playback.pcm "playback"
    capture.pcm "capture"
}

pcm.playback {
    type plug
    slave {
        pcm "hw:$USB_CARD,0"
        rate 16000
        channels 1
        format S16_LE
    }
}

pcm.capture {
    type plug
    slave {
        pcm "hw:$USB_CARD,0"
        rate 16000
        channels 1
        format S16_LE
    }
}

ctl.!default {
    type hw
    card $USB_CARD
}

# Disable JACK audio server
pcm.jack {
    type null
}
EOF

# Set audio levels
echo "Setting audio levels..."
amixer -c $USB_CARD sset 'Mic' 80% 2>/dev/null || true
amixer -c $USB_CARD sset 'Capture' 80% 2>/dev/null || true
amixer -c $USB_CARD sset 'Master' 70% 2>/dev/null || true
amixer -c $USB_CARD sset 'PCM' 70% 2>/dev/null || true

# Disable PulseAudio auto-spawn to prevent conflicts
mkdir -p /home/pi/.config/pulse
echo "autospawn = no" > /home/pi/.config/pulse/client.conf

# Set proper permissions
chown pi:pi /home/pi/.asoundrc
chown -R pi:pi /home/pi/.config/pulse

echo "Audio configuration complete!"
echo "USB audio card: $USB_CARD"
echo "Please test with: arecord -d 5 test.wav && aplay test.wav"
    
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