"""
Client for interacting with Resemble AI's Chatterbox.

This module provides a client for interacting with the Chatterbox API
for voice training and text-to-speech generation.
"""
import os
import time
import logging
import asyncio
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Union, BinaryIO
import aiohttp
import requests
from pydub import AudioSegment

from app.services.chatterbox.models import (
    TrainingJob,
    VoiceModel,
    VoiceStatus,
    TTSRequest,
    TTSResponse,
    WebhookEvent
)

logger = logging.getLogger(__name__)


class ChatterboxClient:
    """Client for interacting with Resemble AI's Chatterbox."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize the Chatterbox client.
        
        Args:
            api_key: API key for Chatterbox. If not provided, will use local mode.
            base_url: Base URL for Chatterbox API. If not provided, will use default.
        """
        self.api_key = api_key or os.environ.get("CHATTERBOX_API_KEY")
        self.use_local_mode = not self.api_key
        
        if self.use_local_mode:
            logger.info("Chatterbox API key not provided, using local mode")
            # Create directories for local storage if they don't exist
            self.local_storage_dir = Path("app/static/chatterbox_data")
            self.local_storage_dir.mkdir(parents=True, exist_ok=True)
            (self.local_storage_dir / "voices").mkdir(exist_ok=True)
            (self.local_storage_dir / "jobs").mkdir(exist_ok=True)
        else:
            self.base_url = base_url or "https://api.chatterbox.resemble.ai/v1"
        
        self.session = None
    
    async def __aenter__(self):
        """Enter async context manager."""
        if not self.use_local_mode:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager."""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        if self.use_local_mode:
            return {}
        return {"Authorization": f"Bearer {self.api_key}"}
    
    async def upload_audio(self, audio_file: Union[str, BinaryIO], user_id: str, voice_name: str) -> TrainingJob:
        """Upload audio file for voice training.
        
        Args:
            audio_file: Path to audio file or file-like object
            user_id: User ID for the voice
            voice_name: Name for the voice
            
        Returns:
            TrainingJob: Details of the training job
        """
        if self.use_local_mode:
            # Simulate local processing
            job_id = str(uuid.uuid4())
            timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            
            # Save audio file to local storage if it's a path
            if isinstance(audio_file, str):
                audio_file_path = audio_file
            else:
                # If it's a file-like object, save it to a temporary file
                audio_file_path = str(self.local_storage_dir / "voices" / f"{job_id}.wav")
                with open(audio_file_path, "wb") as f:
                    f.write(audio_file.read() if hasattr(audio_file, "read") else audio_file)
            
            # Create a simulated training job
            job = TrainingJob(
                job_id=job_id,
                user_id=user_id,
                voice_name=voice_name,
                status=VoiceStatus.PROCESSING,
                created_at=timestamp,
                updated_at=timestamp,
                audio_file_path=audio_file_path
            )
            
            # Save job details to local storage
            job_file = self.local_storage_dir / "jobs" / f"{job_id}.json"
            with open(job_file, "w") as f:
                f.write(job.json())
            
            # Simulate processing delay
            await asyncio.sleep(0.5)
            
            # Update job status to completed
            job.status = VoiceStatus.COMPLETED
            job.updated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            
            # Save updated job details
            with open(job_file, "w") as f:
                f.write(job.json())
            
            return job
        
        if not self.session:
            raise RuntimeError("Client not initialized. Use as async context manager.")
        
        url = f"{self.base_url}/voices/upload"
        
        # Prepare form data
        form_data = aiohttp.FormData()
        form_data.add_field("user_id", user_id)
        form_data.add_field("name", voice_name)
        
        # Handle file path or file-like object
        if isinstance(audio_file, str):
            with open(audio_file, "rb") as f:
                form_data.add_field("audio_file", f, filename=os.path.basename(audio_file))
        else:
            form_data.add_field("audio_file", audio_file)
        
        # Make request
        async with self.session.post(url, data=form_data) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Failed to upload audio: {error_text}")
            
            data = await response.json()
            return TrainingJob(**data)
    
    async def get_training_status(self, job_id: str) -> TrainingJob:
        """Get status of a voice training job.
        
        Args:
            job_id: ID of the training job
            
        Returns:
            TrainingJob: Updated details of the training job
        """
        if self.use_local_mode:
            # Read job details from local storage
            job_file = self.local_storage_dir / "jobs" / f"{job_id}.json"
            if not job_file.exists():
                raise Exception(f"Job {job_id} not found")
            
            with open(job_file, "r") as f:
                job_data = f.read()
            
            return TrainingJob.parse_raw(job_data)
        
        if not self.session:
            raise RuntimeError("Client not initialized. Use as async context manager.")
        
        url = f"{self.base_url}/jobs/{job_id}"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Failed to get job status: {error_text}")
            
            data = await response.json()
            return TrainingJob(**data)
    
    async def list_voices(self, user_id: Optional[str] = None) -> List[VoiceModel]:
        """List available voices.
        
        Args:
            user_id: Optional user ID to filter voices
            
        Returns:
            List[VoiceModel]: List of available voices
        """
        if self.use_local_mode:
            # Simulate voice listing
            voices = []
            timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            
            # In local mode, just return some mock voices
            mock_voices = [
                {
                    "voice_id": "voice_1",
                    "user_id": user_id or "demo_user",
                    "name": "Default Voice 1",
                    "created_at": timestamp,
                    "status": VoiceStatus.COMPLETED
                },
                {
                    "voice_id": "voice_2",
                    "user_id": user_id or "demo_user",
                    "name": "Default Voice 2",
                    "created_at": timestamp,
                    "status": VoiceStatus.COMPLETED
                },
                {
                    "voice_id": "voice_3",
                    "user_id": user_id or "demo_user",
                    "name": "Default Voice 3",
                    "created_at": timestamp,
                    "status": VoiceStatus.COMPLETED
                }
            ]
            
            return [VoiceModel(**voice) for voice in mock_voices]
        
        if not self.session:
            raise RuntimeError("Client not initialized. Use as async context manager.")
        
        url = f"{self.base_url}/voices"
        params = {}
        if user_id:
            params["user_id"] = user_id
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Failed to list voices: {error_text}")
            
            data = await response.json()
            return [VoiceModel(**voice) for voice in data]
    
    async def generate_speech(self, request: TTSRequest) -> TTSResponse:
        """Generate speech from text using a trained voice.
        
        Args:
            request: TTS request parameters
            
        Returns:
            TTSResponse: Generated audio data and metadata
        """
        if self.use_local_mode:
            # Simulate speech generation
            # In a real implementation, this would use the local Chatterbox model
            # For now, we'll just create a dummy WAV file
            
            # Create a simple WAV header (this is just a placeholder)
            audio_data = b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
            
            # Simulate processing delay
            await asyncio.sleep(0.5)
            
            return TTSResponse(
                audio_data=audio_data,
                duration=1.0,  # Dummy duration
                format=request.output_format,
                voice_id=request.voice_id
            )
        
        if not self.session:
            raise RuntimeError("Client not initialized. Use as async context manager.")
        
        url = f"{self.base_url}/tts"
        
        payload = request.dict()
        
        async with self.session.post(url, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Failed to generate speech: {error_text}")
            
            audio_data = await response.read()
            headers = response.headers
            
            return TTSResponse(
                audio_data=audio_data,
                duration=float(headers.get("X-Duration", 0)),
                format=request.output_format,
                voice_id=request.voice_id
            )
    
    async def delete_voice(self, voice_id: str) -> bool:
        """Delete a trained voice.
        
        Args:
            voice_id: ID of the voice to delete
            
        Returns:
            bool: True if deletion was successful
        """
        if self.use_local_mode:
            # Simulate voice deletion
            # In local mode, just return success
            return True
        
        if not self.session:
            raise RuntimeError("Client not initialized. Use as async context manager.")
        
        url = f"{self.base_url}/voices/{voice_id}"
        
        async with self.session.delete(url) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Failed to delete voice: {error_text}")
            
            return True
    
    # Synchronous methods for simpler usage
    
    def upload_audio_sync(self, audio_file: Union[str, BinaryIO], user_id: str, voice_name: str) -> TrainingJob:
        """Synchronous version of upload_audio."""
        if self.use_local_mode:
            # Run the async version in a new event loop
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(self.upload_audio(audio_file, user_id, voice_name))
            finally:
                loop.close()
        
        headers = self._get_headers()
        url = f"{self.base_url}/voices/upload"
        
        files = None
        data = {
            "user_id": user_id,
            "name": voice_name
        }
        
        if isinstance(audio_file, str):
            files = {"audio_file": open(audio_file, "rb")}
        else:
            files = {"audio_file": audio_file}
        
        response = requests.post(url, headers=headers, data=data, files=files)
        if response.status_code != 200:
            raise Exception(f"Failed to upload audio: {response.text}")
        
        return TrainingJob(**response.json())
    
    def get_training_status_sync(self, job_id: str) -> TrainingJob:
        """Synchronous version of get_training_status."""
        if self.use_local_mode:
            # Run the async version in a new event loop
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(self.get_training_status(job_id))
            finally:
                loop.close()
        
        headers = self._get_headers()
        url = f"{self.base_url}/jobs/{job_id}"
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to get job status: {response.text}")
        
        return TrainingJob(**response.json())
    
    def list_voices_sync(self, user_id: Optional[str] = None) -> List[VoiceModel]:
        """Synchronous version of list_voices."""
        if self.use_local_mode:
            # Run the async version in a new event loop
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(self.list_voices(user_id))
            finally:
                loop.close()
        
        headers = self._get_headers()
        url = f"{self.base_url}/voices"
        params = {}
        if user_id:
            params["user_id"] = user_id
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"Failed to list voices: {response.text}")
        
        data = response.json()
        return [VoiceModel(**voice) for voice in data]
    
    def generate_speech_sync(self, request: TTSRequest) -> TTSResponse:
        """Synchronous version of generate_speech."""
        if self.use_local_mode:
            # Run the async version in a new event loop
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(self.generate_speech(request))
            finally:
                loop.close()
        
        headers = self._get_headers()
        url = f"{self.base_url}/tts"
        
        payload = request.dict()
        
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to generate speech: {response.text}")
        
        return TTSResponse(
            audio_data=response.content,
            duration=float(response.headers.get("X-Duration", 0)),
            format=request.output_format,
            voice_id=request.voice_id
        )
    
    def delete_voice_sync(self, voice_id: str) -> bool:
        """Synchronous version of delete_voice."""
        if self.use_local_mode:
            # Run the async version in a new event loop
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(self.delete_voice(voice_id))
            finally:
                loop.close()
        
        headers = self._get_headers()
        url = f"{self.base_url}/voices/{voice_id}"
        
        response = requests.delete(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to delete voice: {response.text}")
        
        return True
