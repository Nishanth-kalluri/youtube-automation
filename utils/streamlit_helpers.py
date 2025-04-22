# utils/streamlit_helpers.py
import streamlit as st
import os
from config import settings

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if 'workflow_state' not in st.session_state:
        st.session_state.workflow_state = None
    
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    
    if 'is_paused' not in st.session_state:
        st.session_state.is_paused = False
    
    if 'pause_reason' not in st.session_state:
        st.session_state.pause_reason = ""
    
    if 'workflow_thread' not in st.session_state:
        st.session_state.workflow_thread = None

def validate_api_keys():
    """Validate required API keys and credentials"""
    missing_keys = []
    
    # Check Event Registry API Key
    if not settings.EVENT_REGISTRY_API_KEY:
        missing_keys.append("EVENT_REGISTRY_API_KEY")
    
    # Check Groq API Key
    if not settings.GROQ_API_KEY:
        missing_keys.append("GROQ_API_KEY")
    
    # Check Google Cloud Service Account Path
    if not settings.GOOGLE_CLOUD_SERVICE_ACCOUNT_PATH or not os.path.exists(settings.GOOGLE_CLOUD_SERVICE_ACCOUNT_PATH):
        missing_keys.append("GOOGLE_CLOUD_SERVICE_ACCOUNT_PATH")
    
    # For YouTube upload feature
    if st.session_state.get('enable_youtube_upload', False):
        # Check YouTube Client Secrets Path
        if not settings.YOUTUBE_CLIENT_SECRETS_PATH or not os.path.exists(settings.YOUTUBE_CLIENT_SECRETS_PATH):
            missing_keys.append("YOUTUBE_CLIENT_SECRETS_PATH")
    
    return missing_keys

def display_news_review(consolidated_news):
    """Display consolidated news for review"""
    st.subheader("News Review")
    st.write("Review the consolidated news before generating a script:")
    
    # Show the consolidated news
    st.text_area("Consolidated News", consolidated_news, height=300, disabled=True)
    
    # Add edit functionality if needed in the future
    # edited_news = st.text_area("Edit News (if needed)", consolidated_news, height=300)
    # return edited_news

def display_script_review(script, image_prompts):
    """Display script and image prompts for review"""
    st.subheader("Script & Image Prompts Review")
    
    # Script
    st.write("Review the generated script:")
    st.text_area("Script", script, height=300, disabled=True)
    
    # Image Prompts
    st.write("Review the generated image prompts:")
    for i, prompt in enumerate(image_prompts):
        st.text_input(f"Image {i+1}", prompt, disabled=True)
    
    # Add edit functionality if needed in the future
    # edited_script = st.text_area("Edit Script (if needed)", script, height=300)
    # edited_prompts = []
    # for i, prompt in enumerate(image_prompts):
    #     edited_prompts.append(st.text_input(f"Edit Image Prompt {i+1}", prompt))
    # return edited_script, edited_prompts

def display_media_review(audio_path, image_paths):
    """Display generated media for review"""
    st.subheader("Media Review")
    
    # Audio player
    if audio_path and os.path.exists(audio_path):
        st.write("Review the generated audio:")
        st.audio(audio_path)
    else:
        st.warning("Audio file not found or not generated yet.")
    
    # Image display
    if image_paths:
        st.write("Review the generated images:")
        cols = st.columns(min(3, len(image_paths)))
        for i, img_path in enumerate(image_paths):
            if os.path.exists(img_path):
                cols[i % len(cols)].image(img_path, caption=f"Image {i+1}", use_column_width=True)
            else:
                cols[i % len(cols)].warning(f"Image {i+1} not found or not generated yet.")
    else:
        st.warning("No images generated yet.")

def display_video_review(video_path):
    """Display generated video for review"""
    st.subheader("Video Review")
    
    if video_path and os.path.exists(video_path):
        st.write("Review the generated video:")
        st.video(video_path)
    else:
        st.warning("Video not found or not generated yet.")

def setup_sidebar_config():
    """Setup configuration in sidebar"""
    with st.sidebar:
        st.subheader("Configuration")
        
        # API Keys (securely)
        st.text_input("Event Registry API Key", 
                      value=settings.EVENT_REGISTRY_API_KEY, 
                      type="password", 
                      key="event_registry_api_key",
                      help="API key for fetching news")
                      
        st.text_input("Groq API Key", 
                      value=settings.GROQ_API_KEY, 
                      type="password", 
                      key="groq_api_key",
                      help="API key for Groq LLM")
                      
        st.text_input("Google Cloud Service Account Path", 
                      value=settings.GOOGLE_CLOUD_SERVICE_ACCOUNT_PATH,
                      key="google_cloud_sa_path",
                      help="Path to Google Cloud Service Account JSON file")
        
        # YouTube upload toggle
        st.checkbox("Enable YouTube Upload", 
                    value=st.session_state.get('enable_youtube_upload', False),
                    key='enable_youtube_upload')
        
        if st.session_state.get('enable_youtube_upload', False):
            st.text_input("YouTube Client Secrets Path", 
                          value=settings.YOUTUBE_CLIENT_SECRETS_PATH,
                          key="youtube_client_secrets_path",
                          help="Path to YouTube API client_secrets.json")
                          
            st.text_input("YouTube Token Pickle Path", 
                          value=settings.YOUTUBE_TOKEN_PICKLE_PATH,
                          key="youtube_token_pickle_path",
                          help="Path to save YouTube OAuth token pickle")
        
        # Save button
        if st.button("Save Configuration"):
            # Update settings with values from session state
            settings.EVENT_REGISTRY_API_KEY = st.session_state.event_registry_api_key
            settings.GROQ_API_KEY = st.session_state.groq_api_key
            settings.GOOGLE_CLOUD_SERVICE_ACCOUNT_PATH = st.session_state.google_cloud_sa_path
            
            if st.session_state.get('enable_youtube_upload', False):
                settings.YOUTUBE_CLIENT_SECRETS_PATH = st.session_state.youtube_client_secrets_path
                settings.YOUTUBE_TOKEN_PICKLE_PATH = st.session_state.youtube_token_pickle_path
            
            st.success("Configuration saved!")