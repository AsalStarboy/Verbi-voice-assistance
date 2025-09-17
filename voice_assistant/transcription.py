# voice_assistant/transcription.py

import json
import logging
import requests
import time

# Optional colorama import for colored output
try:
    from colorama import Fore, init
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Define dummy Fore class if colorama is not available
    class Fore:
        RESET = ""
        RED = ""
        GREEN = ""
        YELLOW = ""
        BLUE = ""
        CYAN = ""
    def init():
        pass

# Optional imports - only if available
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI not available - install with: pip install openai")

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logging.warning("Groq not available - install with: pip install groq")

try:
    from deepgram import DeepgramClient, PrerecordedOptions, FileSource
    DEEPGRAM_AVAILABLE = True
except ImportError:
    DEEPGRAM_AVAILABLE = False
    logging.warning("Deepgram not available - install with: pip install deepgram-sdk")

try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False
    logging.warning("faster-whisper not available. Install with: pip install faster-whisper")

# FastWhisperAPI Docker support removed - use faster-whisper instead

def transcribe_audio(model, api_key, audio_file_path, local_model_path=None):
    """
    Transcribe an audio file using the specified model.
    
    Args:
        model (str): The model to use for transcription ('openai', 'groq', 'deepgram', 'faster-whisper', 'local').
        api_key (str): The API key for the transcription service.
        audio_file_path (str): The path to the audio file to transcribe.
        local_model_path (str): The path to the local model (if applicable).

    Returns:
        str: The transcribed text.
    """
    try:
        if model == 'openai':
            if not OPENAI_AVAILABLE:
                logging.error("OpenAI package not available. Falling back to faster-whisper.")
                return _transcribe_with_faster_whisper(audio_file_path, local_model_path)
            return _transcribe_with_openai(api_key, audio_file_path)
        elif model == 'groq':
            if not GROQ_AVAILABLE:
                logging.error("Groq package not available. Falling back to faster-whisper.")
                return _transcribe_with_faster_whisper(audio_file_path, local_model_path)
            return _transcribe_with_groq(api_key, audio_file_path)
        elif model == 'deepgram':
            if not DEEPGRAM_AVAILABLE:
                logging.error("Deepgram package not available. Falling back to faster-whisper.")
                return _transcribe_with_faster_whisper(audio_file_path, local_model_path)
            return _transcribe_with_deepgram(api_key, audio_file_path)
        # FastWhisperAPI Docker support removed - use faster-whisper instead
        elif model == 'faster-whisper':
            return _transcribe_with_faster_whisper(audio_file_path, local_model_path)
        elif model == 'local':
            # Placeholder for local STT model transcription
            return "Transcribed text from local model"
        else:
            raise ValueError("Unsupported transcription model")
    except Exception as e:
        logging.error(f"{Fore.RED}Failed to transcribe audio: {e}{Fore.RESET}")
        logging.info("🔄 Attempting emergency fallback transcription...")
        
        # Emergency fallback - try speech_recognition directly
        try:
            return _transcribe_with_speech_recognition_fallback(audio_file_path)
        except Exception as fallback_error:
            logging.error(f"❌ All transcription methods failed: {fallback_error}")
            return ""  # Return empty string instead of raising exception

def _transcribe_with_openai(api_key, audio_file_path):
    if not OPENAI_AVAILABLE:
        raise ValueError("OpenAI package not installed. Use: pip install openai")
    client = OpenAI(api_key=api_key)
    with open(audio_file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language='en'
        )
    return transcription.text


def _transcribe_with_groq(api_key, audio_file_path):
    if not GROQ_AVAILABLE:
        raise ValueError("Groq package not installed. Use: pip install groq")
    client = Groq(api_key=api_key)
    with open(audio_file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=audio_file,
            language='en'
        )
    return transcription.text


def _transcribe_with_deepgram(api_key, audio_file_path):
    if not DEEPGRAM_AVAILABLE:
        raise ValueError("Deepgram package not installed. Use: pip install deepgram-sdk")
    deepgram = DeepgramClient(api_key)
    try:
        with open(audio_file_path, "rb") as file:
            buffer_data = file.read()

        payload = {"buffer": buffer_data}
        options = PrerecordedOptions(model="nova-2", smart_format=True)
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
        data = json.loads(response.to_json())

        transcript = data['results']['channels'][0]['alternatives'][0]['transcript']
        return transcript
    except Exception as e:
        logging.error(f"{Fore.RED}Deepgram transcription error: {e}{Fore.RESET}")
        raise


