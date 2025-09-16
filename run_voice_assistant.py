# voice_assistant/main.py

import logging
import time
import re

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

from voice_assistant.audio import record_audio, play_audio
from voice_assistant.transcription import transcribe_audio
from voice_assistant.response_generation import generate_response
from voice_assistant.text_to_speech import text_to_speech
from voice_assistant.utils import delete_file
from voice_assistant.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize colorama
init(autoreset=True)

# Wake word constants
WAKE_WORD = "hi windy"
SLEEP_WORD = "bye windy"

def detect_wake_word(text):
    """
    Detect if the wake word is present in the transcribed text.
    """
    if not text:
        return False
    
    text_lower = text.lower().strip()
    
    # Check for exact match or close variations - more flexible patterns
    wake_patterns = [
        r'\bhi\s+windy\b',
        r'\bhey\s+windy\b', 
        r'\bhello\s+windy\b',
        r'\bhi\s+wendy\b',  # Common misheard variation
        r'\bhey\s+wendy\b',
        r'\bhello\s+wendy\b',
        r'\bwindy\b',  # Just the name
        r'\bwendy\b'   # Just the misheard name
    ]
    
    for pattern in wake_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False

def detect_sleep_word(text):
    """
    Detect if the sleep word is present in the transcribed text.
    """
    if not text:
        return False
    
    text_lower = text.lower().strip()
    
    # Check for exact match or close variations - more flexible patterns
    sleep_patterns = [
        r'\bbye\s+windy\b',
        r'\bgoodbye\s+windy\b',
        r'\bbye\s+wendy\b',  # Common misheard variation
        r'\bgoodbye\s+wendy\b',
        r'\bsee\s+you\s+later\s+windy\b',
        r'\bsleep\s+windy\b',
        r'\bstop\s+windy\b',
        r'\bturn\s+off\b',
        r'\bshut\s+down\b',
        r'\bgo\s+to\s+sleep\b',
        r'\bstop\s+listening\b'
    ]
    
    for pattern in sleep_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False

def wait_for_wake_word():
    """
    Sleep mode - only listen for wake word with minimal processing.
    """
    logging.info(Fore.YELLOW + "💤 Voice Assistant sleeping - Say 'Hi Windy' to wake up..." + Fore.RESET)
    
    while True:
        try:
            # Record audio with wake word optimized settings
            record_audio(Config.INPUT_AUDIO, wake_word_mode=True)
            
            # Transcribe only for wake word detection (faster processing)
            wake_text = transcribe_audio(Config.TRANSCRIPTION_MODEL, None, Config.INPUT_AUDIO, Config.LOCAL_MODEL_PATH)
            
            if wake_text:
                logging.info(Fore.CYAN + f"👂 Heard: {wake_text}" + Fore.RESET)
                
                if detect_wake_word(wake_text):
                    logging.info(Fore.GREEN + "🎉 Wake word detected! Activating voice assistant..." + Fore.RESET)
                    
                    # Play fast wake up greeting
                    greeting = "Hello! How can I help?"
                    text_to_speech(Config.TTS_MODEL, None, greeting, "wake_greeting.wav", Config.LOCAL_MODEL_PATH)
                    play_audio("wake_greeting.wav")
                    delete_file("wake_greeting.wav")
                    
                    return True  # Wake up
            
            # Clean up wake word audio file
            delete_file(Config.INPUT_AUDIO)
            
        except KeyboardInterrupt:
            logging.info(Fore.RED + "👋 Voice Assistant shutting down..." + Fore.RESET)
            return False
        except Exception as e:
            logging.error(f"Error in wake word detection: {e}")
            time.sleep(1)  # Brief pause before retrying


