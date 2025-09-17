#!/bin/bash

# Simple audio test script for voice assistant
# This helps debug audio recording and transcription issues

echo "🔧 Voice Assistant Audio Test"
echo "=============================="

# Check if in virtual environment
if [[ "$VIRTUAL_ENV" ]]; then
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
else
    echo "⚠️  Virtual environment not active - activating..."
    source venv/bin/activate || { echo "❌ Failed to activate venv"; exit 1; }
fi

# Test 1: Record a short audio sample
echo ""
echo "🎤 Test 1: Recording 3-second audio sample..."
timeout 5 arecord -d 3 -f cd test_audio.wav 2>/dev/null
if [ -f "test_audio.wav" ] && [ -s "test_audio.wav" ]; then
    echo "✅ Audio recording successful"
    echo "   File size: $(du -h test_audio.wav | cut -f1)"
else
    echo "❌ Audio recording failed"
    exit 1
fi

# Test 2: Play back the audio
echo ""
echo "🔊 Test 2: Playing back recorded audio..."
aplay test_audio.wav 2>/dev/null && echo "✅ Audio playback successful" || echo "❌ Audio playback failed"

# Test 3: Test Python transcription
echo ""
echo "🔄 Test 3: Testing transcription..."
python3 -c "
import sys
sys.path.append('.')
from voice_assistant.transcription import transcribe_audio
from voice_assistant.config import Config

try:
    result = transcribe_audio(Config.TRANSCRIPTION_MODEL, None, 'test_audio.wav')
    if result and result.strip():
        print(f'✅ Transcription successful: \"{result.strip()}\"')
    else:
        print('⚠️  Transcription returned empty result')
except Exception as e:
    print(f'❌ Transcription failed: {e}')
"

# Test 4: Test wake word detection
echo ""
echo "🎯 Test 4: Testing wake word detection..."
python3 -c "
import sys
sys.path.append('.')
from run_voice_assistant import detect_wake_word

# Test with sample wake word text
test_phrases = ['hi windy', 'hello windy', 'hey windy', 'hi when do', 'high wind']
for phrase in test_phrases:
    result = detect_wake_word(phrase)
    status = '✅' if result else '❌'
    print(f'{status} \"{phrase}\" -> {result}')
"

# Clean up
rm -f test_audio.wav

echo ""
echo "🏁 Audio test complete!"
echo "If any tests failed, check:"
echo "  - USB headset is connected and recognized"
echo "  - ALSA configuration is correct (run: bash setup_audio.sh)"
echo "  - Virtual environment has all dependencies (run: bash one_click_setup.sh)"