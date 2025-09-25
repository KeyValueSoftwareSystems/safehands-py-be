"""
Session management service using Redis
"""
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import redis.asyncio as redis
from app.config import settings
from app.models.schemas import SessionInfo


class SessionManager:
    """Manages user sessions using Redis"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.session_prefix = "session:"
        self.active_sessions_key = "active_sessions"
    
    async def connect(self):
        """Connect to Redis"""
        self.redis_client = redis.from_url(
            settings.redis_url,
            db=settings.redis_db,
            decode_responses=True
        )
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def create_session(self, user_id: Optional[str] = None) -> str:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        session_info = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            is_active=True
        )
        
        # Store session in Redis with expiration
        session_key = f"{self.session_prefix}{session_id}"
        await self.redis_client.setex(
            session_key,
            settings.session_timeout,
            session_info.model_dump_json()
        )
        
        # Add to active sessions set
        await self.redis_client.sadd(self.active_sessions_key, session_id)
        
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Get session information"""
        session_key = f"{self.session_prefix}{session_id}"
        session_data = await self.redis_client.get(session_key)
        
        if not session_data:
            return None
        
        try:
            session_dict = json.loads(session_data)
            return SessionInfo(**session_dict)
        except (json.JSONDecodeError, ValueError):
            return None
    
    async def update_session(self, session_id: str, **kwargs) -> bool:
        """Update session information"""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        session.last_activity = datetime.utcnow()
        
        # Save back to Redis
        session_key = f"{self.session_prefix}{session_id}"
        await self.redis_client.setex(
            session_key,
            settings.session_timeout,
            session.model_dump_json()
        )
        
        return True
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        session_key = f"{self.session_prefix}{session_id}"
        result = await self.redis_client.delete(session_key)
        await self.redis_client.srem(self.active_sessions_key, session_id)
        return result > 0
    
    async def extend_session(self, session_id: str) -> bool:
        """Extend session timeout"""
        session_key = f"{self.session_prefix}{session_id}"
        exists = await self.redis_client.exists(session_key)
        if exists:
            await self.redis_client.expire(session_key, settings.session_timeout)
            return True
        return False
    
    async def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return await self.redis_client.smembers(self.active_sessions_key)
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions from active sessions set"""
        active_sessions = await self.get_active_sessions()
        for session_id in active_sessions:
            session_key = f"{self.session_prefix}{session_id}"
            if not await self.redis_client.exists(session_key):
                await self.redis_client.srem(self.active_sessions_key, session_id)
    
    async def get_session_count(self) -> int:
        """Get number of active sessions"""
        return await self.redis_client.scard(self.active_sessions_key)


# Global session manager instance
session_manager = SessionManager()
