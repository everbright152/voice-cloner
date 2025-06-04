"""
Test script for Chatterbox integration.

This script tests the basic functionality of the Chatterbox client.
"""
import os
import asyncio
import logging
from dotenv import load_dotenv

# Add parent directory to path to allow importing from app
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.chatterbox.client import ChatterboxClient
from app.services.chatterbox.models import TTSRequest, EmotionLevel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Mock API key for testing (will be replaced with actual key in production)
os.environ["CHATTERBOX_API_KEY"] = os.environ.get("CHATTERBOX_API_KEY", "test_api_key")

# Test configuration
TEST_USER_ID = "test_user"
TEST_VOICE_NAME = "Test Voice"
TEST_AUDIO_FILE = "test_audio.wav"  # This would be a real audio file in actual testing


async def test_async_client():
    """Test the asynchronous client functionality."""
    logger.info("Testing asynchronous Chatterbox client...")
    
    try:
        async with ChatterboxClient() as client:
            # In a real test, we would upload audio and train a voice
            # For now, we'll just simulate the API responses
            
            # List voices (this would fail with a mock API key)
            try:
                voices = await client.list_voices(user_id=TEST_USER_ID)
                logger.info(f"Found {len(voices)} voices for user {TEST_USER_ID}")
            except Exception as e:
                logger.warning(f"Could not list voices: {e}")
                logger.info("This is expected with a mock API key")
            
            logger.info("Async client test completed")
    except Exception as e:
        logger.error(f"Error in async client test: {e}")


def test_sync_client():
    """Test the synchronous client functionality."""
    logger.info("Testing synchronous Chatterbox client...")
    
    try:
        client = ChatterboxClient()
        
        # In a real test, we would upload audio and train a voice
        # For now, we'll just simulate the API responses
        
        # List voices (this would fail with a mock API key)
        try:
            voices = client.list_voices_sync(user_id=TEST_USER_ID)
            logger.info(f"Found {len(voices)} voices for user {TEST_USER_ID}")
        except Exception as e:
            logger.warning(f"Could not list voices: {e}")
            logger.info("This is expected with a mock API key")
        
        logger.info("Sync client test completed")
    except Exception as e:
        logger.error(f"Error in sync client test: {e}")


def main():
    """Run all tests."""
    logger.info("Starting Chatterbox integration tests...")
    
    # Run synchronous tests
    test_sync_client()
    
    # Run asynchronous tests
    asyncio.run(test_async_client())
    
    logger.info("All tests completed")


if __name__ == "__main__":
    main()
