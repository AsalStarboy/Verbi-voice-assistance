#!/usr/bin/env python3
"""
Microphone test script to diagnose voice detection issues
"""

import speech_recognition as sr
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_microphone():
    """Test microphone functionality and settings"""
    
    print("🎤 Microphone Diagnostics")
    print("=" * 50)
    
    # List available microphones
    print("\n📍 Available Microphones:")
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"  {index}: {name}")
    
    # Test with default microphone
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print(f"\n🔧 Default Microphone: {source}")
            print("🔍 Testing ambient noise calibration...")
            
            # Record ambient noise for calibration
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print(f"   Energy threshold after calibration: {recognizer.energy_threshold}")
            
            # Test with lower energy threshold for better sensitivity
            recognizer.energy_threshold = max(recognizer.energy_threshold * 0.5, 300)
            recognizer.pause_threshold = 1.5
            recognizer.phrase_threshold = 0.1
            
            print(f"   Adjusted energy threshold: {recognizer.energy_threshold}")
            print(f"   Pause threshold: {recognizer.pause_threshold}")
            print(f"   Phrase threshold: {recognizer.phrase_threshold}")
            
            print("\n🎙️ SPEAK NOW - Say something (you have 10 seconds)...")
            
            try:
                # Listen for audio
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
                print("✅ Audio captured successfully!")
                
                # Try to save the audio
                with open("mic_test.wav", "wb") as f:
                    f.write(audio.get_wav_data())
                print("✅ Audio saved as 'mic_test.wav'")
                
            except sr.WaitTimeoutError:
                print("❌ No speech detected - timeout occurred")
                print("💡 Try speaking louder or closer to the microphone")
                
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check if microphone is connected and working")
        print("2. Check Windows sound settings")
        print("3. Try running as administrator")
        print("4. Check if another application is using the microphone")

if __name__ == "__main__":
    test_microphone()
