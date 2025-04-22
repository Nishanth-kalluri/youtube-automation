# services/video_editor.py
import os
import time
from moviepy.editor import (
    AudioFileClip, ImageClip, concatenate_videoclips, CompositeAudioClip
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
        if not bg_music_path:
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
            
            # Create video clips from images
            video_clips = []
            for img_path in image_paths:
                img_clip = ImageClip(img_path).set_duration(duration_per_image)
                # Set the size uniformly
                img_clip = img_clip.resize(width=1920)
                video_clips.append(img_clip)
            
            # Concatenate video clips
            final_clip = concatenate_videoclips(video_clips, method="compose")
            
            # Add audio (narration and optional background music)
            if os.path.exists(bg_music_path):
                self.logger.info(f"Adding background music from {bg_music_path}")
                bg_music = AudioFileClip(bg_music_path).volumex(0.1)  # Lower volume
                
                # Loop the background music if needed
                if bg_music.duration < audio_duration:
                    bg_music = bg_music.loop(duration=audio_duration)
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
            
            self.logger.info(f"Video created successfully: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error creating video: {e}")
            raise