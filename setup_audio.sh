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

# Enhanced Audio setup script for Raspberry Pi with USB headset
# Fixes ALSA configuration issues and JACK server problems

echo "🔧 Enhanced Audio Setup for Raspberry Pi"
echo "========================================"

# Stop any running audio services that might interfere
echo "🛑 Stopping conflicting audio services..."
sudo killall -9 jackd 2>/dev/null || true
sudo killall -9 pulseaudio 2>/dev/null || true
sudo killall -9 pipewire 2>/dev/null || true

# Check if user is in audio group
if ! groups $USER | grep -q audio; then
    echo "👤 Adding user to audio group..."
    sudo usermod -a -G audio $USER
    echo "⚠️  You may need to log out and back in for group changes to take effect"
fi

# List available audio devices
echo "🎧 Available audio devices:"
echo "Playback devices:"
aplay -l 2>/dev/null || echo "❌ No playback devices found"
echo "Capture devices:"
arecord -l 2>/dev/null || echo "❌ No capture devices found"

# More comprehensive USB audio device detection
USB_CARD=""
USB_DEVICE=""

# Method 1: Check aplay output
USB_INFO=$(aplay -l 2>/dev/null | grep -i "usb\|plantronics\|headset\|webcam\|microphone" | head -1)
if [ ! -z "$USB_INFO" ]; then
    USB_CARD=$(echo "$USB_INFO" | cut -d: -f1 | cut -d' ' -f2)
    USB_DEVICE=$(echo "$USB_INFO" | cut -d: -f2 | cut -d',' -f1 | xargs)
fi

# Method 2: Check /proc/asound/cards if Method 1 fails
if [ -z "$USB_CARD" ]; then
    USB_CARD=$(cat /proc/asound/cards 2>/dev/null | grep -i "usb\|headset\|webcam" | head -1 | cut -d' ' -f2)
fi

# Method 3: Default fallback
if [ -z "$USB_CARD" ]; then
    echo "⚠️  No specific USB audio device found, trying card 1 as default"
    USB_CARD=1
    USB_DEVICE="Default USB Audio"
else
    echo "✅ Found USB audio device: Card $USB_CARD - $USB_DEVICE"
fi

# Create comprehensive ALSA configuration
echo "📝 Creating ALSA configuration..."

# Backup existing configuration
if [ -f /home/pi/.asoundrc ]; then
    cp /home/pi/.asoundrc /home/pi/.asoundrc.backup.$(date +%s)
    echo "💾 Backed up existing .asoundrc"
fi

# Create the main ALSA configuration
sudo tee /home/pi/.asoundrc << EOF
# Enhanced ALSA configuration for USB headset - Raspberry Pi optimized
# Generated on $(date)

# Set default card
defaults.pcm.card $USB_CARD
defaults.ctl.card $USB_CARD

# Main default PCM device with error handling
pcm.!default {
    type asym
    playback.pcm "playback_fixed"
    capture.pcm "capture_fixed"
}

# Robust playback configuration
pcm.playback_fixed {
    type plug
    slave {
        pcm "hw:$USB_CARD,0"
        rate 16000
        channels 1
        format S16_LE
        period_time 125000
        buffer_time 500000
    }
    hint {
        show on
        description "USB Audio Playback"
    }
}

# Robust capture configuration
pcm.capture_fixed {
    type plug
    slave {
        pcm "hw:$USB_CARD,0"
        rate 16000
        channels 1
        format S16_LE
        period_time 125000
        buffer_time 500000
    }
    hint {
        show on
        description "USB Audio Capture"
    }
}

# Control interface
ctl.!default {
    type hw
    card $USB_CARD
}

# Disable problematic audio systems
pcm.jack {
    type null
}

pcm.pulse {
    type null
}

# Alternative configurations for fallback
pcm.usb_direct {
    type hw
    card $USB_CARD
    device 0
}

pcm.usb_plughw {
    type plughw
    card $USB_CARD
    device 0
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