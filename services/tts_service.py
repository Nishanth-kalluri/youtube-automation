# services/tts_service.py
import os
from google.cloud import texttospeech
from google.oauth2 import service_account
from config import settings
from utils.logger import Logger

class TTSService:
    def __init__(self):
        self.logger = Logger(__name__)
        
        try:
            # Load credentials explicitly from the JSON key file
            self.credentials = service_account.Credentials.from_service_account_file(
                settings.GOOGLE_CLOUD_SERVICE_ACCOUNT_PATH
            )
            
            # Instantiate the client
            self.client = texttospeech.TextToSpeechClient(credentials=self.credentials)
            self.logger.info("Successfully initialized Text-to-Speech client")
            
        except FileNotFoundError:
            self.logger.error(f"Service account key file not found at '{settings.GOOGLE_CLOUD_SERVICE_ACCOUNT_PATH}'")
            raise
        except Exception as e:
            self.logger.error(f"Error initializing Text-to-Speech client: {e}")
            raise
    
    def generate_audio(self, script, output_filename=None):
        print("SCRIPT IN GENERATE AUDIO:")
        print(script)
        """
        Generate audio from script text using Google TTS
        
        Args:
            script (str): The script text to convert to speech
            output_filename (str, optional): Output file path. If None, a default path is generated.
            
        Returns:
            str: Path to the generated audio file
        """
        if not output_filename:
            # Generate a default filename based on timestamp
            import time
            timestamp = int(time.time())
            output_filename = os.path.join(settings.AUDIO_DIR, f"audio_{timestamp}.mp3")
        
        self.logger.info(f"Generating audio from script ({len(script)} chars)")
        
        try:
            # Set the text input to be synthesized
            synthesis_input = texttospeech.SynthesisInput(text=script)
            
            # Build the voice request
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US", 
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            
            # Select the type of audio file
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            # Perform the text-to-speech request
            self.logger.info("Calling Google TTS API...")
            response = self.client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_filename), exist_ok=True)
            
            # Write the audio content to file
            with open(output_filename, "wb") as out:
                out.write(response.audio_content)
            
            self.logger.info(f"Audio content written to {output_filename}")
            return output_filename
            
        except Exception as e:
            self.logger.error(f"Error generating audio: {e}")
            raise