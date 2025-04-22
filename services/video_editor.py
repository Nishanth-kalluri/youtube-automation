import os
import time
import random
from moviepy.editor import (
    AudioFileClip, ImageClip, concatenate_videoclips, CompositeAudioClip,
    vfx, transfx
)
from config import settings
from utils.logger import Logger

class VideoEditor:
    def __init__(self):
        self.logger = Logger(__name__)
    
    def create_video(self, audio_path, image_paths, bg_music_path=None):
        """
        Create a video from audio and images
        
        Args:
            audio_path (str): Path to the audio file
            image_paths (list): List of paths to image files
            bg_music_path (str, optional): Path to background music file
            
        Returns:
            str: Path to the generated video file
        """
        if not bg_music_path or not os.path.exists(bg_music_path):
            self.logger.info("Using default background music")
            bg_music_path = settings.BG_MUSIC_PATH
        
        self.logger.info(f"Creating video from {len(image_paths)} images and audio")
        
        try:
            # Generate output filename
            timestamp = int(time.time())
            output_path = os.path.join(settings.VIDEOS_DIR, f"video_{timestamp}.mp4")
            
            # Load audio clip
            audio_clip = AudioFileClip(audio_path)
            audio_duration = audio_clip.duration
            
            # Calculate duration for each image (evenly distributed)
            image_count = len(image_paths)
            duration_per_image = audio_duration / image_count
            
            self.logger.info(f"Audio duration: {audio_duration:.2f}s, Duration per image: {duration_per_image:.2f}s")
            
            # Create video clips from images with slideshow effects
            video_clips = []
            for img_path in image_paths:
                # Apply a random slideshow effect to each image
                img_clip = self._create_animated_clip(img_path, duration_per_image)
                video_clips.append(img_clip)
            
            # Concatenate video clips
            final_clip = concatenate_videoclips(video_clips, method="compose")
            
            # Add audio (narration and background music)
            if os.path.exists(bg_music_path):
                self.logger.info(f"Adding background music from {bg_music_path}")
                bg_music = AudioFileClip(bg_music_path).volumex(0.2)  # Set volume to 20%
                
                # Loop the background music if needed
                if bg_music.duration < audio_duration:
                    bg_music = bg_music.audio_loop(duration=audio_duration)
                else:
                    bg_music = bg_music.subclip(0, audio_duration)
                
                # Combine audio tracks
                final_audio = CompositeAudioClip([audio_clip, bg_music])
                final_clip = final_clip.set_audio(final_audio)
            else:
                self.logger.info("No background music added")
                final_clip = final_clip.set_audio(audio_clip)
            
            # Write the result to a file
            self.logger.info(f"Writing video to {output_path}")
            final_clip.write_videofile(
                output_path, 
                codec='libx264', 
                audio_codec='aac', 
                fps=24,
                logger=None  # Disable moviepy's logger
            )
            
            # Close clips to free memory
            final_clip.close()
            audio_clip.close()
            if os.path.exists(bg_music_path):
                bg_music.close()
            
            self.logger.info(f"Video created successfully: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error creating video: {e}")
            raise
    
    def _create_animated_clip(self, img_path, duration):
        """
        Create an animated clip from a single image with zoom and pan effects
        
        Args:
            img_path (str): Path to the image file
            duration (float): Duration of the clip in seconds
            
        Returns:
            ImageClip: Animated image clip
        """
        # Load the image and resize for consistency
        img_clip = ImageClip(img_path)
        img_clip = img_clip.resize(width=1920)
        
        # Choose a random effect for the image
        effect_type = random.choice(['zoom', 'pan', 'zoom_out', 'pan_zoom'])
        
        if effect_type == 'zoom':
            # Gradual zoom in effect
            zoom_factor = random.uniform(1.05, 1.2)
            img_clip = img_clip.resize(lambda t: 1 + (zoom_factor - 1) * t / duration)
            img_clip = img_clip.set_position(('center', 'center')).set_duration(duration)
            
        elif effect_type == 'zoom_out':
            # Zoom out effect
            zoom_factor = random.uniform(1.1, 1.3)
            img_clip = img_clip.resize(lambda t: zoom_factor - (zoom_factor - 1) * t / duration)
            img_clip = img_clip.set_position(('center', 'center')).set_duration(duration)
            
        elif effect_type == 'pan':
            # Pan effect (left to right, right to left, top to bottom, or bottom to top)
            direction = random.choice(['left_to_right', 'right_to_left', 'top_to_bottom', 'bottom_to_top'])
            
            # Resize image slightly larger for better panning effect
            img_clip = img_clip.resize(width=2200)
            
            if direction == 'left_to_right':
                position_func = lambda t: ('left' if t == 0 else 'right' if t == duration else -200 + 400 * t / duration, 'center')
            elif direction == 'right_to_left':
                position_func = lambda t: ('right' if t == 0 else 'left' if t == duration else 200 - 400 * t / duration, 'center')
            elif direction == 'top_to_bottom':
                position_func = lambda t: ('center', 'top' if t == 0 else 'bottom' if t == duration else -100 + 200 * t / duration)
            else:  # bottom_to_top
                position_func = lambda t: ('center', 'bottom' if t == 0 else 'top' if t == duration else 100 - 200 * t / duration)
                
            img_clip = img_clip.set_position(position_func).set_duration(duration)
            
        else:  # pan_zoom combination
            # Combine zoom and pan for more dynamic effect
            zoom_factor = random.uniform(1.05, 1.15)
            position_x = random.choice([-100, 100])
            position_y = random.choice([-50, 50])
            
            img_clip = img_clip.resize(lambda t: 1 + (zoom_factor - 1) * t / duration)
            img_clip = img_clip.set_position(
                lambda t: ('center' if t == 0 else position_x * t / duration, 
                          'center' if t == 0 else position_y * t / duration)
            ).set_duration(duration)
        
        return img_clip