# orchestration/nodes/script_nodes.py
from services.script_generator import ScriptGenerator
from utils.logger import Logger

logger = Logger(__name__)
script_generator = ScriptGenerator()

def generate_script_and_prompts(state):
    """Node to generate script and image prompts from consolidated news"""
    logger.info("Generating script and image prompts")
    
    try:
        # Update status
        state_dict = state.dict()
        state_dict["status_message"] = "Generating script and image prompts"
        
        # Generate script and prompts
        script, image_prompts = script_generator.generate_script_and_prompts(state.consolidated_news)
        print("SCRIPT:")
        print(script)
        print("IMAGE PROMPTS:")
        print(image_prompts)
        
        # Extract narration lines and combine into one continuous string
        narration_text = ""
        for line in script.split('\n'):
            if line.startswith('Narrator: "'):
                # Extract the content between quotes
                extracted_text = line.split('Narrator: "', 1)[1].rsplit('"', 1)[0]
                narration_text += extracted_text + " "  # Add space between segments
        
        # Remove trailing space and store as a single string
        narration_text = narration_text.strip()
        print("NARRATION TEXT:")
        print(narration_text)
        # Update state
        state_dict["script"] = script
        state_dict["image_prompts"] = image_prompts
        state_dict["narration"] = narration_text  # Store as a single string
        state_dict["status_message"] = "Script and image prompts generated successfully"
        
        return state_dict
        
    except Exception as e:
        logger.error(f"Error in generate_script_and_prompts: {e}")
        state_dict = state.dict()
        state_dict["error"] = f"Failed to generate script: {str(e)}"
        state_dict["has_error"] = True
        state_dict["status_message"] = "Error generating script"
        return state_dict
        
    except Exception as e:
        logger.error(f"Error in generate_script_and_prompts: {e}")
        state_dict = state.dict()
        state_dict["error"] = f"Failed to generate script: {str(e)}"
        state_dict["has_error"] = True
        state_dict["status_message"] = "Error generating script"
        return state_dict

def check_pause_script(state):
    """Node to check if workflow should pause after script generation"""
    logger.info("Checking if workflow should pause after script generation")
    
    state_dict = state.dict()
    
    # If we're paused for script review, set the pause reason
    if state.is_paused and state.pause_reason == "review_script":
        state_dict["status_message"] = "Paused for script review. Click Continue when ready."
    
    return state_dict