"""
Client for interacting with Resemble AI's Chatterbox.

This module provides a client for interacting with the Chatterbox API
for voice training and text-to-speech generation.
"""
import os
import time
import logging
import asyncio
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
            api_key: API key for Chatterbox. If not provided, will look for CHATTERBOX_API_KEY env var.
            base_url: Base URL for Chatterbox API. If not provided, will use default.
        """
        self.api_key = api_key or os.environ.get("CHATTERBOX_API_KEY")
        if not self.api_key:
            raise ValueError("Chatterbox API key not provided")
        
        self.base_url = base_url or "https://api.chatterbox.resemble.ai/v1"
        self.session = None
    
    async def __aenter__(self):
        """Enter async context manager."""
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
        headers = self._get_headers()
        url = f"{self.base_url}/jobs/{job_id}"
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to get job status: {response.text}")
        
        return TrainingJob(**response.json())
    
    def list_voices_sync(self, user_id: Optional[str] = None) -> List[VoiceModel]:
        """Synchronous version of list_voices."""
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
        headers = self._get_headers()
        url = f"{self.base_url}/voices/{voice_id}"
        
        response = requests.delete(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to delete voice: {response.text}")
        
        return True
