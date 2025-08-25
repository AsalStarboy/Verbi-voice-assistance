# Test script for local voice assistant setup

import logging
from voice_assistant.transcription import transcribe_audio
from voice_assistant.response_generation import generate_response
from voice_assistant.text_to_speech import text_to_speech
from voice_assistant.config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_local_setup():
    """Test the complete local voice assistant pipeline"""
    
    print("🧪 Testing Local Voice Assistant Setup")
    print("=" * 50)
    
    # Test TTS first
    print("\n1. 🔊 Testing Piper TTS...")
    try:
        test_text = "Hello! This is a test of the local Piper text to speech system."
        text_to_speech(Config.TTS_MODEL, None, test_text, "test_tts_output.wav")
        print("✅ Piper TTS: SUCCESS")
    except Exception as e:
        print(f"❌ Piper TTS: FAILED - {e}")
        return
    
    # Test LLM
    print("\n2. 🧠 Testing Ollama LLM...")
    try:
        chat_history = [
            {"role": "system", "content": "You are a helpful assistant. Respond briefly."},
            {"role": "user", "content": "Hello, introduce yourself in one sentence."}
        ]
        response = generate_response(Config.RESPONSE_MODEL, None, chat_history, None)
        print(f"✅ Ollama LLM: SUCCESS - Response: {response}")
    except Exception as e:
        print(f"❌ Ollama LLM: FAILED - {e}")
        return
    
    print("\n🎉 All local components are working!")
    print("Your voice assistant is ready for voice input.")
    print("\nTo test with voice:")
    print("1. Make sure you have a microphone connected")
    print("2. Run: python run_voice_assistant.py")
    print("3. Speak when prompted")
    print("4. Say 'goodbye' to exit")

if __name__ == "__main__":
    test_local_setup()
