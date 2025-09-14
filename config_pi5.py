# Raspberry Pi 5 Voice Assistant Configuration
# Optimized for Pi 5's better performance capabilities

import os

class Config:
    # Audio file settings
    INPUT_AUDIO = "input.wav"
    
    # Model configurations - all local for Pi 5
    TRANSCRIPTION_MODEL = "faster-whisper"
    RESPONSE_MODEL = "ollama"
    TTS_MODEL = "piper"
    
    # Local model paths
    LOCAL_MODEL_PATH = os.path.expanduser("~/voice_assistant/models")
    
    # Ollama settings
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_LLM = "phi3.5:3.8b-mini-instruct-q3_K_M"
    
    # FastWhisper settings (optimized for Pi 5's better CPU)
    FASTER_WHISPER_MODEL_SIZE = "base"  # Pi 5 can handle base model well
    FASTER_WHISPER_DEVICE = "cpu"
    FASTER_WHISPER_COMPUTE_TYPE = "int8_float16"  # Better precision-performance balance
    FASTER_WHISPER_CPU_THREADS = 4  # Pi 5 has 4 cores
    FASTER_WHISPER_NUM_WORKERS = 2  # Parallel processing for Pi 5
    
    # Wake Word Configuration
    WAKE_WORD = "hi windy"
    SLEEP_WORD = "bye windy"
    WAKE_WORD_TIMEOUT = 5  # Seconds to listen for wake word
    CONVERSATION_TIMEOUT = 30  # Seconds to wait for user input
    
    # Audio settings for wake word detection (Pi 5 optimized)
    WAKE_WORD_ENERGY_THRESHOLD = 800  # Better audio processing on Pi 5
    WAKE_WORD_PAUSE_THRESHOLD = 0.8   # More responsive wake word detection
    
    # Piper TTS settings
    PIPER_EXECUTABLE = os.path.expanduser("~/voice_assistant/models/piper/piper/piper")
    PIPER_MODEL_PATH = os.path.expanduser("~/voice_assistant/models/piper/en_US-lessac-medium.onnx")
    
    # Audio settings optimized for Pi 5
    SAMPLE_RATE = 16000  # Standard rate for speech
    CHANNELS = 1  # Mono is sufficient
    CHUNK_SIZE = 2048  # Larger chunks for Pi 5's better processing
    
    # Voice detection settings (tuned for Pi 5)
    ENERGY_THRESHOLD = 1000  # Better audio quality threshold
    PAUSE_THRESHOLD = 1.2  # Faster response
    PHRASE_THRESHOLD = 0.3  # Standard phrase length
    
    # Performance settings for Pi 5
    MAX_CHAT_HISTORY = 10  # Pi 5 has more RAM (8GB)
    AUDIO_TIMEOUT = 30  # Standard timeout
    
    # Pi 5-specific optimizations
    USE_GPU = False  # CPU-only optimizations
    LOW_MEMORY_MODE = False  # Pi 5 has sufficient RAM
    BUFFER_SIZE = 4096  # Larger buffer for better performance
    
    # System settings
    LOG_FILE = "/var/log/voice-assistant.log"
    PID_FILE = "/tmp/voice-assistant.pid"
    
    # Resource limits
    CPU_QUOTA = 80  # Percentage of CPU to use
    MEMORY_LIMIT = "3G"  # Memory limit in GB
    
    # Advanced audio settings
    NOISE_REDUCTION = True  # Enable noise reduction
    AGC_LEVEL = 0.8  # Automatic Gain Control level
    
    # Model optimization flags
    ENABLE_CPU_OFFLOAD = True  # Better memory management
    ENABLE_ATTENTION_SLICING = True  # More efficient processing
    QUANTIZE_MODEL = True  # Use quantization where possible
