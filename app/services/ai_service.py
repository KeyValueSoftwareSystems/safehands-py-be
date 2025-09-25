"""
AI service for handling OpenAI interactions
"""
import openai
from typing import Dict, Any, Optional, List
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class AIService:
    """Service for OpenAI model interactions"""
    
    def __init__(self):
        self.openai_client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        if settings.openai_api_key:
            self.openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
            logger.info("OpenAI client initialized")
        else:
            logger.warning("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
    
    async def generate_text(self, prompt: str, model: str = None, **kwargs) -> str:
        """Generate text using OpenAI"""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized. Please check OPENAI_API_KEY.")
        
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        # Use default model from config if not specified
        if model is None:
            model = settings.openai_model
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            
            if not response.choices or not response.choices[0].message.content:
                raise ValueError("Empty response from OpenAI")
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating text with OpenAI: {e}")
            raise
    
    async def analyze_image(self, image_data: bytes, prompt: str, model: str = None) -> str:
        """Analyze image using OpenAI Vision"""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")
        
        import base64
        
        # Use default vision model from config if not specified
        if model is None:
            model = settings.vision_model
        
        try:
            # Encode image to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            raise
    
    async def generate_audio(self, text: str, voice: str = "alloy") -> bytes:
        """Generate audio from text using OpenAI TTS"""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")
        
        try:
            response = await self.openai_client.audio.speech.create(
                model=settings.tts_model,
                voice=voice,
                input=text
            )
            return response.content
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            raise
    
    async def transcribe_audio(self, audio_data: bytes, language: str = "en") -> str:
        """Transcribe audio to text using OpenAI Whisper"""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")
        
        try:
            # Create a file-like object from bytes
            import io
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"
            
            response = await self.openai_client.audio.transcriptions.create(
                model=settings.whisper_model,
                file=audio_file,
                language=language
            )
            return response.text
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise


# Global AI service instance
ai_service = AIService()
