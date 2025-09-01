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

def record_audio(file_path, timeout=10, phrase_time_limit=None, retries=3, energy_threshold=1000, 
                 pause_threshold=1.5, phrase_threshold=0.1, dynamic_energy_threshold=True, 
                 calibration_duration=2, wake_word_mode=False):
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
        energy_threshold = getattr(Config, 'WAKE_WORD_ENERGY_THRESHOLD', 800)
        pause_threshold = getattr(Config, 'WAKE_WORD_PAUSE_THRESHOLD', 1.0)
        timeout = getattr(Config, 'WAKE_WORD_TIMEOUT', 5)
        phrase_time_limit = 3  # Shorter phrase limit for wake words
        
    recognizer = get_recognizer()
    recognizer.energy_threshold = energy_threshold
    recognizer.pause_threshold = pause_threshold
    recognizer.phrase_threshold = phrase_threshold
    recognizer.dynamic_energy_threshold = dynamic_energy_threshold
    
    for attempt in range(retries):
        try:
            with sr.Microphone() as source:
                logging.info("Calibrating for ambient noise...")
                recognizer.adjust_for_ambient_noise(source, duration=calibration_duration)
                logging.info(f"Energy threshold after calibration: {recognizer.energy_threshold}")
                logging.info("Recording started - Please speak now!")
                # Listen for the first phrase and extract it into audio data
                audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                logging.info("Recording complete")

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
            logging.warning(f"Listening timed out, retrying... ({attempt + 1}/{retries})")
        except Exception as e:
            logging.error(f"Failed to record audio: {e}")
            if attempt == retries -1:
                raise
        
    logging.error("Recording failed after all retries")

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