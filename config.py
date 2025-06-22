# config.py
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables first
load_dotenv()

def initialize_app():
    """Initialize the application with proper configuration"""
    
    # Set the Groq API key and model configuration
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        st.error("GROQ_API_KEY not found in environment variables. Please check your .env file.")
        st.stop()

    # Set environment variables for CrewAI
    os.environ["GROQ_API_KEY"] = groq_api_key
    
    # Configure LLM settings
    os.environ["CREWAI_LLM_MODEL"] = "groq/llama3-8b-8192"
    
    # Set session state flags to avoid re-initialization
    if 'env_loaded' not in st.session_state:
        st.session_state.env_loaded = True
    
    if 'model_name' not in st.session_state:
        st.session_state.model_name = 'llama3-8b-8192'
    
    # Debug information (optional)
    if st.session_state.get('debug_mode', False):
        st.write(f"Model being used: {os.getenv('CREWAI_LLM_MODEL')}")
        st.write(f"API Key configured: {'Yes' if groq_api_key else 'No'}")
    
    return True