# services/image_generator.py
import os
import time
import requests
import re
from config import settings
from utils.logger import Logger

class ImageGenerator:
    def __init__(self):
        self.logger = Logger(__name__)
        self.width = 1024
        self.height = 1024
        self.model = 'flux'  # Default model
    
    def _sanitize_prompt(self, prompt):
        """Clean prompt for use in URL and filename"""
        # Replace special characters with underscores
        safe_prompt = re.sub(r'[^a-zA-Z0-9\s]', '_', prompt)
        # Limit length and replace spaces with underscores
        return safe_prompt[:50].strip().replace(' ', '_').lower()
    
    def generate_images(self, image_prompts):
        """
        Generate images from prompts using Pollinations.ai
        
        Args:
            image_prompts (list): List of image prompts
            
        Returns:
            list: Paths to the generated image files
        """
        self.logger.info(f"Generating {len(image_prompts)} images")
        image_paths = []
        
        for i, prompt in enumerate(image_prompts):
            try:
                # Create a seed that varies for each prompt
                seed = 42 + i
                
                # Create a filename based on the prompt
                safe_filename = f"{self._sanitize_prompt(prompt)}_{seed}.jpg"
                output_path = os.path.join(settings.IMAGES_DIR, safe_filename)
                
                # Generate the image URL
                image_url = f"https://pollinations.ai/p/{prompt}?width={self.width}&height={self.height}&seed={seed}&model={self.model}"
                
                self.logger.info(f"Downloading image {i+1}/{len(image_prompts)}: {prompt[:30]}...")
                
                # Download the image
                response = requests.get(image_url)
                
                if response.status_code == 200:
                    # Write the content to file
                    with open(output_path, 'wb') as file:
                        file.write(response.content)
                    
                    self.logger.info(f"Downloaded image to {output_path}")
                    image_paths.append(output_path)
                else:
                    self.logger.error(f"Failed to download image. Status code: {response.status_code}")
                    # Use placeholder image
                    image_paths.append(settings.PLACEHOLDER_IMAGE_PATH)
                
                # Add a small delay to avoid overwhelming the service
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error generating image for prompt '{prompt[:30]}...': {e}")
                # Use placeholder image on error
                image_paths.append(settings.PLACEHOLDER_IMAGE_PATH)
        
        return image_paths