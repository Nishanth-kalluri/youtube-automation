from groq import Groq
from config import settings
from utils.logger import Logger

class ScriptGenerator:
    def __init__(self):
        self.logger = Logger(__name__)
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
    
    def generate_script_and_prompts(self, consolidated_news):
        """Generate a video script and image prompts from consolidated news"""
        self.logger.info("Generating script and image prompts")
        
        # Prepare the prompt for Groq
        prompt = f"""
        I need to create a short video based on the following news summary:
        
        {consolidated_news}
        
        Please generate:
        
        1. A video script with clear sections for intro, 3-5 key points, and outro. The script should be engaging, 
           clear, and timed for a 30 to 45 seconds youtube shorts video.
        
        2. A list of 8-12 image prompts that would visually represent the story. These will be used to generate 
           ultra realisitic and 9:16 images using Pollinations.ai for youtube shorts. Each prompt should be highly detailed and descriptive to generate a 
           compelling 4k image that complements the script.

        IMPORTANT FORMATTING INSTRUCTIONS:
        - Begin the script section with the exact marker "<<VIDEO_SCRIPT_START>>" on its own line
        - End the script section with the exact marker "<<VIDEO_SCRIPT_END>>" on its own line
        - Begin the image prompts section with the exact marker "<<IMAGE_PROMPTS_START>>" on its own line
        - End the image prompts section with the exact marker "<<IMAGE_PROMPTS_END>>" on its own line
        - For image prompts, place each prompt on a new line with no numbering or bullets
        - Do not include any other text, explanations, or formatting outside these markers

        Example format:
        <<VIDEO_SCRIPT_START>>
        [Your complete script goes here]
        <<VIDEO_SCRIPT_END>>

        <<IMAGE_PROMPTS_START>>
        [First image prompt]
        [Second image prompt]
        [Third image prompt]
        <<IMAGE_PROMPTS_END>>
        """
        
        try:
            # Call Groq API
            response = self.groq_client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=2048,
                top_p=0.9,
            )
            
            # Extract the response content
            content = response.choices[0].message.content
            
            # Parse script and image prompts
            script_section = ""
            image_prompts = []
            
            # Extract script section
            if "<<VIDEO_SCRIPT_START>>" in content and "<<VIDEO_SCRIPT_END>>" in content:
                script_section = content.split("<<VIDEO_SCRIPT_START>>")[1].split("<<VIDEO_SCRIPT_END>>")[0].strip()
            else:
                self.logger.warning("Script markers not found in response - falling back to original parsing")
                # Fall back to original parsing if markers not found
                if "VIDEO SCRIPT:" in content and "IMAGE PROMPTS:" in content:
                    parts = content.split("IMAGE PROMPTS:")
                    script_section = parts[0].replace("VIDEO SCRIPT:", "").strip()

            # Extract image prompts
            if "<<IMAGE_PROMPTS_START>>" in content and "<<IMAGE_PROMPTS_END>>" in content:
                prompts_text = content.split("<<IMAGE_PROMPTS_START>>")[1].split("<<IMAGE_PROMPTS_END>>")[0].strip()
                image_prompts = [line.strip() for line in prompts_text.split('\n') if line.strip()]
            else:
                self.logger.warning("Image prompt markers not found in response - falling back to original parsing")
                # Fall back to original parsing if markers not found
                if "IMAGE PROMPTS:" in content:
                    prompts_text = content.split("IMAGE PROMPTS:")[1].strip()
                    for line in prompts_text.split('\n'):
                        if line.strip():
                            # Remove numbering if present
                            if '. ' in line:
                                prompt = line.split('. ', 1)[1].strip()
                            else:
                                prompt = line.strip()
                            
                            if prompt:
                                image_prompts.append(prompt)
            
            # If still empty, make a final attempt with simplistic parsing
            if not script_section or not image_prompts:
                self.logger.warning("Standard parsing failed - attempting basic extraction")
                lines = content.split('\n')
                script_lines = []
                for line in lines:
                    if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.')):
                        image_prompts.append(line.split('. ', 1)[1].strip())
                    else:
                        script_lines.append(line)
                
                if not script_section:
                    script_section = '\n'.join(script_lines)
            
            self.logger.info(f"Generated script ({len(script_section)} chars) and {len(image_prompts)} image prompts")
            
            return script_section, image_prompts
            
        except Exception as e:
            self.logger.error(f"Error generating script: {e}")
            return "Error generating script.", ["Generic news image"]