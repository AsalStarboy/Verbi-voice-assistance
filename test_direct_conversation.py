#!/usr/bin/env python3
"""
Direct Voice Assistant Test - Bypasses wake word detection
Tests STT → LLM → TTS pipeline directly for debugging
"""

import logging
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Optional colorama import
try:
    from colorama import Fore, init
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    class Fore:
        RESET = RED = GREEN = YELLOW = BLUE = CYAN = ""

def test_conversation_pipeline():
    """Test the complete conversation pipeline without wake word detection"""
    
    try:
        # Import voice assistant modules
        from voice_assistant.audio import record_audio, play_audio
        from voice_assistant.transcription import transcribe_audio
        from voice_assistant.response_generation import generate_response
        from voice_assistant.text_to_speech import text_to_speech
        from voice_assistant.utils import delete_file
        from voice_assistant.config import Config
        
        print(f"{Fore.BLUE}🤖 Direct Voice Assistant Test{Fore.RESET}")
        print(f"{Fore.BLUE}================================{Fore.RESET}")
        print(f"{Fore.YELLOW}This bypasses wake word detection and tests STT→LLM→TTS directly{Fore.RESET}")
        print()
        
        # Initialize conversation history
        chat_history = [
            {"role": "system", "content": "You are Windy, a helpful voice assistant. Keep responses short and conversational."}
        ]
        
        conversation_count = 0
        max_conversations = 3  # Limit for testing
        
        while conversation_count < max_conversations:
            conversation_count += 1
            print(f"{Fore.CYAN}--- Conversation {conversation_count}/{max_conversations} ---{Fore.RESET}")
            
            try:
                # Step 1: Record audio
                print(f"{Fore.GREEN}🎤 Step 1: Recording audio...{Fore.RESET}")
                print("🎙️ Please speak your question now!")
                
                record_audio(Config.INPUT_AUDIO, wake_word_mode=False)
                print(f"{Fore.GREEN}✅ Recording complete{Fore.RESET}")
                
                # Step 2: Transcribe audio
                print(f"{Fore.GREEN}🔄 Step 2: Transcribing audio...{Fore.RESET}")
                user_input = transcribe_audio(
                    Config.TRANSCRIPTION_MODEL, 
                    None, 
                    Config.INPUT_AUDIO, 
                    Config.LOCAL_MODEL_PATH
                )
                
                if not user_input or not user_input.strip():
                    print(f"{Fore.YELLOW}⚠️ No transcription result - trying again...{Fore.RESET}")
                    continue
                    
                print(f"{Fore.CYAN}👤 You said: \"{user_input}\"{Fore.RESET}")
                
                # Check for exit commands
                if any(word in user_input.lower() for word in ["exit", "quit", "stop", "bye"]):
                    print(f"{Fore.RED}👋 Exit command detected. Stopping test.{Fore.RESET}")
                    break
                
                # Step 3: Generate response
                print(f"{Fore.GREEN}🤖 Step 3: Generating response...{Fore.RESET}")
                chat_history.append({"role": "user", "content": user_input})
                
                response_text = generate_response(
                    Config.RESPONSE_MODEL, 
                    None, 
                    chat_history, 
                    Config.LOCAL_MODEL_PATH
                )
                
                if not response_text:
                    response_text = "I'm sorry, I couldn't generate a response. Please try again."
                
                print(f"{Fore.BLUE}🤖 Windy: \"{response_text}\"{Fore.RESET}")
                chat_history.append({"role": "assistant", "content": response_text})
                
                # Step 4: Convert to speech
                print(f"{Fore.GREEN}🗣️ Step 4: Converting to speech...{Fore.RESET}")
                
                # Determine output file format
                if Config.TTS_MODEL in ['openai', 'elevenlabs', 'melotts', 'cartesia']:
                    output_file = 'output.mp3'
                else:
                    output_file = 'output.wav'
                
                text_to_speech(
                    Config.TTS_MODEL, 
                    None, 
                    response_text, 
                    output_file, 
                    Config.LOCAL_MODEL_PATH
                )
                
                # Step 5: Play response
                print(f"{Fore.GREEN}🔊 Step 5: Playing response...{Fore.RESET}")
                if Config.TTS_MODEL != "cartesia":
                    play_audio(output_file)
                
                print(f"{Fore.GREEN}✅ Conversation {conversation_count} complete!{Fore.RESET}")
                print()
                
                # Clean up files
                delete_file(Config.INPUT_AUDIO)
                if os.path.exists(output_file):
                    delete_file(output_file)
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}⏸️ Test interrupted by user{Fore.RESET}")
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Error in conversation {conversation_count}: {e}{Fore.RESET}")
                logging.exception("Detailed error:")
                
                # Clean up on error
                for file in [Config.INPUT_AUDIO, 'output.wav', 'output.mp3']:
                    if os.path.exists(file):
                        delete_file(file)
                continue
        
        print(f"{Fore.BLUE}🏁 Direct voice assistant test complete!{Fore.RESET}")
        print(f"{Fore.YELLOW}Total conversations tested: {conversation_count}{Fore.RESET}")
        
    except ImportError as e:
        print(f"{Fore.RED}❌ Import error: {e}{Fore.RESET}")
        print(f"{Fore.YELLOW}Make sure you're in the virtual environment and all dependencies are installed{Fore.RESET}")
        return False
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Fore.RESET}")
        logging.exception("Detailed error:")
        return False
    
    return True

if __name__ == "__main__":
    print(f"{Fore.YELLOW}🚀 Starting Direct Voice Assistant Test...{Fore.RESET}")
    print(f"{Fore.YELLOW}Press Ctrl+C to stop at any time{Fore.RESET}")
    print()
    
    success = test_conversation_pipeline()
    
    if success:
        print(f"{Fore.GREEN}✅ Test completed successfully!{Fore.RESET}")
    else:
        print(f"{Fore.RED}❌ Test failed - check the logs above{Fore.RESET}")
        sys.exit(1)