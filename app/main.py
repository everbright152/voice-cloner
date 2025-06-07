"""
Main application file for the Voice Cloning Web App.

This module initializes the Gradio interface for voice upload and training.
"""
import os
import time
import uuid
import json
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

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

# Training job status storage (in-memory for demo)
# In production, this would be a database
TRAINING_JOBS = {}

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


def get_file_size(file_path):
    """Get file size with robust error handling for cross-platform compatibility.
    
    Args:
        file_path: Path to the file
        
    Returns:
        tuple: (success, size_mb or error_message)
    """
    try:
        if file_path is None:
            return False, "No file selected"
            
        # Handle different path formats from different platforms
        if isinstance(file_path, list) and len(file_path) > 0:
            # Some platforms may return a list with [path, sample_rate]
            file_path = file_path[0]
            
        # Ensure path is a string
        if not isinstance(file_path, (str, Path)):
            return False, f"Invalid file path type: {type(file_path)}"
            
        # Check if file exists
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
            
        # Get file size
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        
        return True, size_mb
    except Exception as e:
        logger.error(f"Error getting file size: {e}")
        return False, f"Error checking file size: {str(e)}"


# Global variable to track the latest job status for UI updates
# This ensures status is available even if browser events fail
LATEST_JOB_STATUS = {}


def simulate_training_progress(job_id):
    """Simulate training progress for demo purposes.
    
    In a real implementation, this would poll the actual API.
    
    Args:
        job_id: ID of the training job
    """
    global LATEST_JOB_STATUS
    
    # Initialize job status
    job_status = {
        "status": "pending",
        "progress": 0,
        "message": "Initializing training...",
        "start_time": time.time(),
        "elapsed_time": 0
    }
    
    TRAINING_JOBS[job_id] = job_status
    LATEST_JOB_STATUS[job_id] = job_status
    
    # Simulate training progress
    total_steps = 10
    for step in range(1, total_steps + 1):
        # Sleep to simulate processing time
        time.sleep(3)
        
        # Update job status
        progress = step / total_steps * 100
        elapsed_time = time.time() - job_status["start_time"]
        
        job_status = {
            "status": "processing" if step < total_steps else "completed",
            "progress": progress,
            "message": f"Processing step {step}/{total_steps}" if step < total_steps else "Training completed",
            "start_time": TRAINING_JOBS[job_id]["start_time"],
            "elapsed_time": elapsed_time
        }
        
        # Update both storage locations
        TRAINING_JOBS[job_id] = job_status
        LATEST_JOB_STATUS[job_id] = job_status
        
        logger.info(f"Updated job {job_id}: {job_status}")
        
        # If training is completed, break
        if step == total_steps:
            break


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
        # Check file size with robust error handling
        success, result = get_file_size(audio_file)
        if not success:
            return f"Error: {result}", None
            
        file_size_mb = result
        if file_size_mb > MAX_UPLOAD_SIZE_MB:
            return f"File too large: {file_size_mb:.1f}MB (max {MAX_UPLOAD_SIZE_MB}MB)", None
        
        # Save uploaded audio to our directory
        file_path = save_uploaded_audio(audio_file)
        if not file_path:
            return "Failed to save audio file", None
        
        # Generate a job ID
        job_id = str(uuid.uuid4())
        
        # Start training in a background thread
        # In a real implementation, this would call the actual API
        thread = threading.Thread(
            target=simulate_training_progress,
            args=(job_id,),
            daemon=True
        )
        thread.start()
        
        # Wait a moment to ensure the job is initialized
        time.sleep(0.5)
        
        return f"Voice training started. Progress will update automatically.", job_id
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
        # First check the global latest status
        if job_id in LATEST_JOB_STATUS:
            job = LATEST_JOB_STATUS[job_id]
        # Fall back to the main storage
        elif job_id in TRAINING_JOBS:
            job = TRAINING_JOBS[job_id]
        else:
            return "Job not found. It may have expired or been removed."
        
        # Calculate elapsed time if not provided
        elapsed_time = job.get("elapsed_time", time.time() - job["start_time"])
        
        # Format status message
        if job["status"] == "completed":
            return f"✅ Training completed in {elapsed_time:.1f} seconds"
        else:
            return f"⏳ Status: {job['status']} | Progress: {job['progress']:.1f}% | Time: {elapsed_time:.1f}s | {job['message']}"
    except Exception as e:
        logger.error(f"Error in check_training_status: {e}")
        return f"Error checking status: {str(e)}"


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


