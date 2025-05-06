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
    
    if 'trending_topics' not in st.session_state:
        st.session_state.trending_topics = []
    
    if 'selected_trending_topic' not in st.session_state:
        st.session_state.selected_trending_topic = ""

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

def display_trending_topics(trending_topics):
    """
    Display trending topics and allow selection
    
    Returns:
        str: Selected trending topic or empty string
    """
    if not trending_topics:
        st.warning("No trending topics available at the moment.")
        return ""
    
    st.subheader("Trending Topics")
    
    # Display trending topics in a grid
    cols = st.columns(5)
    selected_topic = ""
    
    # Limit to top 10 trends
    display_topics = trending_topics[:10]
    
    for i, topic in enumerate(display_topics):
        col_index = i % 5
        with cols[col_index]:
            topic_selected = st.button(
                topic, 
                key=f"trend_{i}",
                use_container_width=True,
                type="secondary" if st.session_state.get('selected_trending_topic') != topic else "primary"
            )
            if topic_selected:
                st.session_state.selected_trending_topic = topic
                selected_topic = topic
    
    # Return the selected topic
    return st.session_state.get('selected_trending_topic', "")

def display_news_review(consolidated_news):
    """Display consolidated news for review"""
    st.write("Review the consolidated news content before proceeding to script generation:")
    
    # Show the consolidated news in a nicer format
    st.text_area("Consolidated News", consolidated_news, height=300)
    
    # Add edit functionality
    edited_news = st.text_area("Edit News (if needed)", consolidated_news, height=300)
    
    # Update session state if edited
    if edited_news != consolidated_news:
        st.session_state.workflow_state.consolidated_news = edited_news
        st.success("News content updated.")

def display_script_review(script, image_prompts):
    """Display script and image prompts for review"""
    tab1, tab2 = st.tabs(["Script", "Image Prompts"])
    
    with tab1:
        st.write("Review the generated script:")
        edited_script = st.text_area("Script", script, height=400)
        
        # Update session state if edited
        if edited_script != script:
            st.session_state.workflow_state.script = edited_script
            st.success("Script updated.")
    
    with tab2:  
        st.write("Review the generated image prompts:")
        
        edited_prompts = []
        for i, prompt in enumerate(image_prompts):
            edited_prompt = st.text_input(f"Image {i+1}", prompt)
            edited_prompts.append(edited_prompt)
        
        # Update session state if any prompts were edited
        if edited_prompts != image_prompts:
            st.session_state.workflow_state.image_prompts = edited_prompts
            st.success("Image prompts updated.")

def display_media_review(audio_path, image_paths):
    """Display generated media for review"""
    # Create tabs for audio and images
    tab1, tab2 = st.tabs(["Audio", "Images"])
    
    with tab1:
        # Audio player with better layout
        if audio_path and os.path.exists(audio_path):
            st.write("Review the generated audio narration:")
            st.audio(audio_path)
            st.download_button(
                "Download Audio",
                data=open(audio_path, "rb").read(),
                file_name=os.path.basename(audio_path),
                mime="audio/mp3"
            )
        else:
            st.warning("Audio file not found or not generated yet.")
    
    with tab2:
        # Image display
        if image_paths:
            st.write("Review the generated images:")
            
            # Calculate optimal number of columns based on number of images
            num_cols = min(3, len(image_paths))
            cols = st.columns(num_cols)
            
            for i, img_path in enumerate(image_paths):
                if os.path.exists(img_path):
                    with cols[i % num_cols]:
                        st.image(img_path, caption=f"Image {i+1}", use_column_width=True)
                        st.download_button(
                            f"Download Image {i+1}",
                            data=open(img_path, "rb").read(),
                            file_name=os.path.basename(img_path),
                            mime="image/jpeg"
                        )
                else:
                    with cols[i % num_cols]:
                        st.warning(f"Image {i+1} not found or not generated yet.")
        else:
            st.warning("No images generated yet.")

def display_video_review(video_path):
    """Display generated video for review"""
    if video_path and os.path.exists(video_path):
        st.write("Review the generated video:")
        
        # Video player
        st.video(video_path)
        
        # Download option
        st.download_button(
            "Download Video",
            data=open(video_path, "rb").read(),
            file_name=os.path.basename(video_path),
            mime="video/mp4"
        )
        
        # Metadata display if available
        if hasattr(st.session_state.workflow_state, 'title') and st.session_state.workflow_state.title:
            with st.expander("Video Metadata"):
                st.text_input("Title", st.session_state.workflow_state.title)
                st.text_area("Description", st.session_state.workflow_state.description)
                st.text_input("Emotion", st.session_state.workflow_state.emotion)
    else:
        st.warning("Video not found or not generated yet.")

def setup_sidebar_config():
    """Setup configuration in sidebar"""
    with st.sidebar:
        st.header("Configuration")
        
        # Collapsible sections for better organization
        with st.expander("API Keys", expanded=False):
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
        
        # YouTube Integration
        with st.expander("YouTube Integration", expanded=False):
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
        
        # Advanced Settings
        with st.expander("Advanced Settings", expanded=False):
            st.slider("News Lookback Days", 
                    min_value=1, 
                    max_value=7, 
                    value=1, 
                    key="news_lookback_days",
                    help="Number of days to look back for news articles")
            
            st.selectbox("Language", 
                        options=["English", "Spanish", "French", "German"], 
                        index=0,
                        key="news_language",
                        help="Language for news articles")
        
        # Save button
        if st.button("Save Configuration", type="primary"):
            # Update settings with values from session state
            settings.EVENT_REGISTRY_API_KEY = st.session_state.event_registry_api_key
            settings.GROQ_API_KEY = st.session_state.groq_api_key
            settings.GOOGLE_CLOUD_SERVICE_ACCOUNT_PATH = st.session_state.google_cloud_sa_path
            
            if st.session_state.get('enable_youtube_upload', False):
                settings.YOUTUBE_CLIENT_SECRETS_PATH = st.session_state.youtube_client_secrets_path
                settings.YOUTUBE_TOKEN_PICKLE_PATH = st.session_state.youtube_token_pickle_path
            
            st.success("Configuration saved!")
        
        # Application Info
        st.markdown("---")
        st.subheader("About")
        st.info(
            "AI News Video Generator automatically creates news videos by:\n"
            "1. Fetching trending topics and news\n"
            "2. Generating an engaging script\n"
            "3. Creating narration audio and relevant images\n"
            "4. Assembling a professional video\n"
            "5. Optionally uploading to YouTube"
        )