def main():
    """
    Main function to run the voice assistant with wake word system.
    """
    logging.info(Fore.BLUE + "🤖 Windy Voice Assistant Starting..." + Fore.RESET)
    logging.info(Fore.YELLOW + f"💡 Wake word: '{WAKE_WORD}'" + Fore.RESET)
    logging.info(Fore.YELLOW + f"💡 Sleep word: '{SLEEP_WORD}'" + Fore.RESET)
    
    while True:
        try:
            # Start in sleep mode - wait for wake word
            should_continue = wait_for_wake_word()
            if not should_continue:
                break
            
            # Active mode - full conversation
            active_conversation()
            
        except KeyboardInterrupt:
            logging.info(Fore.RED + "👋 Voice Assistant shutting down..." + Fore.RESET)
            break
        except Exception as e:
            logging.error(Fore.RED + f"An error occurred in main loop: {e}" + Fore.RESET)
            time.sleep(2)

def active_conversation():
    """
    Active conversation mode - full voice assistant functionality.
    """
    chat_history = [
        {"role": "system", "content": """You are Windy, a friendly voice assistant. 
        Keep responses natural, conversational, and brief. 
        No special formatting, symbols, or instructions.
        Just be helpful and speak naturally."""}
    ]
    
    logging.info(Fore.GREEN + "🎤 Voice Assistant active - Start talking! Say 'Bye Windy' to sleep." + Fore.RESET)
    
    while True:
        try:
            # Record audio from the microphone with conversation settings
            record_audio(Config.INPUT_AUDIO, wake_word_mode=False)

            # Transcribe the audio file
            user_input = transcribe_audio(Config.TRANSCRIPTION_MODEL, None, Config.INPUT_AUDIO, Config.LOCAL_MODEL_PATH)

            # Check if the transcription is empty and restart the recording if it is
            if not user_input:
                logging.info("No transcription was returned. Starting recording again.")
                continue
                
            logging.info(Fore.GREEN + "You said: " + user_input + Fore.RESET)

            # Check for sleep word to go back to wake word mode
            if detect_sleep_word(user_input):
                logging.info(Fore.YELLOW + "😴 Sleep word detected! Going to sleep mode..." + Fore.RESET)
                
                # Say fast goodbye
                goodbye_message = "Goodbye!"
                text_to_speech(Config.TTS_MODEL, None, goodbye_message, "goodbye.wav", Config.LOCAL_MODEL_PATH)
                play_audio("goodbye.wav")
                delete_file("goodbye.wav")
                
                # Clean up and return to wake word mode
                delete_file(Config.INPUT_AUDIO)
                return

            # Check if the user wants to exit the program completely
            if any(word in user_input.lower() for word in ["shutdown", "turn off", "exit program", "quit"]):
                logging.info(Fore.RED + "👋 Shutdown command received. Exiting..." + Fore.RESET)
                break

            # Append the user's input to the chat history
            chat_history.append({"role": "user", "content": user_input})
            
            # Generate a response
            response_text = generate_response(Config.RESPONSE_MODEL, None, chat_history, Config.LOCAL_MODEL_PATH)
            logging.info(Fore.CYAN + "Windy: " + response_text + Fore.RESET)

            # Append the assistant's response to the chat history
            chat_history.append({"role": "assistant", "content": response_text})

            # Determine the output file format based on the TTS model
            if Config.TTS_MODEL == 'openai' or Config.TTS_MODEL == 'elevenlabs' or Config.TTS_MODEL == 'melotts' or Config.TTS_MODEL == 'cartesia':
                output_file = 'output.mp3'
            else:
                output_file = 'output.wav'

            # Convert the response text to speech
            text_to_speech(Config.TTS_MODEL, None, response_text, output_file, Config.LOCAL_MODEL_PATH)

            # Play the generated speech audio
            if Config.TTS_MODEL != "cartesia":
                play_audio(output_file)
            
            # Clean up audio files for this conversation turn
            delete_file(Config.INPUT_AUDIO)
            delete_file(output_file)

        except Exception as e:
            logging.error(Fore.RED + f"An error occurred in conversation: {e}" + Fore.RESET)
            # Clean up files on error
            delete_file(Config.INPUT_AUDIO)
            if 'output_file' in locals():
                delete_file(output_file)
            time.sleep(1)

if __name__ == "__main__":
    main()
