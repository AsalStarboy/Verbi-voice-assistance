# voice_assistant/text_to_speech.py
import logging
import subprocess
import os

from voice_assistant.config import Config

# Optional imports - only if available
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logging.warning("PyAudio not available - install with: pip install pyaudio")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI not available - install with: pip install openai")

try:
    from deepgram import DeepgramClient, SpeakOptions
    DEEPGRAM_AVAILABLE = True
except ImportError:
    DEEPGRAM_AVAILABLE = False
    logging.warning("Deepgram not available - install with: pip install deepgram-sdk")

try:
    from elevenlabs.client import ElevenLabs
    import elevenlabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    logging.warning("ElevenLabs not available - install with: pip install elevenlabs")

try:
    from cartesia import Cartesia
    CARTESIA_AVAILABLE = True
except ImportError:
    CARTESIA_AVAILABLE = False
    logging.warning("Cartesia not available - install with: pip install cartesia")

def text_to_speech(model: str, api_key:str, text:str, output_file_path:str, local_model_path:str=None):
    """
    Convert text to speech using the specified model.
    
    Args:
    model (str): The model to use for TTS ('openai', 'deepgram', 'elevenlabs', 'local').
    api_key (str): The API key for the TTS service.
    text (str): The text to convert to speech.
    output_file_path (str): The path to save the generated speech audio file.
    local_model_path (str): The path to the local model (if applicable).
    """
    
    try:
        if model == 'openai':
            if not OPENAI_AVAILABLE:
                logging.error("OpenAI package not available. Falling back to Piper TTS.")
                return text_to_speech('piper', api_key, text, output_file_path, local_model_path)
            client = OpenAI(api_key=api_key)
            speech_response = client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=text
            )
            speech_response.stream_to_file(output_file_path)

        elif model == 'deepgram':
            if not DEEPGRAM_AVAILABLE:
                logging.error("Deepgram package not available. Falling back to Piper TTS.")
                return text_to_speech('piper', api_key, text, output_file_path, local_model_path)
            client = DeepgramClient(api_key=api_key)
            options = SpeakOptions(
                model="aura-arcas-en",
                encoding="linear16",
                container="wav"
            )
            SPEAK_OPTIONS = {"text": text}
            response = client.speak.v("1").save(output_file_path, SPEAK_OPTIONS, options)
        
        elif model == 'elevenlabs':
            if not ELEVENLABS_AVAILABLE:
                logging.error("ElevenLabs package not available. Falling back to Piper TTS.")
                return text_to_speech('piper', api_key, text, output_file_path, local_model_path)
            client = ElevenLabs(api_key=api_key)
            audio = client.generate(
                text=text, 
                voice="Paul J.", 
                output_format="mp3_22050_32", 
                model="eleven_turbo_v2"
            )
            elevenlabs.save(audio, output_file_path)
        
        elif model == "cartesia":
            if not CARTESIA_AVAILABLE or not PYAUDIO_AVAILABLE:
                logging.error("Cartesia or PyAudio not available. Falling back to Piper TTS.")
                return text_to_speech('piper', api_key, text, output_file_path, local_model_path)
            client = Cartesia(api_key=api_key)
            voice_id = "f114a467-c40a-4db8-964d-aaba89cd08fa"
            voice = client.voices.get(id=voice_id)
            model_id = "sonic-english"
            output_format = {
                "container": "raw",
                "encoding": "pcm_f32le",
                "sample_rate": 44100,
            }
            p = pyaudio.PyAudio()
            rate = 44100
            stream = None
            for output in client.tts.sse(
                model_id=model_id,
                transcript=text,
                voice_embedding=voice["embedding"],
                stream=True,
                output_format=output_format,
            ):
                buffer = output["audio"]
                if stream is None:
                    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=rate, output=True)
                stream.write(buffer)
            if stream:
                stream.stop_stream()
                stream.close()
            p.terminate()

        elif model == "piper":  # LOCAL TTS - RASPBERRY PI OPTIMIZED
            try:
                # For Raspberry Pi, try different installation paths
                piper_executable = Config.PIPER_EXECUTABLE
                
                # Check if piper is in PATH first
                try:
                    subprocess.run(["which", "piper"], check=True, capture_output=True)
                    piper_executable = "piper"
                except subprocess.CalledProcessError:
                    # Try common installation paths
                    possible_paths = [
                        "/usr/local/bin/piper",
                        "/home/pi/.local/bin/piper",
                        "piper"
                    ]
                    piper_executable = None
                    for path in possible_paths:
                        try:
                            subprocess.run([path, "--help"], check=True, capture_output=True)
                            piper_executable = path
                            break
                        except (subprocess.CalledProcessError, FileNotFoundError):
                            continue
                    
                    if not piper_executable:
                        # Use espeak as fallback
                        logging.warning("Piper not found, using espeak as fallback")
                        result = subprocess.run(
                            ["espeak", "-w", output_file_path, text],
                            capture_output=True,
                            check=True
                        )
                        logging.info(f"Espeak TTS output saved to {output_file_path}")
                        return
                
                # Try to use piper with default model if custom model doesn't exist
                model_path = Config.PIPER_MODEL_PATH
                if not os.path.exists(model_path):
                    logging.warning(f"Piper model not found at {model_path}, using default")
                    # Run without model path to use default
                    command = [piper_executable, "-f", output_file_path]
                else:
                    command = [piper_executable, "-m", model_path, "-f", output_file_path]
                
                result = subprocess.run(
                    command, 
                    input=text, 
                    text=True, 
                    capture_output=True, 
                    check=True
                )
                
                logging.info(f"Piper TTS output saved to {output_file_path}")
                
            except subprocess.CalledProcessError as e:
                logging.error(f"Piper TTS command failed: {e.stderr}")
                # Fallback to espeak
                try:
                    subprocess.run(
                        ["espeak", "-w", output_file_path, text],
                        capture_output=True,
                        check=True
                    )
                    logging.info(f"Espeak fallback TTS output saved to {output_file_path}")
                except subprocess.CalledProcessError as e2:
                    logging.error(f"Espeak fallback also failed: {e2}")
                    raise
            except Exception as e:
                logging.error(f"Piper TTS error: {e}")
                raise
        
        elif model == 'local':
            with open(output_file_path, "wb") as f:
                f.write(b"Local TTS audio data")
        
        else:
            raise ValueError("Unsupported TTS model")
        
    except Exception as e:
        logging.error(f"Failed to convert text to speech: {e}")
        raise