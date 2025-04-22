from pydub import AudioSegment
import os

def trim_audio(input_path, output_path, target_duration_ms=60000):
    """
    Trim an audio file to the specified duration.
    
    Args:
        input_path (str): Path to the input audio file
        output_path (str): Path to save the trimmed audio file
        target_duration_ms (int): Target duration in milliseconds (default: 60000ms = 1 minute)
    """
    try:
        # Load the audio file
        print(f"Loading audio file: {input_path}")
        audio = AudioSegment.from_file(input_path)
        
        # Get the original duration
        original_duration_sec = len(audio) / 1000
        print(f"Original duration: {original_duration_sec:.2f} seconds")
        
        # Trim to target duration
        trimmed_audio = audio[:target_duration_ms]
        
        # Save the trimmed audio
        print(f"Saving trimmed audio to: {output_path}")
        trimmed_audio.export(output_path, format=os.path.splitext(output_path)[1][1:])
        
        print(f"Successfully trimmed audio to {target_duration_ms/1000:.2f} seconds")
        
    except Exception as e:
        print(f"Error processing audio: {e}")

if __name__ == "__main__":
    # Input and output file paths
    input_file = r"C:\Users\the_b\Downloads\relaxing-music-vol1-124477.mp3"
    output_file = r"C:\Users\the_b\Downloads\relaxing-music-vol1-trimmed-1min.mp3"
    
    # Trim the audio to 1 minute (60,000 milliseconds)
    trim_audio(input_file, output_file)