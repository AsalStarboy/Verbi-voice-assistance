# Voice Assistant Troubleshooting Guide

## 🎤 Voice Detection Issues - Solutions

### Problem: "Not detecting voice"

### Solution 1: Check Windows Microphone Settings
1. Right-click on the speaker icon in the system tray
2. Select "Open Sound settings"
3. Under "Input", make sure the correct microphone is selected
4. Test your microphone by speaking - you should see the volume bar move
5. Set the input volume to at least 70%

### Solution 2: Update Audio Configuration
The voice assistant has been updated with more sensitive settings:
- Energy threshold lowered from 2000 to 1000 (more sensitive)
- Pause threshold increased from 1.0 to 1.5 seconds (more time to speak)
- Calibration duration increased to 2 seconds (better ambient noise detection)

### Solution 3: Manual Testing Commands

Run these commands one by one to test each component:

1. **Test Microphone:**
```powershell
cd "C:\Users\ADMIN\Documents\Vestas_Helmet\Verbi-voice-assistance"
C:/Users/ADMIN/Documents/Vestas_Helmet/.venv/Scripts/python.exe test_microphone.py
```

2. **Test Voice Assistant (with debug info):**
```powershell
C:/Users/ADMIN/Documents/Vestas_Helmet/.venv/Scripts/python.exe run_voice_assistant.py
```

### What to Look For:
- "Energy threshold after calibration: XXX" - should be between 300-1500
- "Recording started - Please speak now!" - this is when you should talk
- If timeout occurs repeatedly, microphone permissions or hardware issue

### Solution 4: Alternative Test
If the above doesn't work, try this simple test:
```powershell
echo "Hello test" | C:/Users/ADMIN/Documents/Vestas_Helmet/.venv/Scripts/piper.exe -m piper_models/en_US-lessac-medium.onnx -f test_output.wav
```
This tests if at least the TTS (text-to-speech) is working.

### Solution 5: Microphone Permissions
1. Go to Windows Settings > Privacy & Security > Microphone
2. Make sure "Microphone access" is turned ON
3. Make sure "Let apps access your microphone" is turned ON
4. Scroll down and make sure Python apps can access microphone

### Expected Behavior:
When working correctly, you should see:
1. "Calibrating for ambient noise..."
2. "Energy threshold after calibration: [number]"
3. "Recording started - Please speak now!"
4. [Speak here]
5. "Recording complete"
6. "You said: [your transcribed text]"
7. "Response: [AI response]"
8. [Audio plays with AI voice response]
