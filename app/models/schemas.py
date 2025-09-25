"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    """Types of messages in the system"""
    TEXT = "text"
    VOICE = "voice"
    SCREEN = "screen"
    COMMAND = "command"
    RESPONSE = "response"
    HEARTBEAT = "heartbeat"
    ERROR = "error"


class ResponseType(str, Enum):
    """Types of assistant responses"""
    INSTRUCTION = "instruction"
    HIGHLIGHT = "highlight"
    VERIFICATION = "verification"
    PROACTIVE = "proactive"
    ERROR = "error"


class UIElement(BaseModel):
    """Represents a UI element on screen"""
    id: str
    type: str  # button, text, image, etc.
    position: Dict[str, int]  # x, y, width, height
    text: Optional[str] = None
    app_context: Optional[str] = None


class TextMessage(BaseModel):
    """Text input message"""
    session_id: str
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    language: Optional[str] = "en-US"


class VoiceMessage(BaseModel):
    """Voice input message"""
    session_id: str
    audio_data: bytes
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    language: Optional[str] = "en-US"


class ScreenMessage(BaseModel):
    """Screen capture message"""
    session_id: str
    screenshot: bytes
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    screen_size: Optional[Dict[str, int]] = None


class CommandMessage(BaseModel):
    """Command message from client"""
    session_id: str
    command: str
    parameters: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AssistantResponse(BaseModel):
    """Assistant response message"""
    session_id: str
    response_type: ResponseType
    content: str
    audio_response: Optional[bytes] = None
    ui_element: Optional[UIElement] = None
    next_step: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HeartbeatMessage(BaseModel):
    """Heartbeat message to keep connection alive"""
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorMessage(BaseModel):
    """Error message"""
    session_id: str
    error_code: str
    error_message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SessionInfo(BaseModel):
    """Session information"""
    session_id: str
    user_id: Optional[str] = None
    created_at: datetime
    last_activity: datetime
    current_app: Optional[str] = None
    current_task: Optional[str] = None
    is_active: bool = True


class WebSocketMessage(BaseModel):
    """Base WebSocket message wrapper"""
    message_type: MessageType
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ConnectionRequest(BaseModel):
    """Initial connection request"""
    user_id: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None


class ConnectionResponse(BaseModel):
    """Connection response"""
    session_id: str
    status: str
    message: str
    server_time: datetime = Field(default_factory=datetime.utcnow)
