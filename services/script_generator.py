#services/script_generator.py
from groq import Groq
from config import settings
from utils.logger import Logger

class ScriptGenerator:
    def __init__(self):
        self.logger = Logger(__name__)
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
    
    def generate_script_and_prompts(self, consolidated_news):
        """Generate a video script and image prompts from consolidated news"""
        self.logger.info("Generating script, image prompts, emotion tone, title and description")
        
        # Prepare the prompt for Groq
        prompt = f"""
        I need to create a short video based on the following news summary:
        
        {consolidated_news}
        
        Please generate:
        
        1. A video script with clear sections for intro, 3-5 key points, outro and emotions. The script should be engaging, 
           clear, and timed for a 30 to 45 seconds youtube shorts video.
           
           IMPORTANT: All narration lines MUST be formatted as 'Narrator: "actual narration text"' for consistent processing.
           Each narrator line should be on its own line, surrounded by double quotes, and prefixed with 'Narrator: '.
           Example: Narrator: "Hey gamers! This week has been HUGE for gaming fans!"
        
        2. A list of 8-12 image prompts that would visually represent the story. These will be used to generate 
           ultra realisitic and 9:16 images using Pollinations.ai for youtube shorts. Each prompt should be highly detailed and descriptive to generate a 
           compelling 4k image that complements the script.
        
        3. The overall emotional tone for the narration. Choose ONE emotional tone from this list: happy, sad, excited, calm, angry, whisper, nervous.

        4. A catchy, attention-grabbing YouTube Shorts title (50-60 characters max) that will drive clicks and views.

        5. A concise YouTube Shorts description (2-3 sentences max) that summarizes the content and includes 5-7 relevant hashtags at the end.

        IMPORTANT FORMATTING INSTRUCTIONS:
        - Begin with the emotion marker "<<EMOTION_START>>" followed by your chosen emotion and "<<EMOTION_END>>" on the same line
        - Begin the script section with the exact marker "<<VIDEO_SCRIPT_START>>" on its own line
        - End the script section with the exact marker "<<VIDEO_SCRIPT_END>>" on its own line
        - Begin the image prompts section with the exact marker "<<IMAGE_PROMPTS_START>>" on its own line
        - End the image prompts section with the exact marker "<<IMAGE_PROMPTS_END>>" on its own line
        - Begin the title section with the exact marker "<<TITLE_START>>" on its own line
        - End the title section with the exact marker "<<TITLE_END>>" on its own line
        - Begin the description section with the exact marker "<<DESCRIPTION_START>>" on its own line
        - End the description section with the exact marker "<<DESCRIPTION_END>>" on its own line
        - For image prompts, place each prompt on a new line with no numbering or bullets
        - Do not include any other text, explanations, or formatting outside these markers
        - ENSURE ALL narration lines are formatted as: Narrator: "narration text here"

        Example format:
        <<EMOTION_START>>excited<<EMOTION_END>>
        <<VIDEO_SCRIPT_START>>
        [INTRO]
        (0:00 - 0:03)
        (Upbeat music starts playing. Text on screen: "Big News This Week!")
        Narrator: "Hey viewers! This week has been amazing! Let's dive in!"
        
        [KEY POINT 1]
        (0:04 - 0:09)
        (Visuals of related content)
        Narrator: "First key point goes here with details!"
        <<VIDEO_SCRIPT_END>>

        <<IMAGE_PROMPTS_START>>
        [First image prompt]
        [Second image prompt]
        [Third image prompt]
        <<IMAGE_PROMPTS_END>>

        <<TITLE_START>>
        Breaking News: The Most Shocking Updates You Need to Know!
        <<TITLE_END>>

        <<DESCRIPTION_START>>
        Get the latest updates on this breaking story. Don't miss these crucial details everyone's talking about! #BreakingNews #Update #MustWatch #Viral #TrendingNow
        <<DESCRIPTION_END>>
        """
        
        try:
            # Call Groq API
            response = self.groq_client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=4096,
                top_p=0.9,
            )
            
            # Extract the response content
            content = response.choices[0].message.content
            print("THE OVERALL ACTUAL RESPONSE")
            print(content)
            
            # Parse emotion, script, image prompts, title and description
            script_section = ""
            image_prompts = []
            emotion = "neutral"  # Default emotion if none found
            title = ""
            description = ""
            
            # Extract emotion using markers
            if "<<EMOTION_START>>" in content and "<<EMOTION_END>>" in content:
                emotion = content.split("<<EMOTION_START>>")[1].split("<<EMOTION_END>>")[0].strip().lower()
            else:
                # Fallback emotion extraction
                emotion_prefixes = ["Emotion:", "EMOTION:", "Emotional tone:", "Tone:"]
                for line in content.split('\n'):
                    for prefix in emotion_prefixes:
                        if prefix in line:
                            potential_emotion = line.split(prefix, 1)[1].strip().lower()
                            # Remove quotes if present
                            potential_emotion = potential_emotion.strip('"\'')
                            if potential_emotion in ["happy", "sad", "excited", "calm", "angry", "whisper", "nervous"]:
                                emotion = potential_emotion
                                break
            
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
                                
            # Extract title
            if "<<TITLE_START>>" in content and "<<TITLE_END>>" in content:
                title = content.split("<<TITLE_START>>")[1].split("<<TITLE_END>>")[0].strip()
            else:
                self.logger.warning("Title markers not found in response - attempting to extract title from content")
                title_prefixes = ["Title:", "VIDEO TITLE:", "YouTube Title:"]
                for line in content.split('\n'):
                    for prefix in title_prefixes:
                        if prefix in line:
                            title = line.split(prefix, 1)[1].strip()
                            # Remove quotes if present
                            title = title.strip('"\'')
                            break
                            
            # Extract description
            if "<<DESCRIPTION_START>>" in content and "<<DESCRIPTION_END>>" in content:
                description = content.split("<<DESCRIPTION_START>>")[1].split("<<DESCRIPTION_END>>")[0].strip()
            else:
                self.logger.warning("Description markers not found in response - attempting to extract description from content")
                desc_prefixes = ["Description:", "VIDEO DESCRIPTION:", "YouTube Description:"]
                for line in content.split('\n'):
                    for prefix in desc_prefixes:
                        if prefix in line:
                            description = line.split(prefix, 1)[1].strip()
                            # Remove quotes if present
                            description = description.strip('"\'')
                            break
            
            # Check if the script has proper narrator formatting
            # Look for lines with "Narrator:" format
            has_narrator_format = False
            for line in script_section.split('\n'):
                if 'Narrator:' in line and '"' in line:
                    has_narrator_format = True
                    break
            
            # If no proper narrator format is found, try to fix it
            if not has_narrator_format:
                self.logger.warning("Narrator format not found in script - attempting to standardize format")
                fixed_script_lines = []
                for line in script_section.split('\n'):
                    # Skip section headers and timing/direction notes (in parentheses)
                    if (line.startswith('[') and line.endswith(']')) or line.startswith('(') or not line.strip():
                        fixed_script_lines.append(line)
                    # If it doesn't have a special format and doesn't already start with "Narrator:",
                    # it might be dialogue that needs the narrator tag
                    elif not line.startswith('Narrator:') and line.strip() and not all(c in '()[]{}' for c in line.strip()):
                        # If line already has quotes, format properly
                        if '"' in line:
                            # Extract the content between quotes
                            quote_parts = line.split('"')
                            if len(quote_parts) >= 3:
                                dialogue = quote_parts[1]
                                fixed_script_lines.append(f'Narrator: "{dialogue}"')
                            else:
                                fixed_script_lines.append(f'Narrator: "{line.strip()}"')
                        else:
                            fixed_script_lines.append(f'Narrator: "{line.strip()}"')
                    else:
                        fixed_script_lines.append(line)
                
                script_section = '\n'.join(fixed_script_lines)
            
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
            
            # Verify we can extract narration text properly
            test_narration = ""
            for line in script_section.split('\n'):
                if line.startswith('Narrator: "'):
                    # Extract the content between quotes
                    try:
                        extracted_text = line.split('Narrator: "', 1)[1].rsplit('"', 1)[0]
                        test_narration += extracted_text + " "  # Add space between segments
                    except IndexError:
                        self.logger.warning(f"Could not parse narrator line: {line}")

            if not test_narration and script_section:
                self.logger.warning("Could not extract narrator text properly - script format may be inconsistent")
            
            self.logger.info(f"Generated script ({len(script_section)} chars), {len(image_prompts)} image prompts, and emotion: {emotion}")
            self.logger.info(f"Successfully extracted {len(test_narration.split())} words of narration text")
            self.logger.info(f"Generated title: {title}")
            self.logger.info(f"Generated description with hashtags: {description}")
            
            return script_section, image_prompts, emotion, title, description
            
        except Exception as e:
            self.logger.error(f"Error generating script: {e}")
            return "Error generating script.", ["Generic news image"], "neutral", "Error generating title", "Error generating description"