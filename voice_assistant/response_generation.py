# voice_assistant/response_generation.py

import logging
import re

from openai import OpenAI
from groq import Groq
import ollama

from voice_assistant.config import Config


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
            response = _generate_openai_response(api_key, chat_history)
        elif model == 'groq':
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
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=Config.OPENAI_LLM,
        messages=chat_history
    )
    return response.choices[0].message.content


def _generate_groq_response(api_key, chat_history):
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=Config.GROQ_LLM,
        messages=chat_history
    )
    return response.choices[0].message.content


def _generate_ollama_response(chat_history):
    # Create system prompt for Windy
    system_prompt = {
        "role": "system", 
        "content": """You are Windy, a helpful voice assistant. Keep your responses:
- Conversational and natural
- Brief and to the point  
- Free of special characters, symbols, or formatting
- No asterisks, dashes, or markup
- No instructions about wake words or commands
- Just speak naturally like a friend"""
    }
    
    # Add system prompt to beginning of chat history
    messages_with_system = [system_prompt] + chat_history
    
    response = ollama.chat(
        model=Config.OLLAMA_LLM,
        messages=messages_with_system,
    )
    return response['message']['content']


def _clean_response(response):
    """
    Clean the LLM response to remove unwanted characters and formatting.
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
    
    # If response is empty after cleaning, provide fallback
    if not response or len(response.strip()) < 3:
        return "I'm here to help! What would you like to know?"
    
    # Ensure response ends with proper punctuation for speech
    if not response.endswith(('.', '!', '?')):
        response += '.'
    
    return response