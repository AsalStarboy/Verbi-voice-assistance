# 🎙️ Wake Word System Documentation

## 🌟 Overview
The voice assistant now features an intelligent wake word system that allows for:
- **Energy-efficient sleep mode** - Only minimal processing when waiting
- **Wake word activation** - Say "Hi Windy" to start conversation  
- **Sleep command** - Say "Bye Windy" to return to sleep mode
- **Hands-free operation** - Perfect for always-on voice assistant

## 🗣️ Voice Commands

### ⏰ Wake Up Commands
- **"Hi Windy"** (primary wake word)
- **"Hey Windy"** (alternative)
- **"Hi Wendy"** / **"Hey Wendy"** (handles misheard variations)

### 😴 Sleep Commands  
- **"Bye Windy"** (primary sleep word)
- **"Goodbye Windy"**
- **"See you later Windy"**
- **"Bye Wendy"** / **"Goodbye Wendy"** (handles misheard variations)

### 🔌 Shutdown Commands
- **"Shutdown"** / **"Turn off"** / **"Exit program"** / **"Quit"**

## 🔄 Operating Modes

### 💤 Sleep Mode
**What it does:**
- Continuously listens for wake word only
- Uses minimal CPU and memory resources
- Optimized audio settings for wake word detection
- No LLM processing until wake word detected

**Audio Settings:**
- Lower energy threshold (more sensitive)
- Shorter timeout (5 seconds)
- Faster processing for wake word detection

**Status:** `Voice Assistant sleeping - Say 'Hi Windy' to wake up...`

### 🎤 Active Mode  
**What it does:**
- Full conversation capabilities
- Complete STT → LLM → TTS pipeline
- Maintains conversation context
- Responds to all user input until sleep command

**Features:**
- Context-aware conversations
- Memory of previous messages in session
- Full Windy personality responses
- High-quality audio processing

**Status:** `Voice Assistant active - Start talking! Say 'Bye Windy' to sleep.`

## ⚙️ Configuration

### Wake Word Settings (config.py)
```python
# Wake Word Configuration
WAKE_WORD = "hi windy"
SLEEP_WORD = "bye windy"
WAKE_WORD_TIMEOUT = 5  # Seconds to listen for wake word
CONVERSATION_TIMEOUT = 30  # Seconds to wait for user input

# Audio settings for wake word detection
WAKE_WORD_ENERGY_THRESHOLD = 800  # Lower = more sensitive
WAKE_WORD_PAUSE_THRESHOLD = 1.0   # Shorter pause for wake word
```

### Raspberry Pi Settings (config_pi.py)
```python
# Pi-optimized wake word settings
WAKE_WORD_ENERGY_THRESHOLD = 600  # Even lower for Pi microphones
WAKE_WORD_PAUSE_THRESHOLD = 1.0   
```

## 🎯 Usage Flow

### Standard Operation
```
1. 💤 Assistant starts in sleep mode
2. 🗣️ User: "Hi Windy"  
3. 🎉 Wake word detected → Activates
4. 🤖 Windy: "Hello! I'm Windy, your voice assistant. How can I help you?"
5. 💬 Normal conversation...
6. 🗣️ User: "Bye Windy"
7. 😴 Sleep word detected → Returns to sleep
8. 🤖 Windy: "Goodbye! Say 'Hi Windy' when you need me again."
9. 💤 Back to sleep mode
```

### Raspberry Pi Auto-Start
```
1. 🔌 Pi powers on
2. 🚀 Service auto-starts  
3. 💤 Enters sleep mode automatically
4. 👂 Always listening for "Hi Windy"
5. ♻️ Cycle continues until shutdown
```

## 🔧 Advanced Features

### Pattern Recognition
The system uses regex patterns to catch variations:
- **Phonetic similarities**: "Windy" vs "Wendy"
- **Alternative greetings**: "Hi" vs "Hey"
- **Casual variations**: Different goodbye phrases

### Error Handling
- **Audio failures**: Automatic retry with logging
- **Transcription errors**: Graceful handling of empty results
- **Model errors**: Service continues running, logs issues
- **Hardware issues**: Restarts automatically via systemd

### Performance Optimization
- **Sleep mode**: Minimal resource usage
- **Wake detection**: Fast processing, no LLM
- **Memory management**: Automatic cleanup of audio files
- **Pi-specific**: Optimized thresholds and timeouts

## 📊 System Impact

### Resource Usage
**Sleep Mode:**
- CPU: ~5-10% (wake word processing only)
- Memory: ~200MB (base system)
- Disk: Minimal (only wake word audio files)

**Active Mode:**
- CPU: ~20-40% (full AI pipeline)  
- Memory: ~1-1.5GB (LLM + models loaded)
- Disk: Active file management

### Battery Life (for portable setups)
- **Sleep mode**: 5-10x longer battery life vs always active
- **Smart activation**: Only processes when needed
- **Pi optimization**: Minimal power consumption

## 🚨 Troubleshooting

### Wake Word Not Detected
```bash
# Check microphone
arecord -l

# Test wake word sensitivity
# Lower the threshold in config
WAKE_WORD_ENERGY_THRESHOLD = 400  # More sensitive

# Check logs
sudo journalctl -u voice-assistant -f
```

### False Wake Activations
```bash
# Increase threshold to reduce sensitivity
WAKE_WORD_ENERGY_THRESHOLD = 1200  # Less sensitive

# Adjust pause threshold
WAKE_WORD_PAUSE_THRESHOLD = 1.5  # Require longer phrases
```

### Assistant Won't Sleep
```bash
# Check sleep word patterns in logs
# Make sure to say the complete phrase clearly
# Try: "Bye Windy" (pause between words)
```

## 🎉 Benefits

### For Users
- ✅ **Always ready** - No manual activation needed
- ✅ **Natural interaction** - Just talk like to a person
- ✅ **Privacy friendly** - Only processes after wake word
- ✅ **Energy efficient** - Smart power management

### For Developers  
- ✅ **Modular design** - Easy to customize wake words
- ✅ **Performance optimized** - Separate modes for efficiency
- ✅ **Error resilient** - Robust error handling
- ✅ **Pi compatible** - Works great on Raspberry Pi

---
*🎤 Say "Hi Windy" and start your conversation!*
