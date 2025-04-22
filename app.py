# app.py
import streamlit as st
import threading
import time
from config import settings
from orchestration.workflow import workflow
from orchestration.schema import WorkflowState
from utils.streamlit_helpers import (
    initialize_session_state,
    validate_api_keys,
    display_news_review,
    display_script_review,
    display_media_review,
    display_video_review,
    setup_sidebar_config
)

def run_workflow_thread(topic, pause_checkpoints):
    """Run the workflow in a separate thread"""
    # Initialize state
    initial_state = WorkflowState(topic=topic)
    
    # Execute workflow with streaming updates
    for step_output in workflow.stream(initial_state):
        # Update session state with current workflow state
        st.session_state.workflow_state = step_output
        
        # Check if we should pause at this point
        current_node = step_output.get("__metadata__", {}).get("current_node", "")
        
        if current_node == "check_pause_news" and pause_checkpoints.get("review_news", False):
            st.session_state.is_paused = True
            st.session_state.pause_reason = "review_news"
            # Wait until unpaused
            while st.session_state.is_paused:
                time.sleep(0.5)
        
        elif current_node == "check_pause_script" and pause_checkpoints.get("review_script", False):
            st.session_state.is_paused = True
            st.session_state.pause_reason = "review_script"
            # Wait until unpaused
            while st.session_state.is_paused:
                time.sleep(0.5)
        
        elif current_node == "check_pause_media" and pause_checkpoints.get("review_media", False):
            st.session_state.is_paused = True
            st.session_state.pause_reason = "review_media"
            # Wait until unpaused
            while st.session_state.is_paused:
                time.sleep(0.5)
        
        elif current_node == "check_pause_video" and pause_checkpoints.get("review_video", False):
            st.session_state.is_paused = True
            st.session_state.pause_reason = "review_video"
            # Wait until unpaused
            while st.session_state.is_paused:
                time.sleep(0.5)
    
    # Workflow completed
    st.session_state.is_running = False

def main():
    """Main Streamlit application"""
    st.title("AI News Video Generator")
    st.write("Generate news videos automatically from trending topics or your own input.")
    
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
    
    # Input form
    with st.form(key="input_form"):
        topic = st.text_input("News Topic (Optional)", placeholder="Leave empty to use trending topics")
    
    # Checkpoints for pausing
        st.subheader("Review Checkpoints")
        col1, col2 = st.columns(2)
        with col1:
            review_news = st.checkbox("Review Consolidated News", value=True)
            review_script = st.checkbox("Review Generated Script & Prompts", value=True)
        with col2:
            review_media = st.checkbox("Review Generated Media", value=True)
            review_video = st.checkbox("Review Final Video", value=True)
    
    # Submit button
        submit_button = st.form_submit_button("Generate Video")

# Handle form submission
    if submit_button:
    # Start workflow regardless of topic (the workflow will handle empty topics)
        pause_checkpoints = {
            "review_news": review_news,
            "review_script": review_script,
            "review_media": review_media,
            "review_video": review_video
        }
    
    # Start workflow in a separate thread
        st.session_state.is_running = True
        workflow_thread = threading.Thread(
            target=run_workflow_thread,
            args=(topic, pause_checkpoints),
            daemon=True
        )
        st.session_state.workflow_thread = workflow_thread
        workflow_thread.start()
    
    # Rerun to refresh UI
        st.rerun()
    
    # Display workflow status and results
    if st.session_state.is_running or st.session_state.workflow_state:
        state = st.session_state.workflow_state
        
        # Status area
        status_container = st.container()
        
        if state:
            # Show status
            if state.has_error:
                status_container.error(f"Error: {state.error}")
            else:
                status_container.info(state.status_message)
            
            # Display pause screens based on pause reason
            if st.session_state.is_paused:
                if st.session_state.pause_reason == "review_news" and state.consolidated_news:
                    display_news_review(state.consolidated_news)
                
                elif st.session_state.pause_reason == "review_script" and state.script:
                    display_script_review(state.script, state.image_prompts)
                
                elif st.session_state.pause_reason == "review_media" and (state.audio_path or state.image_paths):
                    display_media_review(state.audio_path, state.image_paths)
                
                elif st.session_state.pause_reason == "review_video" and state.video_path:
                    display_video_review(state.video_path)
                
                # Continue button
                if st.button("Continue"):
                    st.session_state.is_paused = False
                    st.session_state.pause_reason = ""
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
        else:
            status_container.info("Starting workflow...")
    
    # Additional information
    st.sidebar.markdown("---")
    st.sidebar.subheader("About")
    st.sidebar.info(
        "This application generates news videos automatically by:\n"
        "1. Fetching news on a topic\n"
        "2. Generating a script\n"
        "3. Creating audio and images\n"
        "4. Assembling a video\n"
        "5. Optionally uploading to YouTube"
    )

if __name__ == "__main__":
    main()