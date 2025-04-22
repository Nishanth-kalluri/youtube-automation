# orchestration/nodes/video_nodes.py
from services.video_editor import VideoEditor
from utils.logger import Logger

logger = Logger(__name__)
video_editor = VideoEditor()

def assemble_video(state):
    """Node to assemble video from audio and images"""
    logger.info("Assembling video from audio and images")
    
    try:
        # Update status
        state_dict = state.dict()
        state_dict["status_message"] = "Assembling video"
        
        # Assemble video
        video_path = video_editor.create_video(state.audio_path, state.image_paths)
        
        # Update state
        state_dict["video_path"] = video_path
        state_dict["status_message"] = "Video assembled successfully"
        
        return state_dict
        
    except Exception as e:
        logger.error(f"Error in assemble_video: {e}")
        state_dict = state.dict()
        state_dict["error"] = f"Failed to assemble video: {str(e)}"
        state_dict["has_error"] = True
        state_dict["status_message"] = "Error assembling video"
        return state_dict

def check_pause_video(state):
    """Node to check if workflow should pause after video assembly"""
    logger.info("Checking if workflow should pause after video assembly")
    
    state_dict = state.dict()
    
    # If we're paused for video review, set the pause reason
    if state.is_paused and state.pause_reason == "review_video":
        state_dict["status_message"] = "Paused for video review. Click Continue when ready."
    
    return state_dict