"""
Voice processing service for speech-to-text and text-to-speech
"""
import base64
import io
from typing import Optional, Dict, Any
from pydantic import BaseModel
from app.services.ai_service import ai_service
import logging

logger = logging.getLogger(__name__)


class VoiceProcessor:
    """Handles voice input and output processing"""
    
    def __init__(self):
        self.supported_formats = ['wav', 'mp3', 'm4a', 'ogg']
        self.max_audio_size = 25 * 1024 * 1024  # 25MB limit for OpenAI
    
    async def process_voice_input(self, audio_data: bytes, language: str = "en") -> Dict[str, Any]:
        """Process voice input and return transcribed text"""
        try:
            # Validate input
            if not audio_data:
                raise ValueError("Audio data cannot be empty")
            
            if len(audio_data) > self.max_audio_size:
                raise ValueError(f"Audio file too large. Maximum size: {self.max_audio_size} bytes")
            
            if not self.validate_audio_format(audio_data):
                raise ValueError("Invalid audio format")
            
            # Transcribe audio to text
            transcribed_text = await ai_service.transcribe_audio(audio_data, language)
            
            if not transcribed_text or not transcribed_text.strip():
                raise ValueError("No speech detected in audio")
            
            # Clean and normalize text
            cleaned_text = self._clean_transcription(transcribed_text)
            
            return {
                "success": True,
                "transcribed_text": cleaned_text,
                "original_text": transcribed_text,
                "language": language,
                "confidence": 0.9,  # Placeholder confidence score
                "audio_size": len(audio_data)
            }
            
        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            return {
                "success": False,
                "error": str(e),
                "transcribed_text": "",
                "confidence": 0.0,
                "audio_size": len(audio_data) if audio_data else 0
            }
    
    async def generate_voice_response(self, text: str, voice: str = "alloy") -> Dict[str, Any]:
        """Generate audio response from text"""
        try:
            # Generate audio from text
            audio_data = await ai_service.generate_audio(text, voice)
            
            # Encode to base64 for transmission
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            return {
                "success": True,
                "audio_data": audio_base64,
                "text": text,
                "voice": voice,
                "duration": len(audio_data) / 16000  # Rough duration estimate
            }
            
        except Exception as e:
            logger.error(f"Error generating voice response: {e}")
            return {
                "success": False,
                "error": str(e),
                "audio_data": "",
                "text": text
            }
    
    def _clean_transcription(self, text: str) -> str:
        """Clean and normalize transcribed text"""
        if not text:
            return ""
        
        # Basic cleaning
        cleaned = text.strip()
        
        # Remove extra whitespace
        cleaned = " ".join(cleaned.split())
        
        # Capitalize first letter
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]
        
        return cleaned
    
    def validate_audio_format(self, audio_data: bytes) -> bool:
        """Validate audio format and size"""
        if len(audio_data) == 0:
            return False
        
        if len(audio_data) > self.max_audio_size:
            return False
        
        # Basic format validation (check for common audio headers)
        audio_headers = {
            b'RIFF': 'wav',
            b'ID3': 'mp3',
            b'\xff\xfb': 'mp3',
            b'fLaC': 'flac',
            b'OggS': 'ogg'
        }
        
        for header, format_type in audio_headers.items():
            if audio_data.startswith(header):
                return True
        
        return True  # Allow other formats, let OpenAI handle validation
    
    async def process_voice_with_context(self, audio_data: bytes, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process voice input with additional context"""
        try:
            # Process voice input
            voice_result = await self.process_voice_input(
                audio_data, 
                context.get('language', 'en')
            )
            
            if not voice_result['success']:
                return voice_result
            
            # Add context information
            voice_result.update({
                'context': context,
                'timestamp': context.get('timestamp'),
                'session_id': context.get('session_id')
            })
            
            return voice_result
            
        except Exception as e:
            logger.error(f"Error processing voice with context: {e}")
            return {
                "success": False,
                "error": str(e),
                "transcribed_text": "",
                "confidence": 0.0
            }
