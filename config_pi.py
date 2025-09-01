# Raspberry Pi Voice Assistant Configuration
# Optimized for Raspberry Pi hardware

import os

class Config:
    # Audio file settings
    INPUT_AUDIO = "input.wav"
    
    # Model configurations - all local for Pi
    TRANSCRIPTION_MODEL = "faster-whisper"
    RESPONSE_MODEL = "ollama"
    TTS_MODEL = "piper"
    
    # Local model paths
    LOCAL_MODEL_PATH = os.path.expanduser("~/voice_assistant/models")
    
    # Ollama settings
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_LLM = "phi3.5:3.8b-mini-instruct-q3_K_M"
    
    # FastWhisper settings (optimized for Raspberry Pi performance)
    FASTER_WHISPER_MODEL_SIZE = "base"  # Use base model for better Pi performance
    FASTER_WHISPER_DEVICE = "cpu"
    FASTER_WHISPER_COMPUTE_TYPE = "int8"  # Lower precision for Pi
    FASTER_WHISPER_CPU_THREADS = 2  # Adjust based on your Pi model (Pi 4: 4, Pi 3: 4, Pi Zero: 1)
    FASTER_WHISPER_NUM_WORKERS = 1
    
    # Wake Word Configuration for Pi
    WAKE_WORD = "hi windy"
    SLEEP_WORD = "bye windy"
    WAKE_WORD_TIMEOUT = 5  # Seconds to listen for wake word
    CONVERSATION_TIMEOUT = 30  # Seconds to wait for user input in conversation
    
    # Audio settings for wake word detection (Pi optimized)
    WAKE_WORD_ENERGY_THRESHOLD = 600  # Lower threshold for Pi microphones
    WAKE_WORD_PAUSE_THRESHOLD = 1.0   # Shorter pause for wake word detection
    
    # Piper TTS settings
    PIPER_EXECUTABLE = os.path.expanduser("~/voice_assistant/models/piper/piper/piper")
    PIPER_MODEL_PATH = os.path.expanduser("~/voice_assistant/models/piper/en_US-lessac-medium.onnx")
    
    # Audio settings optimized for Pi
    SAMPLE_RATE = 16000  # Standard rate for speech
    CHANNELS = 1  # Mono for efficiency
    CHUNK_SIZE = 1024  # Smaller chunks for Pi
    
    # Voice detection settings (tuned for Pi microphones)
    ENERGY_THRESHOLD = 800  # Lower threshold for Pi microphones
    PAUSE_THRESHOLD = 1.5  # Time to wait for speech to end
    PHRASE_THRESHOLD = 0.3  # Minimum phrase length
    
    # Performance settings for Pi
    MAX_CHAT_HISTORY = 5  # Limit chat history to save memory
    AUDIO_TIMEOUT = 30  # Maximum recording time
    
    # Pi-specific optimizations
    USE_GPU = False  # Pi doesn't have dedicated GPU for these models
    LOW_MEMORY_MODE = True  # Enable memory optimizations
    
    # Wake word configuration
    WAKE_WORD = "hi windy"
    SLEEP_WORD = "bye windy"
    WAKE_WORD_ENERGY_THRESHOLD = 600  # Lower for Pi microphones
    CONVERSATION_ENERGY_THRESHOLD = 800  # Adjusted for Pi
    
    # Response length configuration (optimized for voice assistant)
    MAX_RESPONSE_WORDS = 25  # Slightly shorter for Pi performance (~15-20 seconds)
    MAX_RESPONSE_TOKENS = 50  # Lower token limit for Pi
    RESPONSE_TEMPERATURE = 0.6  # More consistent responses for Pi
