"""
Main application file for the Voice Cloning Web App.

This module initializes the Gradio interface for voice upload and training.
"""
import os
import time
import uuid
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import gradio as gr
from dotenv import load_dotenv

from app.services.chatterbox.client import ChatterboxClient
from app.services.chatterbox.models import TTSRequest, EmotionLevel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Constants
UPLOAD_DIR = Path("app/static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_UPLOAD_SIZE_MB = 100  # Maximum upload size in MB

# Initialize Chatterbox client
client = ChatterboxClient()

# Mock user ID for demo (would be replaced with actual user authentication)
DEMO_USER_ID = "demo_user"


def save_uploaded_audio(audio_file) -> str:
    """Save uploaded audio file and return the file path.
    
    Args:
        audio_file: Uploaded audio file path from Gradio
        
    Returns:
        str: Path to saved audio file
    """
    if audio_file is None:
        return None
    
    try:
        # Generate unique filename
        filename = f"{uuid.uuid4()}.wav"
        file_path = UPLOAD_DIR / filename
        
        # Since Gradio's Audio with type="filepath" returns a path string,
        # we need to read the file and then write it to our destination
        with open(audio_file, "rb") as src_file:
            audio_data = src_file.read()
            
        # Save file to our uploads directory
        with open(file_path, "wb") as dest_file:
            dest_file.write(audio_data)
        
        return str(file_path)
    except Exception as e:
        logger.error(f"Error saving audio file: {e}")
        return None


def upload_and_train(audio_file, voice_name: str) -> Tuple[str, str]:
    """Upload audio file and start voice training.
    
    Args:
        audio_file: Uploaded audio file path
        voice_name: Name for the voice
        
    Returns:
        Tuple[str, str]: Status message and job ID
    """
    if audio_file is None:
        return "No audio file provided", None
    
    if not voice_name:
        return "Voice name is required", None
    
    try:
        # Check if file exists
        if not os.path.exists(audio_file):
            return f"Audio file not found: {audio_file}", None
            
        # Check file size
        file_size_mb = os.path.getsize(audio_file) / (1024 * 1024)
        if file_size_mb > MAX_UPLOAD_SIZE_MB:
            return f"File too large: {file_size_mb:.1f}MB (max {MAX_UPLOAD_SIZE_MB}MB)", None
        
        # Save uploaded audio to our directory
        file_path = save_uploaded_audio(audio_file)
        if not file_path:
            return "Failed to save audio file", None
        
        # Upload to Chatterbox
        # In a real implementation, this would call the actual API
        # For now, we'll simulate the response
        job_id = str(uuid.uuid4())
        
        return f"Voice training started with job ID: {job_id}", job_id
    except Exception as e:
        logger.error(f"Error in upload_and_train: {e}")
        return f"Error: {str(e)}", None


def check_training_status(job_id: str) -> str:
    """Check status of voice training job.
    
    Args:
        job_id: ID of the training job
        
    Returns:
        str: Status message
    """
    if not job_id:
        return "No job ID provided"
    
    try:
        # In a real implementation, this would call the actual API
        # For now, we'll simulate the response
        statuses = ["pending", "processing", "completed"]
        # Simulate progress based on time
        status = statuses[int(time.time() % 3)]
        
        return f"Job status: {status}"
    except Exception as e:
        logger.error(f"Error in check_training_status: {e}")
        return f"Error: {str(e)}"


def generate_speech(text: str, voice_id: str, emotion: float) -> Tuple[str, Optional[str]]:
    """Generate speech from text using a trained voice.
    
    Args:
        text: Text to convert to speech
        voice_id: ID of the voice to use
        emotion: Emotion level (0.0-1.5)
        
    Returns:
        Tuple[str, Optional[str]]: Status message and path to audio file
    """
    if not text:
        return "No text provided", None
    
    if not voice_id:
        return "No voice selected", None
    
    try:
        # In a real implementation, this would call the actual API
        # For now, we'll simulate the response
        output_file = UPLOAD_DIR / f"{uuid.uuid4()}.wav"
        
        # Create a simple WAV file for testing playback
        # This creates a 1-second silent WAV file
        with open(output_file, "wb") as f:
            # Simple WAV header for a silent 1-second file
            # RIFF header
            f.write(b'RIFF')
            f.write((36).to_bytes(4, byteorder='little'))  # File size - 8
            f.write(b'WAVE')
            
            # Format chunk
            f.write(b'fmt ')
            f.write((16).to_bytes(4, byteorder='little'))  # Chunk size
            f.write((1).to_bytes(2, byteorder='little'))   # PCM format
            f.write((1).to_bytes(2, byteorder='little'))   # Mono
            f.write((44100).to_bytes(4, byteorder='little'))  # Sample rate
            f.write((44100 * 2).to_bytes(4, byteorder='little'))  # Byte rate
            f.write((2).to_bytes(2, byteorder='little'))   # Block align
            f.write((16).to_bytes(2, byteorder='little'))  # Bits per sample
            
            # Data chunk
            f.write(b'data')
            f.write((44100 * 2).to_bytes(4, byteorder='little'))  # Chunk size
            
            # 1 second of silence (16-bit samples)
            for _ in range(44100):
                f.write((0).to_bytes(2, byteorder='little'))
        
        return "Speech generated successfully", str(output_file)
    except Exception as e:
        logger.error(f"Error in generate_speech: {e}")
        return f"Error: {str(e)}", None


def list_available_voices() -> List[str]:
    """List available trained voices.
    
    Returns:
        List[str]: List of voice IDs
    """
    try:
        # In a real implementation, this would call the actual API
        # For now, we'll return mock data
        return ["voice_1", "voice_2", "voice_3"]
    except Exception as e:
        logger.error(f"Error in list_available_voices: {e}")
        return []


def create_ui():
    """Create and launch the Gradio UI."""
    with gr.Blocks(title="Voice Cloning App", theme=gr.themes.Base()) as app:
        gr.Markdown("# Voice Cloning Web Application")
        gr.Markdown("Upload audio samples and generate text-to-speech with cloned voices.")
        
        with gr.Tab("Voice Training"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown(f"**Maximum upload size: {MAX_UPLOAD_SIZE_MB}MB**")
                    audio_input = gr.Audio(
                        label="Upload Audio Sample (min 10 minutes recommended)",
                        type="filepath",
                        format="wav"
                    )
                    voice_name = gr.Textbox(
                        label="Voice Name",
                        placeholder="Enter a name for this voice"
                    )
                    train_button = gr.Button("Start Training", variant="primary")
                
                with gr.Column():
                    training_status = gr.Textbox(
                        label="Training Status",
                        placeholder="Training status will appear here",
                        interactive=False
                    )
                    job_id = gr.Textbox(
                        label="Job ID",
                        visible=False
                    )
                    check_status_button = gr.Button("Check Status")
                    
                    # Add upload progress indicator
                    upload_progress = gr.Textbox(
                        label="Upload Progress",
                        placeholder="No upload in progress",
                        interactive=False
                    )
        
        with gr.Tab("Text-to-Speech"):
            with gr.Row():
                with gr.Column():
                    voice_dropdown = gr.Dropdown(
                        label="Select Voice",
                        choices=list_available_voices(),
                        interactive=True
                    )
                    emotion_slider = gr.Slider(
                        label="Emotion Level",
                        minimum=0.0,
                        maximum=1.5,
                        step=0.1,
                        value=0.0
                    )
                    text_input = gr.Textbox(
                        label="Text to Convert",
                        placeholder="Enter text to convert to speech",
                        lines=5
                    )
                    generate_button = gr.Button("Generate Speech", variant="primary")
                
                with gr.Column():
                    tts_status = gr.Textbox(
                        label="Status",
                        placeholder="Generation status will appear here",
                        interactive=False
                    )
                    audio_output = gr.Audio(
                        label="Generated Speech",
                        interactive=False,
                        format="wav"
                    )
        
        # Set up event handlers
        def update_upload_progress(audio_file, name):
            if audio_file is None:
                return "No file selected"
            try:
                file_size_mb = os.path.getsize(audio_file) / (1024 * 1024)
                return f"File size: {file_size_mb:.2f}MB / {MAX_UPLOAD_SIZE_MB}MB"
            except:
                return "Error checking file size"
        
        audio_input.change(
            fn=update_upload_progress,
            inputs=[audio_input, voice_name],
            outputs=[upload_progress]
        )
        
        train_button.click(
            fn=upload_and_train,
            inputs=[audio_input, voice_name],
            outputs=[training_status, job_id]
        )
        
        check_status_button.click(
            fn=check_training_status,
            inputs=[job_id],
            outputs=[training_status]
        )
        
        generate_button.click(
            fn=generate_speech,
            inputs=[text_input, voice_dropdown, emotion_slider],
            outputs=[tts_status, audio_output]
        )
        
        # Refresh voice list button
        refresh_button = gr.Button("Refresh Voice List")
        refresh_button.click(
            fn=list_available_voices,
            inputs=[],
            outputs=[voice_dropdown]
        )
    
    return app


def main():
    """Main entry point."""
    app = create_ui()
    app.launch(server_name="0.0.0.0")


if __name__ == "__main__":
    main()