def update_upload_progress(audio_file, name):
    """Update upload progress with robust error handling for cross-platform compatibility.
    
    Args:
        audio_file: Uploaded audio file path
        name: Voice name (not used, but required for Gradio)
        
    Returns:
        str: Progress message
    """
    if audio_file is None:
        return "No file selected"
        
    # Get file size with robust error handling
    success, result = get_file_size(audio_file)
    if not success:
        return str(result)
        
    file_size_mb = result
    return f"File size: {file_size_mb:.2f}MB / {MAX_UPLOAD_SIZE_MB}MB"


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
                    # Add a visual progress bar
                    progress_bar = gr.Slider(
                        label="Training Progress",
                        minimum=0,
                        maximum=100,
                        value=0,
                        interactive=False
                    )
                    
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
        audio_input.change(
            fn=update_upload_progress,
            inputs=[audio_input, voice_name],
            outputs=[upload_progress]
        )
        
        # Function to update both status text and progress bar
        def update_training_display(job_id):
            if not job_id:
                return 0, "No job ID provided"
                
            try:
                # Get status message
                status_message = check_training_status(job_id)
                
                # Get progress percentage for the progress bar
                progress = 0
                if job_id in LATEST_JOB_STATUS:
                    progress = LATEST_JOB_STATUS[job_id].get("progress", 0)
                elif job_id in TRAINING_JOBS:
                    progress = TRAINING_JOBS[job_id].get("progress", 0)
                    
                return progress, status_message
            except Exception as e:
                logger.error(f"Error updating training display: {e}")
                return 0, f"Error: {str(e)}"
        
        train_button.click(
            fn=upload_and_train,
            inputs=[audio_input, voice_name],
            outputs=[training_status, job_id]
        ).then(
            fn=update_training_display,
            inputs=[job_id],
            outputs=[progress_bar, training_status]
        )
        
        check_status_button.click(
            fn=update_training_display,
            inputs=[job_id],
            outputs=[progress_bar, training_status]
        )
        
        # Auto-refresh training status
        app.load(
            fn=lambda: None,  # No-op function
            inputs=None,
            outputs=None,
            _js="""
            function() {
                // Set up interval to refresh status
                let intervalId;
                
                document.addEventListener('DOMContentLoaded', function() {
                    // Find the job_id element by its label
                    const jobIdElements = Array.from(document.querySelectorAll('label')).filter(
                        el => el.textContent.includes('Job ID')
                    );
                    
                    if (jobIdElements.length > 0) {
                        const jobIdContainer = jobIdElements[0].closest('.gradio-container');
                        const jobIdInput = jobIdContainer.querySelector('input');
                        
                        // Find the Check Status button
                        const checkStatusButtons = Array.from(document.querySelectorAll('button')).filter(
                            el => el.textContent.includes('Check Status')
                        );
                        
                        if (checkStatusButtons.length > 0) {
                            const checkStatusButton = checkStatusButtons[0];
                            
                            // Set up interval to click the button every 3 seconds if job_id has a value
                            intervalId = setInterval(function() {
                                if (jobIdInput && jobIdInput.value) {
                                    checkStatusButton.click();
                                }
                            }, 3000);
                        }
                    }
                });
                
                // Clean up interval when component is unloaded
                return () => {
                    if (intervalId) {
                        clearInterval(intervalId);
                    }
                };
            }
            """
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
