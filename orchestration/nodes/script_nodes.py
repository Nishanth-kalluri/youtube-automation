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
        script, image_prompts, emotion, title, description = script_generator.generate_script_and_prompts(state.consolidated_news)
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
        print("EMOTION:")
        print(emotion)
        
        # Enhance image prompts with more detailed descriptions
        enhanced_image_prompts = enhance_image_prompts(state.consolidated_news, image_prompts)
        print("ENHANCED IMAGE PROMPTS:")
        print(enhanced_image_prompts)
        
        # Update state
        state_dict["script"] = script
        state_dict["image_prompts"] = enhanced_image_prompts  # Use enhanced prompts instead
        state_dict["narration"] = narration_text  # Store as a single string
        state_dict["emotion"] = emotion
        state_dict["status_message"] = "Script and image prompts generated successfully"
        state_dict["title"] = title
        state_dict["description"] = description
        return state_dict
        
    except Exception as e:
        logger.error(f"Error in generate_script_and_prompts: {e}")
        state_dict = state.dict()
        state_dict["error"] = f"Failed to generate script: {str(e)}"
        state_dict["has_error"] = True
        state_dict["status_message"] = "Error generating script"
        return state_dict

def enhance_image_prompts(consolidated_news, original_prompts):
    """Function to enhance image prompts with more detailed descriptions using simplified strict formatting"""
    logger.info("Enhancing image prompts with more detailed descriptions")
    
    try:
        # Create a simple list of original prompts for context
        formatted_prompts = "\n".join([f"• {prompt}" for prompt in original_prompts])
        
        # Construct a simplified but strict prompt for the LLM
        prompt = f"""
        I need to enhance these image prompts for a YouTube Shorts video based on this news summary:
        
        NEWS SUMMARY:
        {consolidated_news}
        
        ORIGINAL PROMPTS:
        {formatted_prompts}
        
        INSTRUCTIONS:
        Transform each original prompt into a detailed professional AI image generation prompt. Each enhanced prompt must:
        - Be 100-150 words long
        - Include specific subject positioning, camera angle, lighting, and mood
        - Specify a cohesive color palette that aligns with the message tone
        - Add depth cues like foreground/midground/background elements
        - Include fine details like textures, materials, and environmental elements
        - Specify '9:16 vertical aspect ratio' for YouTube Shorts format
        - Include the exact phrase: "8K resolution, photorealistic, professional photography quality"
        - Be a complete, standalone image description
        - Avoid using any sensitive, offensive, or inappropriate language
        - Maintain appropriate content suitable for all audiences
        
        FORMAT YOUR RESPONSE EXACTLY LIKE THIS:
        
        START_PROMPT
        [First complete enhanced prompt goes here]
        END_PROMPT
        
        START_PROMPT
        [Second complete enhanced prompt goes here]
        END_PROMPT
        
        (Continue this pattern for all prompts)
        
        Important: Do not include any text, explanations, or comments outside the START_PROMPT/END_PROMPT tags.
        Do not use any sensitive, offensive, or inappropriate terminology in your descriptions.
        """
        
        # Call the LLM via Groq
        response = script_generator.groq_client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=4096,
            top_p=0.9,
        )
        
        # Extract the content from the response
        content = response.choices[0].message.content
        print("RAW ENHANCED PROMPTS RESPONSE:")
        print(content)
        
        # Parse the enhanced prompts using simple string splitting
        enhanced_prompts = []
        
        # Split content by START_PROMPT marker
        parts = content.split("START_PROMPT")
        
        # Process each part (skip the first part which is before any START_PROMPT)
        for part in parts[1:]:
            # Split by END_PROMPT and take the first part (the actual prompt)
            if "END_PROMPT" in part:
                prompt_text = part.split("END_PROMPT")[0].strip()
                if prompt_text:
                    enhanced_prompts.append(prompt_text)
        
        # Validate and fix each prompt
        validated_prompts = []
        required_elements = ["9:16 vertical aspect ratio", "8K resolution, photorealistic, professional photography quality"]
        
        for i, prompt in enumerate(enhanced_prompts):
            # Simple validation and fixes
            fixed_prompt = prompt
            
            # Check for minimum length (about 75 words)
            if len(prompt.split()) < 75:
                # If too short, enhance with original content
                if i < len(original_prompts):
                    fixed_prompt = f"{original_prompts[i]}. {fixed_prompt}"
            
            # Ensure required elements are present
            for element in required_elements:
                if element not in fixed_prompt:
                    fixed_prompt += f" {element}."
            
            # Clean up any formatting issues
            fixed_prompt = fixed_prompt.replace("[", "").replace("]", "")
            fixed_prompt = ' '.join(fixed_prompt.split())  # Fix whitespace
            
            # Ensure proper ending punctuation
            if not fixed_prompt.endswith(('.', '!', '?')):
                fixed_prompt += '.'
                
            validated_prompts.append(fixed_prompt)
        
        # If we have fewer enhanced prompts than original ones, enhance the remaining
        if len(validated_prompts) < len(original_prompts):
            logger.warning(f"Only got {len(validated_prompts)} enhanced prompts from {len(original_prompts)} originals")
            
            for i in range(len(validated_prompts), len(original_prompts)):
                enhanced_original = (
                    f"{original_prompts[i]}. Detailed scene with professional positioning and composition. "
                    f"Dramatic lighting with rich, cohesive color palette. Includes foreground, midground, and background "
                    f"elements with fine texture details. 9:16 vertical aspect ratio. 8K resolution, photorealistic, "
                    f"professional photography quality."
                )
                validated_prompts.append(enhanced_original)
        
        logger.info(f"Successfully enhanced {len(validated_prompts)} image prompts")
        return validated_prompts
        
    except Exception as e:
        logger.error(f"Error enhancing image prompts: {e}")
        logger.warning("Falling back to original image prompts with basic enhancements")
        
        # Add basic enhancements to original prompts as fallback
        enhanced_originals = []
        for prompt in original_prompts:
            enhanced_original = (
                f"{prompt}. Professional composition with balanced subject positioning. "
                f"Soft, natural lighting with complementary color palette. Includes foreground and background elements "
                f"for depth. Fine details in textures and materials. 9:16 vertical aspect ratio. 8K resolution, "
                f"photorealistic, professional photography quality."
            )
            enhanced_originals.append(enhanced_original)
        
        return enhanced_originals

def check_pause_script(state):
    """Node to check if workflow should pause after script generation"""
    logger.info("Checking if workflow should pause after script generation")
    
    state_dict = state.dict()
    
    # If we're paused for script review, set the pause reason
    if state.is_paused and state.pause_reason == "review_script":
        state_dict["status_message"] = "Paused for script review. Click Continue when ready."
    
    return state_dict