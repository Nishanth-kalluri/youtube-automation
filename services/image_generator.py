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
        self.max_retries = 5  # Maximum number of retry attempts
        self.retry_delay = 2  # Seconds to wait between retries
    
    def _sanitize_prompt(self, prompt):
        """Clean prompt for use in URL and filename"""
        # Replace special characters with underscores
        safe_prompt = re.sub(r'[^a-zA-Z0-9\s]', '_', prompt)
        # Limit length and replace spaces with underscores
        return safe_prompt[:50].strip().replace(' ', '_').lower()
    
    def _download_image(self, prompt, seed, attempt=1):
        """
        Download a single image with retry logic
        
        Args:
            prompt (str): The image prompt
            seed (int): The seed for image generation
            attempt (int): Current attempt number
            
        Returns:
            tuple: (success_flag, output_path)
        """
        # Create a filename based on the prompt
        safe_filename = f"{self._sanitize_prompt(prompt)}_{seed}.jpg"
        output_path = os.path.join(settings.IMAGES_DIR, safe_filename)
        
        # Generate the image URL
        image_url = f"https://pollinations.ai/p/{prompt}?width={self.width}&height={self.height}&seed={seed}&model={self.model}"
        
        self.logger.info(f"Downloading image (attempt {attempt}/{self.max_retries}): {prompt[:30]}...")
        
        try:
            # Download the image
            response = requests.get(image_url)
            
            if response.status_code == 200:
                # Write the content to file
                with open(output_path, 'wb') as file:
                    file.write(response.content)
                
                self.logger.info(f"Downloaded image to {output_path}")
                return True, output_path
            else:
                self.logger.warning(f"Failed to download image. Status code: {response.status_code}")
                return False, None
        
        except Exception as e:
            self.logger.warning(f"Error downloading image: {e}")
            return False, None
    
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
            # Create a seed that varies for each prompt
            seed = 42 + i
            
            # Try to download the image with retries
            success = False
            output_path = None
            
            for attempt in range(1, self.max_retries + 1):
                success, output_path = self._download_image(prompt, seed, attempt)
                
                if success:
                    break
                
                if attempt < self.max_retries:
                    retry_wait = self.retry_delay * attempt  # Increasing backoff
                    self.logger.info(f"Retrying in {retry_wait} seconds...")
                    time.sleep(retry_wait)
            
            if success:
                image_paths.append(output_path)
            else:
                self.logger.error(f"Failed to generate image after {self.max_retries} attempts. Using placeholder.")
                image_paths.append(settings.PLACEHOLDER_IMAGE_PATH)
            
            # Add a small delay before processing the next prompt
            time.sleep(1)
        
        return image_paths