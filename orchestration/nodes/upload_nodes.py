# orchestration/nodes/upload_nodes.py
import os
from services.youtube_uploader import YouTubeUploader
from utils.logger import Logger

logger = Logger(__name__)
youtube_uploader = YouTubeUploader()

def upload_video(state):
    """Node to upload video to YouTube"""
    logger.info("Uploading video to YouTube")
    
    try:
        # Update status
        state_dict = state.dict()
        state_dict["status_message"] = "Uploading video to YouTube"
        
        # Generate title and description from script and consolidated news
        title = f"News Update: {state.topic}"
        description = (
            f"Auto-generated news video about {state.topic}.\n\n"
            f"Summary:\n{state.consolidated_news[:500]}...\n\n"
            "This video was automatically generated."
        )
        
        # Upload video
        upload_status = youtube_uploader.upload_video(state.video_path, title, description)
        
        # Update state
        state_dict["upload_status"] = upload_status
        
        if "error" in upload_status:
            state_dict["status_message"] = f"Video upload failed: {upload_status['error']}"
        else:
            state_dict["status_message"] = f"Video uploaded successfully: {upload_status['video_url']}"
            
            # Cleanup temporary files after successful upload
            cleanup_files(state.audio_path, state.image_paths, state.video_path)
        
        return state_dict
        
    except Exception as e:
        logger.error(f"Error in upload_video: {e}")
        state_dict = state.dict()
        state_dict["error"] = f"Failed to upload video: {str(e)}"
        state_dict["has_error"] = True
        state_dict["status_message"] = "Error uploading video"
        return state_dict

def cleanup_files(audio_path, image_paths, video_path):
    """Clean up temporary files after successful video upload"""
    logger.info("Cleaning up temporary files")
    
    # Delete audio file
    if audio_path and os.path.exists(audio_path):
        try:
            os.remove(audio_path)
            logger.info(f"Deleted audio file: {audio_path}")
        except Exception as e:
            logger.warning(f"Failed to delete audio file {audio_path}: {e}")
    
    # Delete image files
    for img_path in image_paths:
        if img_path and os.path.exists(img_path):
            try:
                os.remove(img_path)
                logger.info(f"Deleted image file: {img_path}")
            except Exception as e:
                logger.warning(f"Failed to delete image file {img_path}: {e}")
    
    # Delete video file
    if video_path and os.path.exists(video_path):
        try:
            os.remove(video_path)
            logger.info(f"Deleted video file: {video_path}")
        except Exception as e:
            logger.warning(f"Failed to delete video file {video_path}: {e}")