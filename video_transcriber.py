import os
import tempfile
import yt_dlp
import json
import logging
from typing import Dict, Any

try:
    import whisper
except ImportError:
    whisper = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class VideoTranscriber:
    def __init__(self, model_size: str = "base"):
        """
        Initializes the Whisper model.
        :param model_size: 'tiny', 'base', 'small', 'medium', 'large'
                           'base' is a good balance for backend generation without a GPU.
        """
        if whisper is None:
            logging.warning("Whisper module not found. Video transcription will be disabled.")
            self.model = None
        else:
            logging.info(f"Loading Whisper model '{model_size}'...")
            self.model = whisper.load_model(model_size)
            logging.info("Whisper model loaded successfully.")

    def download_audio(self, video_url: str, output_path: str) -> bool:
        """
        Downloads the lowest-quality audio from the given URL.
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            # We enforce downloading as a standard audio format to avoid weird encodings
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        try:
            logging.info(f"Downloading audio from {video_url}...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            return True
        except Exception as e:
            logging.error(f"Failed to download audio: {e}")
            return False

    def transcribe_video(self, video_url: str) -> Dict[str, Any]:
        """
        Downloads the video audio to a temporary file, transcribes it, and cleans up.
        """
        result = {
            "video_url": video_url,
            "transcript": None,
            "language": None,
            "error": None
        }

        # Create a temporary directory to store the audio
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_audio_path = os.path.join(temp_dir, "audio")
            
            # Download audio
            success = self.download_audio(video_url, temp_audio_path)
            if not success:
                result["error"] = "Audio download failed. The URL might be invalid or unsupported."
                return result

            # yt-dlp's FFmpeg postprocessor will create "audio.mp3"
            final_audio_path = temp_audio_path + ".mp3"
            
            # Fallback if yt-dlp didn't append .mp3 for some reason
            if not os.path.exists(final_audio_path) and os.path.exists(temp_audio_path):
                final_audio_path = temp_audio_path

            if not os.path.exists(final_audio_path):
                result["error"] = "Audio file was not created successfully."
                return result

            # Transcribe the audio
            if self.model is None:
                result["error"] = "Transcription is disabled on this server."
                return result

            try:
                logging.info(f"Transcribing audio with Whisper...")
                transcription_result = self.model.transcribe(final_audio_path)
                result["transcript"] = transcription_result["text"].strip()
                result["language"] = transcription_result.get("language")
                logging.info(f"Transcription complete.")
            except Exception as e:
                logging.error(f"Failed to transcribe audio: {e}")
                result["error"] = f"Transcription Error: {e}"

        return result

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
        transcriber = VideoTranscriber(model_size="tiny")  # Use tiny for faster testing
        res = transcriber.transcribe_video(test_url)
        print(json.dumps(res, indent=2))
    else:
        print("Usage: python video_transcriber.py <video_url>")
        print("Required system dependency: FFmpeg must be installed and in your PATH.")