# FastWhisperAPI Docker function removed - use faster-whisper instead


def _transcribe_with_faster_whisper(audio_file_path, local_model_path=None):
    """
    Transcribe audio using faster-whisper locally with fallbacks.
    
    Args:
        audio_file_path (str): Path to the audio file
        local_model_path (str): Not used, kept for compatibility
    
    Returns:
        str: Transcribed text
    """
    if not FASTER_WHISPER_AVAILABLE:
        return _transcribe_with_speech_recognition_fallback(audio_file_path)
    
    try:
        import os
        from voice_assistant.config import Config
        
        # Check if audio file exists and has content
        if not os.path.exists(audio_file_path):
            logging.error(f"Audio file not found: {audio_file_path}")
            return ""
            
        if os.path.getsize(audio_file_path) == 0:
            logging.error(f"Audio file is empty: {audio_file_path}")
            return ""
        
        logging.info(f"🔄 Loading faster-whisper model: {Config.FASTER_WHISPER_MODEL_SIZE}")
        
        # Initialize the model using config settings
        model = WhisperModel(
            Config.FASTER_WHISPER_MODEL_SIZE, 
            device=Config.FASTER_WHISPER_DEVICE, 
            compute_type=Config.FASTER_WHISPER_COMPUTE_TYPE,
            cpu_threads=getattr(Config, 'FASTER_WHISPER_CPU_THREADS', 2),
            num_workers=getattr(Config, 'FASTER_WHISPER_NUM_WORKERS', 1)
        )
        
        logging.info(f"🎙️ Transcribing audio file: {audio_file_path}")
        
        # Transcribe the audio with optimized settings for Raspberry Pi
        segments, info = model.transcribe(
            audio_file_path, 
            beam_size=1,  # Reduced beam size for speed
            language="en",
            condition_on_previous_text=False,  # Disable for speed
            temperature=0.0,  # Deterministic output
            compression_ratio_threshold=2.4,
            no_speech_threshold=0.6
        )
        
        # Combine all segments into a single text
        transcribed_text = ""
        segment_count = 0
        for segment in segments:
            transcribed_text += segment.text + " "
            segment_count += 1
        
        if segment_count == 0:
            logging.warning("No segments transcribed - audio may be silent or too short")
            return _transcribe_with_speech_recognition_fallback(audio_file_path)
        
        logging.info(f"✅ Transcription complete: {segment_count} segments")
        logging.info(f"🌍 Detected language: {info.language} (probability: {info.language_probability:.2f})")
        
        result = transcribed_text.strip()
        if not result:
            logging.warning("Empty transcription result, trying fallback...")
            return _transcribe_with_speech_recognition_fallback(audio_file_path)
            
        return result
        
    except Exception as e:
        logging.error(f"❌ faster-whisper transcription error: {e}")
        logging.info("🔄 Trying speech_recognition fallback...")
        return _transcribe_with_speech_recognition_fallback(audio_file_path)

def _transcribe_with_speech_recognition_fallback(audio_file_path):
    """
    Fallback transcription using speech_recognition library.
    """
    try:
        import speech_recognition as sr
        
        r = sr.Recognizer()
        with sr.AudioFile(audio_file_path) as source:
            audio = r.record(source)
            
        # Try multiple engines in order of preference
        engines = [
            ("Google", lambda: r.recognize_google(audio)),
            ("Sphinx", lambda: r.recognize_sphinx(audio) if hasattr(r, 'recognize_sphinx') else None)
        ]
        
        for engine_name, recognize_func in engines:
            try:
                logging.info(f"🔄 Trying {engine_name} speech recognition...")
                result = recognize_func()
                if result:
                    logging.info(f"✅ {engine_name} transcription successful")
                    return result
            except Exception as e:
                logging.warning(f"⚠️ {engine_name} recognition failed: {e}")
                continue
        
        logging.error("All speech recognition engines failed")
        return ""
        
    except Exception as e:
        logging.error(f"❌ Speech recognition fallback failed: {e}")
        return ""