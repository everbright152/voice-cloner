"""
Data models for Chatterbox integration.
"""
from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class EmotionLevel(float, Enum):
    """Emotion intensity levels for voice generation."""
    NEUTRAL = 0.0
    LOW = 0.5
    MEDIUM = 1.0
    HIGH = 1.5


class VoiceStatus(str, Enum):
    """Status of a voice training job."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TrainingJob(BaseModel):
    """Model representing a voice training job."""
    job_id: str
    user_id: str
    voice_name: str
    status: VoiceStatus = VoiceStatus.PENDING
    created_at: str
    updated_at: str
    audio_file_path: str
    metadata: Optional[Dict] = None


class VoiceModel(BaseModel):
    """Model representing a trained voice."""
    voice_id: str
    user_id: str
    name: str
    created_at: str
    status: VoiceStatus
    metadata: Optional[Dict] = None


class TTSRequest(BaseModel):
    """Model for text-to-speech generation request."""
    voice_id: str
    text: str
    emotion: float = Field(default=EmotionLevel.NEUTRAL, ge=0.0)
    output_format: str = "wav"


class TTSResponse(BaseModel):
    """Model for text-to-speech generation response."""
    audio_data: bytes
    duration: float
    format: str
    voice_id: str


class WebhookEvent(BaseModel):
    """Model for webhook events."""
    event_type: str
    job_id: str
    status: VoiceStatus
    voice_id: Optional[str] = None
    message: Optional[str] = None
    timestamp: str
    metadata: Optional[Dict] = None
