# voice_assistant/audio.py

import speech_recognition as sr
import pygame
import time
import logging
import pydub
from io import BytesIO
from pydub import AudioSegment
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@lru_cache(maxsize=None)
def get_recognizer():
    """
    Return a cached speech recognizer instance
    """
    return sr.Recognizer()

def record_audio(file_path, timeout=15, phrase_time_limit=10, retries=3, energy_threshold=1000, 
                 pause_threshold=1.5, phrase_threshold=0.1, dynamic_energy_threshold=True, 
                 calibration_duration=1, wake_word_mode=False, use_fallback=True):
    """
    Record audio from the microphone and save it as a WAV file.
    
    Args:
    file_path (str): The path to save the recorded audio file.
    timeout (int): Maximum time to wait for a phrase to start (in seconds).
    phrase_time_limit (int): Maximum time for the recorded phrase (in seconds).
    retries (int): Number of retry attempts if recording fails.
    energy_threshold (int): Minimum audio energy to consider for recording.
    pause_threshold (float): How much silence before ending recording (in seconds).
    phrase_threshold (float): Minimum length of phrase to be recorded (in seconds).
    dynamic_energy_threshold (bool): Automatically adjust energy threshold.
    calibration_duration (int): Duration for ambient noise calibration (in seconds).
    wake_word_mode (bool): If True, use optimized settings for wake word detection.
    """
    
    # Adjust settings for wake word mode
    if wake_word_mode:
        from voice_assistant.config import Config
        energy_threshold = getattr(Config, 'WAKE_WORD_ENERGY_THRESHOLD', 600)
        pause_threshold = getattr(Config, 'WAKE_WORD_PAUSE_THRESHOLD', 0.8)
        timeout = 10  # Reasonable timeout for wake word
        phrase_time_limit = 5  # Max time for wake word phrase
        logging.info("🎤 Recording in WAKE WORD mode...")
    else:
        # Conversation mode - more generous timeouts
        timeout = 15  # More time to start speaking
        phrase_time_limit = 10  # More time for longer responses
        energy_threshold = 800  # Slightly lower for conversation
        pause_threshold = 2.0  # Longer pause for end of sentence
        logging.info("🎤 Recording in CONVERSATION mode...")
        
    recognizer = get_recognizer()
    recognizer.energy_threshold = energy_threshold
    recognizer.pause_threshold = pause_threshold
    recognizer.phrase_threshold = phrase_threshold
    recognizer.dynamic_energy_threshold = dynamic_energy_threshold
    
    for attempt in range(retries):
        try:
            with sr.Microphone() as source:
                logging.info("Calibrating for ambient noise...")
                try:
                    recognizer.adjust_for_ambient_noise(source, duration=calibration_duration)
                    logging.info(f"Energy threshold after calibration: {recognizer.energy_threshold}")
                except OSError as audio_error:
                    logging.warning(f"Audio calibration failed: {audio_error}")
                    # Continue with default energy threshold
                    recognizer.energy_threshold = energy_threshold
                
                logging.info(f"🎙️ Recording started - Please speak now! (timeout: {timeout}s, phrase_limit: {phrase_time_limit}s)")
                
                # Listen for the first phrase and extract it into audio data
                start_time = time.time()
                audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                record_duration = time.time() - start_time
                
                logging.info(f"✅ Recording complete in {record_duration:.2f} seconds")

                # Save the recorded audio data as WAV file
                wav_data = audio_data.get_wav_data()
                
                try:
                    with open(file_path, 'wb') as audio_file:
                        audio_file.write(wav_data)
                    logging.info(f"Audio saved successfully to {file_path}")
                    return
                except Exception as save_error:
                    logging.error(f"Failed to save audio file: {save_error}")
                    raise
        except sr.WaitTimeoutError:
            if wake_word_mode:
                # For wake word mode, timeout is expected - just retry
                logging.debug(f"⏰ Wake word listening timed out, retrying... ({attempt + 1}/{retries})")
            else:
                # For conversation mode, timeout might indicate a problem
                logging.warning(f"⏰ Conversation listening timed out, retrying... ({attempt + 1}/{retries})")
                logging.info("💡 Try speaking louder or closer to the microphone")
        except OSError as audio_error:
            logging.error(f"🔧 Audio device error: {audio_error}")
            if "Invalid number of channels" in str(audio_error) or "ALSA" in str(audio_error):
                logging.info("🔄 Trying with different audio settings...")
                time.sleep(1)  # Brief wait before retry
        except Exception as e:
            logging.error(f"❌ Failed to record audio: {e}")
            if attempt == retries - 1:
                logging.error("🚨 All recording attempts failed!")
                raise
        
    logging.error("🚨 Speech Recognition recording failed after all retries")
    
    # Try alternative recording methods if fallback is enabled
    if use_fallback:
        logging.info("🔄 Trying alternative recording methods...")
        
        # Method 1: Direct arecord command
        if _record_with_arecord(file_path, phrase_time_limit):
            return
            
        # Method 2: sox recording (if available)
        if _record_with_sox(file_path, phrase_time_limit):
            return
            
        # Method 3: Manual recording prompt
        if _manual_recording_prompt(file_path):
            return
    
    logging.error("❌ All recording methods failed")
    raise Exception("All audio recording methods failed")

