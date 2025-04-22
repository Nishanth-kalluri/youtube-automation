import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

class Settings:
    # API Keys - prioritize Streamlit secrets over environment variables
    @property
    def EVENT_REGISTRY_API_KEY(self):
        return st.secrets.get("EVENT_REGISTRY_API_KEY", os.getenv("EVENT_REGISTRY_API_KEY"))
    
    @property
    def GROQ_API_KEY(self):
        return st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
    
    # File paths for Google Cloud and YouTube
    @property
    def GOOGLE_CLOUD_SERVICE_ACCOUNT_PATH(self):
        return st.secrets.get("GOOGLE_CLOUD_SERVICE_ACCOUNT_PATH", 
                              os.getenv("GOOGLE_CLOUD_SERVICE_ACCOUNT_PATH"))
    
    @property
    def YOUTUBE_CLIENT_SECRETS_PATH(self):
        return st.secrets.get("YOUTUBE_CLIENT_SECRETS_PATH", 
                              os.getenv("YOUTUBE_CLIENT_SECRETS_PATH"))
    
    @property
    def YOUTUBE_TOKEN_PICKLE_PATH(self):
        return st.secrets.get("YOUTUBE_TOKEN_PICKLE_PATH", 
                              os.getenv("YOUTUBE_TOKEN_PICKLE_PATH"))
    
    # Directory paths
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
    AUDIO_DIR = os.path.join(OUTPUT_DIR, "audio")
    IMAGES_DIR = os.path.join(OUTPUT_DIR, "images")
    VIDEOS_DIR = os.path.join(OUTPUT_DIR, "videos")
    TEMP_DIR = os.path.join(OUTPUT_DIR, "temp")
    
    # Assets
    BG_MUSIC_PATH = os.getenv("BG_MUSIC_PATH", "assets/bg_music.mp3")
    PLACEHOLDER_IMAGE_PATH = os.getenv("PLACEHOLDER_IMAGE_PATH", "assets/placeholder.jpg")
    
    # Ensure directories exist
    @classmethod
    def ensure_directories(cls):
        for directory in [cls.OUTPUT_DIR, cls.AUDIO_DIR, cls.IMAGES_DIR, cls.VIDEOS_DIR, cls.TEMP_DIR]:
            os.makedirs(directory, exist_ok=True)

# Create a settings instance
settings = Settings()
settings.ensure_directories()