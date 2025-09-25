"""
WebSocket connection manager
"""
import json
import asyncio
from datetime import datetime
from typing import Dict, Set, Optional
from fastapi import WebSocket
from app.models.schemas import WebSocketMessage, MessageType
# Removed session_manager dependency - using in-memory storage only
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        # Map session_id to WebSocket connection
        self.active_connections: Dict[str, WebSocket] = {}
        # Map WebSocket to session_id for reverse lookup
        self.connection_to_session: Dict[WebSocket, str] = {}
        # Set of connections that need heartbeat
        self.heartbeat_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.connection_to_session[websocket] = session_id
        self.heartbeat_connections.add(websocket)
        
        logger.info(f"WebSocket connected for session: {session_id}")
        
        # Send welcome message
        welcome_message = WebSocketMessage(
            message_type=MessageType.RESPONSE,
            data={
                "type": "connection_established",
                "session_id": session_id,
                "message": "Connected to SafeHands Assistant"
            }
        )
        await self.send_message(session_id, welcome_message)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        session_id = self.connection_to_session.get(websocket)
        if session_id:
            del self.active_connections[session_id]
            del self.connection_to_session[websocket]
            self.heartbeat_connections.discard(websocket)
            logger.info(f"WebSocket disconnected for session: {session_id}")
    
    async def send_message(self, session_id: str, message: WebSocketMessage):
        """Send a message to a specific session"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_text(message.model_dump_json())
            except Exception as e:
                logger.error(f"Error sending message to session {session_id}: {e}")
                self.disconnect(websocket)
    
    async def send_personal_message(self, websocket: WebSocket, message: WebSocketMessage):
        """Send a message to a specific WebSocket connection"""
        try:
            # Check if connection is still active
            if websocket not in self.connection_to_session:
                return
            await websocket.send_text(message.model_dump_json())
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: WebSocketMessage):
        """Broadcast a message to all connected clients"""
        disconnected = []
        for session_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message.model_dump_json())
            except Exception as e:
                logger.error(f"Error broadcasting to session {session_id}: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected connections
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def send_heartbeat(self, websocket: WebSocket):
        """Send heartbeat to a specific connection"""
        # Check if connection is still active
        if websocket not in self.connection_to_session:
            return
            
        heartbeat_message = WebSocketMessage(
            message_type=MessageType.HEARTBEAT,
            data={"timestamp": str(datetime.utcnow())}
        )
        await self.send_personal_message(websocket, heartbeat_message)
    
    async def start_heartbeat_task(self):
        """Start the heartbeat task for all connections"""
        while True:
            try:
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                
                # Send heartbeat to all connections
                disconnected = []
                for websocket in list(self.heartbeat_connections):
                    try:
                        # Check if connection is still active before sending heartbeat
                        if websocket in self.connection_to_session:
                            await self.send_heartbeat(websocket)
                        else:
                            disconnected.append(websocket)
                    except Exception as e:
                        logger.error(f"Error sending heartbeat: {e}")
                        disconnected.append(websocket)
                
                # Clean up disconnected connections
                for websocket in disconnected:
                    self.disconnect(websocket)
                    
            except Exception as e:
                logger.error(f"Error in heartbeat task: {e}")
                await asyncio.sleep(5)
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)
    
    def get_session_id(self, websocket: WebSocket) -> Optional[str]:
        """Get session ID for a WebSocket connection"""
        return self.connection_to_session.get(websocket)
    
    async def cleanup_inactive_connections(self):
        """Clean up inactive connections"""
        # This would be called periodically to clean up stale connections
        # Implementation depends on your specific requirements
        pass


# Global connection manager instance
connection_manager = ConnectionManager()
