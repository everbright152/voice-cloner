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

# Initialize Chatterbox client
client = ChatterboxClient()

# Mock user ID for demo (would be replaced with actual user authentication)
DEMO_USER_ID = "demo_user"


def save_uploaded_audio(audio_file) -> str:
    """Save uploaded audio file and return the file path.
    
    Args:
        audio_file: Uploaded audio file
        
    Returns:
        str: Path to saved audio file
    """
    if audio_file is None:
        return None
    
    # Generate unique filename
    filename = f"{uuid.uuid4()}.wav"
    file_path = UPLOAD_DIR / filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(audio_file)
    
    return str(file_path)


def upload_and_train(audio_file, voice_name: str) -> Tuple[str, str]:
    """Upload audio file and start voice training.
    
    Args:
        audio_file: Uploaded audio file
        voice_name: Name for the voice
        
    Returns:
        Tuple[str, str]: Status message and job ID
    """
    if audio_file is None:
        return "No audio file provided", None
    
    if not voice_name:
        return "Voice name is required", None
    
    try:
        # Save uploaded audio
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
        
        # Simulate audio file creation (would be actual TTS result)
        with open(output_file, "wb") as f:
            f.write(b"RIFF....WAV...")  # Dummy WAV header
        
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
                    audio_input = gr.Audio(
                        label="Upload Audio Sample (min 10 minutes recommended)",
                        type="filepath"
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
                        interactive=False
                    )
        
        # Set up event handlers
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
