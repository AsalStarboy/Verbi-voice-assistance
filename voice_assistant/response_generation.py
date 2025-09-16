# voice_assistant/response_generation.py

import logging
import re

# Only import what we need for Ollama
import ollama

from voice_assistant.config import Config

# Optional imports for external APIs - only if available
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


def generate_response(model:str, api_key:str, chat_history:list, local_model_path:str=None):
    """
    Generate a response using the specified model.
    
    Args:
    model (str): The model to use for response generation ('openai', 'groq', 'local').
    api_key (str): The API key for the response generation service.
    chat_history (list): The chat history as a list of messages.
    local_model_path (str): The path to the local model (if applicable).

    Returns:
    str: The generated response text.
    """
    try:
        if model == 'openai':
            if not OPENAI_AVAILABLE:
                logging.error("OpenAI package not available. Falling back to Ollama.")
                response = _generate_ollama_response(chat_history)
            else:
                response = _generate_openai_response(api_key, chat_history)
        elif model == 'groq':
            if not GROQ_AVAILABLE:
                logging.error("Groq package not available. Falling back to Ollama.")
                response = _generate_ollama_response(chat_history)
            else:
                response = _generate_groq_response(api_key, chat_history)
        elif model == 'ollama':
            response = _generate_ollama_response(chat_history)
        elif model == 'local':
            # Placeholder for local LLM response generation
            response = "Generated response from local model"
        else:
            raise ValueError("Unsupported response generation model")
        
        # Clean the response before returning
        return _clean_response(response)
        
    except Exception as e:
        logging.error(f"Failed to generate response: {e}")
        return "I'm having trouble processing that right now."

def _generate_openai_response(api_key, chat_history):
    if not OPENAI_AVAILABLE:
        raise ValueError("OpenAI package not installed. Use: pip install openai")
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=Config.OPENAI_LLM,
        messages=chat_history
    )
    return response.choices[0].message.content


def _generate_groq_response(api_key, chat_history):
    if not GROQ_AVAILABLE:
        raise ValueError("Groq package not installed. Use: pip install groq")
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=Config.GROQ_LLM,
        messages=chat_history
    )
    return response.choices[0].message.content


def _generate_ollama_response(chat_history):
    # Create system prompt for Windy with strict length constraints
    system_prompt = {
        "role": "system", 
        "content": """You are Windy, a helpful voice assistant. CRITICAL RULES:
- Keep responses under 30 words maximum
- Be direct and to the point
- No special characters, symbols, or formatting
- One main idea per response
- Conversational but brief
- If asked complex questions, give short summary only
- Example: "What's India like?" → "India is a diverse country with rich culture, amazing food, and over 1.4 billion people."
Keep it SHORT and NATURAL for voice interaction."""
    }
    
    # Add system prompt to beginning of chat history
    messages_with_system = [system_prompt] + chat_history
    
    response = ollama.chat(
        model=Config.OLLAMA_LLM,
        messages=messages_with_system,
        options={
            "temperature": Config.RESPONSE_TEMPERATURE,
            "top_p": 0.7,  # Lower for faster, more focused responses
            "top_k": 20,   # Reduce choices for faster generation
            "num_predict": Config.MAX_RESPONSE_TOKENS,  # Limit token count
            "repeat_penalty": 1.1,  # Avoid repetition
            "num_ctx": 1024,  # Smaller context window for speed
        }
    )
    return response['message']['content']


def _clean_response(response):
    """
    Clean the LLM response to remove unwanted characters and enforce length limits.
    """
    if not response:
        return "I didn't catch that. Could you repeat?"
    
    # Remove markdown formatting
    response = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', response)  # Remove *bold* and **bold**
    response = re.sub(r'_{1,2}([^_]+)_{1,2}', r'\1', response)    # Remove _italic_ and __italic__
    
    # Remove special characters and symbols
    response = re.sub(r'[#\-=`~\[\]{}()<>]', '', response)  # Remove common markdown symbols
    response = re.sub(r'---+', '', response)  # Remove horizontal lines
    response = re.sub(r'\*{3,}', '', response)  # Remove multiple asterisks
    
    # Remove wake word instructions
    response = re.sub(r'.*\*\*.*wake.*up.*\*\*.*', '', response, flags=re.IGNORECASE)
    response = re.sub(r'.*\*\*.*farewell.*\*\*.*', '', response, flags=re.IGNORECASE)
    response = re.sub(r'.*say.*"hi windy".*', '', response, flags=re.IGNORECASE)
    response = re.sub(r'.*say.*"bye windy".*', '', response, flags=re.IGNORECASE)
    
    # Clean up multiple spaces and newlines
    response = re.sub(r'\n+', ' ', response)  # Replace newlines with spaces
    response = re.sub(r'\s+', ' ', response)  # Replace multiple spaces with single space
    
    # Remove leading/trailing whitespace
    response = response.strip()
    
    # Enforce word count limit (from config for ~20 second speech)
    words = response.split()
    max_words = Config.MAX_RESPONSE_WORDS
    if len(words) > max_words:
        # Keep first N words and ensure sentence ends properly
        response = ' '.join(words[:max_words])
        # Try to end at a natural sentence boundary
        if not response.endswith(('.', '!', '?')):
            # Find last sentence ending within the limit
            for i in range(len(response)-1, -1, -1):
                if response[i] in '.!?':
                    response = response[:i+1]
                    break
            else:
                # No sentence ending found, add period
                response += '.'
    
    # If response is empty after cleaning, provide fallback
    if not response or len(response.strip()) < 3:
        return "I'm here to help! What would you like to know?"
    
    # Ensure response ends with proper punctuation for speech
    if not response.endswith(('.', '!', '?')):
        response += '.'
    
    # Final word count check - if still too long, provide generic short response
    final_words = response.split()
    if len(final_words) > 35:  # Hard limit with some buffer
        return "That's an interesting question. Could you be more specific?"
    
    return response