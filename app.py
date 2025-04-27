# app.py
import streamlit as st
from config import settings
from orchestration.workflow import workflow
from orchestration.schema import WorkflowState
from services.trends_scraper import TrendsScraper
from utils.streamlit_helpers import (
    initialize_session_state,
    validate_api_keys,
    display_news_review,
    display_script_review,
    display_media_review,
    display_video_review,
    setup_sidebar_config,
    display_trending_topics
)

def main():
    """Main Streamlit application"""
    # Page configuration
    st.set_page_config(
        page_title="AI News Video Generator",
        page_icon="📺",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Setup sidebar configuration
    setup_sidebar_config()
    
    # Validate API keys
    missing_keys = validate_api_keys()
    if missing_keys:
        st.error(f"Missing required configuration: {', '.join(missing_keys)}")
        st.info("Please configure the missing items in the sidebar.")
        return
    
    # Main content area
    with st.container():
        # Header with logo and title
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image("assets/placeholder.png", width=100)
        with col2:
            st.title("AI News Video Generator")
            st.write("Generate professional news videos automatically from trending topics or your own input.")
    
    # Get trending topics at application load if not already in session state
    trending_topics=st.session_state.trending_topics
    if len(trending_topics)==0:
        with st.spinner("Fetching trending topics..."):
            try:
                trends_scraper = TrendsScraper()
                topics = trends_scraper.get_trending_topics()
                st.session_state.trending_topics = topics
            except Exception as e:
                st.error(f"Error fetching trending topics: {str(e)}")
                st.session_state.trending_topics = []
    
    # Display trending topics for selection
    selected_topic = display_trending_topics(st.session_state.trending_topics)
    
    # Topic input form
    with st.form(key="input_form"):
        st.subheader("News Topic")
        
        # User input for custom topic
        if selected_topic:
            topic = st.text_input("Or enter your own topic:", placeholder="Leave empty to use selected trending topic")
        else:
            topic = st.text_input("Enter news topic:", placeholder="Enter a topic of interest")
        
        # Use the selected trending topic if no custom topic is entered
        if not topic and selected_topic:
            topic = selected_topic
        
        # Checkpoints for pausing with improved UI
        st.subheader("Review Checkpoints")
        
        col1, col2 = st.columns(2)
        with col1:
            review_news = st.checkbox("Review Consolidated News", value=True,
                                       help="Pause after fetching news to review content")
            review_script = st.checkbox("Review Generated Script & Prompts", value=True,
                                         help="Pause after generating script to review content")
        with col2:
            review_media = st.checkbox("Review Generated Media", value=True,
                                       help="Pause after generating audio and images to review content")
            review_video = st.checkbox("Review Final Video", value=True,
                                       help="Pause after video assembly to review before upload")
        
        # Submit button
        submit_button = st.form_submit_button("Generate Video", 
                                             use_container_width=True,
                                             type="primary")

    # Handle form submission
    if submit_button:
        if not topic:
            st.error("Please either select a trending topic or enter your own topic!")
            return
            
        # Create pause checkpoints configuration
        pause_checkpoints = {
            "review_news": review_news,
            "review_script": review_script,
            "review_media": review_media,
            "review_video": review_video
        }
        
        # Execute workflow in the main thread (no separate thread)
        st.session_state.is_running = True
        
        # Initialize state
        initial_state = WorkflowState(topic=topic)
        
        # Progress bar
        progress_bar = st.progress(0)
        status_container = st.empty()
        status_container.info(f"Starting workflow for topic: {topic}")
        
        # Execute workflow step by step
        try:
            steps_total = 8  # Approximate number of steps in the workflow
            step_count = 0
            
            for step_output in workflow.stream(initial_state):
                # Update session state with current workflow state
                st.session_state.workflow_state = step_output
                
                # Update progress bar
                step_count += 1
                progress_percentage = min(step_count / steps_total, 1.0)
                progress_bar.progress(progress_percentage)
                
                # Update status message
                if "status_message" in step_output:
                    status_container.info(step_output["status_message"])
                
                # Check if we should pause at this point
                current_node = step_output.get("__metadata__", {}).get("current_node", "")
                
                if current_node == "check_pause_news" and pause_checkpoints.get("review_news", False):
                    st.session_state.is_paused = True
                    st.session_state.pause_reason = "review_news"
                    break
                
                elif current_node == "check_pause_script" and pause_checkpoints.get("review_script", False):
                    st.session_state.is_paused = True
                    st.session_state.pause_reason = "review_script"
                    break
                
                elif current_node == "check_pause_media" and pause_checkpoints.get("review_media", False):
                    st.session_state.is_paused = True
                    st.session_state.pause_reason = "review_media"
                    break
                
                elif current_node == "check_pause_video" and pause_checkpoints.get("review_video", False):
                    st.session_state.is_paused = True
                    st.session_state.pause_reason = "review_video"
                    break
                
            # If paused, show the appropriate review screen
            if st.session_state.is_paused:
                st.rerun()
            
        except Exception as e:
            st.error(f"Error in workflow execution: {str(e)}")
            st.session_state.is_running = False
    
    # Display workflow status and results
    state = st.session_state.workflow_state
    
    if state:
        # Show error if any
        if state.has_error:
            st.error(f"Error: {state.error}")
        
        # Display pause screens based on pause reason
        if st.session_state.is_paused:
            st.subheader(f"Paused at: {st.session_state.pause_reason.replace('_', ' ').title()}")
                
            if st.session_state.pause_reason == "review_news" and state.consolidated_news:
                display_news_review(state.consolidated_news)
            
            elif st.session_state.pause_reason == "review_script" and state.script:
                display_script_review(state.script, state.image_prompts)
            
            elif st.session_state.pause_reason == "review_media" and (state.audio_path or state.image_paths):
                display_media_review(state.audio_path, state.image_paths)
            
            elif st.session_state.pause_reason == "review_video" and state.video_path:
                display_video_review(state.video_path)
            
            # Continue button
            if st.button("Continue Processing", type="primary", use_container_width=True):
                st.session_state.is_paused = False
                st.session_state.pause_reason = ""
                
                # Continue the workflow
                initial_state = WorkflowState(**state.dict())
                
                st.session_state.is_running = True
                st.rerun()
        
        # Final results
        if not st.session_state.is_running and not st.session_state.is_paused:
            st.subheader("Final Results")
            
            if state.upload_status and "video_url" in state.upload_status:
                st.success(f"Video uploaded successfully!")
                st.markdown(f"[Watch on YouTube]({state.upload_status['video_url']})")
            elif state.video_path:
                st.success("Video generated successfully!")
                st.video(state.video_path)

if __name__ == "__main__":
    main()