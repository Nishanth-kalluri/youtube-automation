# orchestration/nodes/media_nodes.py
from services.tts_service import TTSService
from services.image_generator import ImageGenerator
from utils.logger import Logger

logger = Logger(__name__)
tts_service = TTSService()
image_generator = ImageGenerator()

def generate_audio(state):
    """Node to generate audio from script using TTS"""
    logger.info("Generating audio from script")
    
    try:
        # Update status
        state_dict = state.dict()
        state_dict["status_message"] = "Generating audio from script"
        
        # Generate audio
        audio_path = tts_service.generate_audio(state.narration)
        print("generated audio :{}",audio_path)
        # Update state
        state_dict["audio_path"] = audio_path
        state_dict["status_message"] = "Audio generated successfully"
        
        return state_dict
        
    except Exception as e:
        logger.error(f"Error in generate_audio: {e}")
        state_dict = state.dict()
        state_dict["error"] = f"Failed to generate audio: {str(e)}"
        state_dict["has_error"] = True
        state_dict["status_message"] = "Error generating audio"
        return state_dict

def generate_images(state):
    """Node to generate images from prompts"""
    logger.info(f"Generating images from {len(state.image_prompts)} prompts")
    
    try:
        # Update status
        state_dict = state.dict()
        state_dict["status_message"] = "Generating images from prompts"
        
        # Generate images
        image_paths = image_generator.generate_images(state.image_prompts)
        
        # Update state
        state_dict["image_paths"] = image_paths
        state_dict["status_message"] = "Images generated successfully"
        
        return state_dict
        
    except Exception as e:
        logger.error(f"Error in generate_images: {e}")
        state_dict = state.dict()
        state_dict["error"] = f"Failed to generate images: {str(e)}"
        state_dict["has_error"] = True
        state_dict["status_message"] = "Error generating images"
        return state_dict

def check_pause_media(state):
    """Node to check if workflow should pause after media generation"""
    logger.info("Checking if workflow should pause after media generation")
    
    state_dict = state.dict()
    
    # If we're paused for media review, set the pause reason
    if state.is_paused and state.pause_reason == "review_media":
        state_dict["status_message"] = "Paused for media review. Click Continue when ready."
    
    return state_dict