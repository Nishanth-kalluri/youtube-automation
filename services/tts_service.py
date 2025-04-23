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
    
    def generate_audio(self, script, emotion=None, voice_name="en-US-Wavenet-D", output_filename=None):
        """
        Generate audio from script text using Google TTS with emotional expression
        
        Args:
            script (str): The script text to convert to speech
            emotion (str, optional): Emotion to apply (e.g., 'happy', 'sad', 'excited')
            voice_name (str, optional): The voice to use for synthesis
            output_filename (str, optional): Output file path. If None, a default path is generated.
            
        Returns:
            str: Path to the generated audio file
        """
        if not output_filename:
            # Generate a default filename based on timestamp
            import time
            timestamp = int(time.time())
            output_filename = os.path.join(settings.AUDIO_DIR, f"audio_{timestamp}.mp3")
        
        self.logger.info(f"Generating audio from script ({len(script)} chars), emotion: {emotion}")
        
        try:
            # Create synthesis input based on whether SSML is already included
            if script.strip().startswith('<speak>'):
                synthesis_input = texttospeech.SynthesisInput(ssml=script)
            else:
                # Apply emotion formatting if specified
                if emotion:
                    ssml_script = self._apply_emotion_to_ssml(script, emotion)
                    synthesis_input = texttospeech.SynthesisInput(ssml=ssml_script)
                else:
                    synthesis_input = texttospeech.SynthesisInput(text=script)
            
            # Build the voice request
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US", 
                name=voice_name
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

    def _apply_emotion_to_ssml(self, text, emotion):
        """
        Apply emotional styling to text using SSML
        
        Args:
            text (str): Plain text to convert
            emotion (str): Emotion to apply
            
        Returns:
            str: SSML formatted text with emotion applied
        """
        # Define emotion settings based on prosody attributes
        emotion_settings = {
            'happy': {
                'rate': '1.1', 
                'pitch': '+1.5st', 
                'volume': 'loud'
            },
            'sad': {
                'rate': '0.9',
                'pitch': '-2st',
                'volume': 'soft'
            },
            'excited': {
                'rate': '1.3',
                'pitch': '+3st',
                'volume': 'x-loud'
            },
            'calm': {
                'rate': '0.8',
                'pitch': '-0.5st',
                'volume': 'medium'
            },
            'angry': {
                'rate': '1.2',
                'pitch': '-1st',
                'volume': 'loud'
            },
            'whisper': {
                'rate': '0.95',
                'pitch': '-1st',
                'volume': 'x-soft'
            },
            'nervous': {
                'rate': '1.1',
                'pitch': '+0.8st',
                'volume': 'medium'
            }
        }
        
        # Get settings for the requested emotion or use default
        settings = emotion_settings.get(emotion.lower(), {})
        
        # Create SSML with prosody tag
        if settings:
            rate = settings.get('rate', '1.0')
            pitch = settings.get('pitch', '+0st')
            volume = settings.get('volume', 'medium')
            
            ssml = f"""<speak>
                <prosody rate="{rate}" pitch="{pitch}" volume="{volume}">
                    {text}
                </prosody>
            </speak>"""
        else:
            # If emotion not recognized, just wrap in speak tags
            ssml = f"<speak>{text}</speak>"
            
        return ssml
    
    def create_expressive_ssml(self, script, expressions=None):
        """
        Create SSML with advanced expression controls
        
        Args:
            script (str): The base script text
            expressions (list): List of dicts with start/end indexes and expression types
            
        Returns:
            str: Fully formatted SSML string
        """
        if not expressions:
            return f"<speak>{script}</speak>"
            
        # Start with opening speak tag
        ssml = "<speak>"
        last_end = 0
        
        # Apply expressions where specified
        for expr in sorted(expressions, key=lambda x: x['start']):
            start = expr['start']
            end = expr['end']
            expr_type = expr['type']
            
            # Add text before this expression
            ssml += script[last_end:start]
            
            # Apply the expression
            text_segment = script[start:end]
            if expr_type == 'emphasis':
                level = expr.get('level', 'moderate')
                ssml += f'<emphasis level="{level}">{text_segment}</emphasis>'
            elif expr_type == 'break':
                duration = expr.get('duration', 500)
                ssml += f'{text_segment}<break time="{duration}ms"/>'
            elif expr_type == 'emotion':
                emotion = expr.get('emotion', 'neutral')
                emotion_settings = self._get_emotion_settings(emotion)
                ssml += f'<prosody rate="{emotion_settings["rate"]}" pitch="{emotion_settings["pitch"]}" volume="{emotion_settings["volume"]}">{text_segment}</prosody>'
            elif expr_type == 'character':
                char_type = expr.get('character_type', 'robot')
                ssml += f'<say-as interpret-as="character" character-type="{char_type}">{text_segment}</say-as>'
            else:
                # If no recognized expression, just add the text
                ssml += text_segment
                
            last_end = end
            
        # Add any remaining text
        ssml += script[last_end:]
        
        # Close the speak tag
        ssml += "</speak>"
        return ssml
    
    def _get_emotion_settings(self, emotion):
        """Get prosody settings for a specific emotion"""
        emotion_settings = {
            'happy': {'rate': '1.1', 'pitch': '+1.5st', 'volume': 'loud'},
            'sad': {'rate': '0.9', 'pitch': '-2st', 'volume': 'soft'},
            'excited': {'rate': '1.3', 'pitch': '+3st', 'volume': 'x-loud'},
            'calm': {'rate': '0.8', 'pitch': '-0.5st', 'volume': 'medium'},
            'angry': {'rate': '1.2', 'pitch': '-1st', 'volume': 'loud'},
            'whisper': {'rate': '0.95', 'pitch': '-1st', 'volume': 'x-soft'},
            'nervous': {'rate': '1.1', 'pitch': '+0.8st', 'volume': 'medium'}
        }
        return emotion_settings.get(emotion.lower(), {'rate': '1.0', 'pitch': '+0st', 'volume': 'medium'})