#!/usr/bin/env python3
"""
Ultimate Voice Assistant Test - Multiple Input Methods
Tests STT → LLM → TTS pipeline with audio and text fallbacks
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

def get_user_input_with_fallback():
    """Get user input using audio recording with text fallback"""
    
    try:
        from voice_assistant.audio import record_audio
        from voice_assistant.transcription import transcribe_audio
        from voice_assistant.config import Config
        
        # Try audio recording first
        try:
            print(f"{Fore.GREEN}🎤 Method 1: Audio Recording{Fore.RESET}")
            print("🎙️ Please speak your question now!")
            
            record_audio(Config.INPUT_AUDIO, wake_word_mode=False, use_fallback=True)
            
            # Check if file was created and has content
            if os.path.exists(Config.INPUT_AUDIO) and os.path.getsize(Config.INPUT_AUDIO) > 1000:
                print(f"{Fore.GREEN}✅ Audio recorded successfully{Fore.RESET}")
                
                # Try transcription
                print(f"{Fore.GREEN}🔄 Transcribing audio...{Fore.RESET}")
                transcription = transcribe_audio(
                    Config.TRANSCRIPTION_MODEL, 
                    None, 
                    Config.INPUT_AUDIO, 
                    Config.LOCAL_MODEL_PATH
                )
                
                if transcription and transcription.strip():
                    print(f"{Fore.CYAN}👤 You said: \"{transcription}\"{Fore.RESET}")
                    return transcription.strip()
                else:
                    print(f"{Fore.YELLOW}⚠️ Transcription failed or empty{Fore.RESET}")
            else:
                print(f"{Fore.YELLOW}⚠️ Audio recording failed or file too small{Fore.RESET}")
                
        except Exception as audio_error:
            print(f"{Fore.YELLOW}⚠️ Audio method failed: {audio_error}{Fore.RESET}")
        
        # Fallback to text input
        print(f"{Fore.BLUE}💬 Method 2: Text Input Fallback{Fore.RESET}")
        print("Since audio didn't work, please type your question:")
        
        user_text = input("👤 Your question: ").strip()
        
        if user_text:
            print(f"{Fore.CYAN}👤 You typed: \"{user_text}\"{Fore.RESET}")
            return user_text
        else:
            print(f"{Fore.YELLOW}⚠️ Empty input{Fore.RESET}")
            return None
            
    except Exception as e:
        print(f"{Fore.RED}❌ All input methods failed: {e}{Fore.RESET}")
        return None

def test_complete_pipeline():
    """Test the complete pipeline with multiple input methods"""
    
    try:
        # Import voice assistant modules
        from voice_assistant.response_generation import generate_response
        from voice_assistant.text_to_speech import text_to_speech
        from voice_assistant.audio import play_audio
        from voice_assistant.utils import delete_file
        from voice_assistant.config import Config
        
        print(f"{Fore.BLUE}🤖 Ultimate Voice Assistant Test{Fore.RESET}")
        print(f"{Fore.BLUE}==================================={Fore.RESET}")
        print(f"{Fore.YELLOW}Tests complete STT→LLM→TTS pipeline with fallbacks{Fore.RESET}")
        print()
        
        # Initialize conversation history
        chat_history = [
            {"role": "system", "content": "You are Windy, a helpful voice assistant. Keep responses short and conversational (under 20 words)."}
        ]
        
        conversation_count = 0
        max_conversations = 5  # More tests
        
        while conversation_count < max_conversations:
            conversation_count += 1
            print(f"{Fore.CYAN}--- Conversation {conversation_count}/{max_conversations} ---{Fore.RESET}")
            
            try:
                # Step 1: Get user input (audio or text)
                print(f"{Fore.GREEN}📝 Step 1: Getting user input...{Fore.RESET}")
                user_input = get_user_input_with_fallback()
                
                if not user_input:
                    print(f"{Fore.YELLOW}⚠️ No input received - trying again...{Fore.RESET}")
                    continue
                
                # Check for exit commands
                if any(word in user_input.lower() for word in ["exit", "quit", "stop", "bye", "end"]):
                    print(f"{Fore.RED}👋 Exit command detected. Stopping test.{Fore.RESET}")
                    break
                
                # Step 2: Generate response
                print(f"{Fore.GREEN}🤖 Step 2: Generating AI response...{Fore.RESET}")
                chat_history.append({"role": "user", "content": user_input})
                
                response_text = generate_response(
                    Config.RESPONSE_MODEL, 
                    None, 
                    chat_history, 
                    Config.LOCAL_MODEL_PATH
                )
                
                if not response_text or not response_text.strip():
                    response_text = "I'm sorry, I couldn't generate a response right now."
                
                # Limit response length for better speech
                if len(response_text) > 100:
                    response_text = response_text[:97] + "..."
                
                print(f"{Fore.BLUE}🤖 Windy: \"{response_text}\"{Fore.RESET}")
                chat_history.append({"role": "assistant", "content": response_text})
                
                # Step 3: Convert to speech
                print(f"{Fore.GREEN}🗣️ Step 3: Converting to speech...{Fore.RESET}")
                
                # Determine output file format
                if Config.TTS_MODEL in ['openai', 'elevenlabs', 'melotts', 'cartesia']:
                    output_file = 'output.mp3'
                else:
                    output_file = 'output.wav'
                
                try:
                    text_to_speech(
                        Config.TTS_MODEL, 
                        None, 
                        response_text, 
                        output_file, 
                        Config.LOCAL_MODEL_PATH
                    )
                    
                    # Step 4: Play response
                    print(f"{Fore.GREEN}🔊 Step 4: Playing response...{Fore.RESET}")
                    if Config.TTS_MODEL != "cartesia" and os.path.exists(output_file):
                        play_audio(output_file)
                        print(f"{Fore.GREEN}✅ Audio playback complete{Fore.RESET}")
                    else:
                        print(f"{Fore.YELLOW}⚠️ Audio file not found or cartesia TTS used{Fore.RESET}")
                        
                except Exception as tts_error:
                    print(f"{Fore.YELLOW}⚠️ TTS/Audio playback failed: {tts_error}{Fore.RESET}")
                    print(f"{Fore.BLUE}📝 Response (text only): {response_text}{Fore.RESET}")
                
                print(f"{Fore.GREEN}✅ Conversation {conversation_count} complete!{Fore.RESET}")
                print()
                
                # Clean up files
                for file in [Config.INPUT_AUDIO, output_file]:
                    if os.path.exists(file):
                        delete_file(file)
                        
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
        
        print(f"{Fore.BLUE}🏁 Ultimate voice assistant test complete!{Fore.RESET}")
        print(f"{Fore.YELLOW}Total conversations tested: {conversation_count}{Fore.RESET}")
        
    except ImportError as e:
        print(f"{Fore.RED}❌ Import error: {e}{Fore.RESET}")
        print(f"{Fore.YELLOW}Make sure you're in the virtual environment and dependencies are installed{Fore.RESET}")
        return False
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}{Fore.RESET}")
        logging.exception("Detailed error:")
        return False
    
    return True

if __name__ == "__main__":
    print(f"{Fore.YELLOW}🚀 Starting Ultimate Voice Assistant Test...{Fore.RESET}")
    print(f"{Fore.YELLOW}This will try audio first, then fall back to text input{Fore.RESET}")
    print(f"{Fore.YELLOW}Press Ctrl+C to stop at any time{Fore.RESET}")
    print()
    
    success = test_complete_pipeline()
    
    if success:
        print(f"{Fore.GREEN}✅ Test completed successfully!{Fore.RESET}")
    else:
        print(f"{Fore.RED}❌ Test failed - check the logs above{Fore.RESET}")
        sys.exit(1)