def _record_with_arecord(file_path, duration=10):
    """Fallback recording using arecord command directly"""
    try:
        import subprocess
        import os
        
        logging.info("🎤 Trying direct arecord recording...")
        logging.info(f"🎙️ Recording for {duration} seconds - Please speak now!")
        
        # Use arecord directly with specific parameters
        cmd = [
            "arecord",
            "-f", "cd",  # CD quality (16-bit, 44.1kHz, stereo)
            "-t", "wav",
            "-d", str(duration),
            file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration+5)
        
        if result.returncode == 0 and os.path.exists(file_path) and os.path.getsize(file_path) > 1000:
            logging.info("✅ arecord recording successful")
            return True
        else:
            logging.warning(f"⚠️ arecord failed: {result.stderr}")
            return False
            
    except Exception as e:
        logging.warning(f"⚠️ arecord recording failed: {e}")
        return False

def _record_with_sox(file_path, duration=10):
    """Fallback recording using sox (if available)"""
    try:
        import subprocess
        import os
        
        logging.info("🎤 Trying sox recording...")
        logging.info(f"🎙️ Recording for {duration} seconds - Please speak now!")
        
        # Use sox for recording
        cmd = [
            "sox", "-d", file_path,
            "trim", "0", str(duration),
            "rate", "16000",
            "channels", "1"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration+5)
        
        if result.returncode == 0 and os.path.exists(file_path) and os.path.getsize(file_path) > 1000:
            logging.info("✅ sox recording successful")
            return True
        else:
            logging.warning(f"⚠️ sox not available or failed: {result.stderr}")
            return False
            
    except Exception as e:
        logging.warning(f"⚠️ sox recording failed: {e}")
        return False

def _manual_recording_prompt(file_path):
    """Prompt user to manually record audio"""
    try:
        import os
        import time
        
        logging.info("🎤 Manual recording mode - Use another device to record")
        logging.info("📝 Instructions:")
        logging.info("   1. Use another device/app to record your voice")
        logging.info("   2. Save as WAV file and copy to this location:")
        logging.info(f"   3. File path: {os.path.abspath(file_path)}")
        logging.info("   4. Press Enter when file is ready (or Ctrl+C to skip)")
        
        # Wait for user to place the file
        input("⏳ Press Enter when audio file is ready...")
        
        if os.path.exists(file_path) and os.path.getsize(file_path) > 100:
            logging.info("✅ Manual audio file detected")
            return True
        else:
            logging.warning("⚠️ No valid audio file found")
            return False
            
    except KeyboardInterrupt:
        logging.info("⏭️ Manual recording skipped")
        return False
    except Exception as e:
        logging.warning(f"⚠️ Manual recording prompt failed: {e}")
        return False

def play_audio(file_path):
    """
    Play an audio file using pygame.
    
    Args:
    file_path (str): The path to the audio file to play.
    """
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
    except pygame.error as e:
        logging.error(f"Failed to play audio: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while playing audio: {e}")
    finally:
        pygame.mixer.quit()