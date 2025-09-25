"""
Proactive engagement service for checking in with users
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.services.session_manager import session_manager
from app.websocket.connection_manager import connection_manager
from app.models.schemas import WebSocketMessage, MessageType, ResponseType
import logging

logger = logging.getLogger(__name__)


class ProactiveEngagementService:
    """Service for proactive user engagement"""
    
    def __init__(self):
        self.engagement_interval = 300  # 5 minutes
        self.inactivity_threshold = 600  # 10 minutes
        self.is_running = False
        self.engagement_task = None
    
    async def start(self):
        """Start the proactive engagement service"""
        if not self.is_running:
            self.is_running = True
            self.engagement_task = asyncio.create_task(self._engagement_loop())
            logger.info("Proactive engagement service started")
    
    async def stop(self):
        """Stop the proactive engagement service"""
        if self.is_running:
            self.is_running = False
            if self.engagement_task:
                self.engagement_task.cancel()
                try:
                    await self.engagement_task
                except asyncio.CancelledError:
                    pass
            logger.info("Proactive engagement service stopped")
    
    async def _engagement_loop(self):
        """Main engagement loop"""
        while self.is_running:
            try:
                await asyncio.sleep(self.engagement_interval)
                await self._check_user_engagement()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in engagement loop: {e}")
                await asyncio.sleep(30)  # Wait before retrying
    
    async def _check_user_engagement(self):
        """Check user engagement and send proactive messages"""
        try:
            # Get all active sessions
            active_sessions = await session_manager.get_active_sessions()
            
            for session_id in active_sessions:
                await self._check_session_engagement(session_id)
                
        except Exception as e:
            logger.error(f"Error checking user engagement: {e}")
    
    async def _check_session_engagement(self, session_id: str):
        """Check engagement for a specific session"""
        try:
            # Get session info
            session = await session_manager.get_session(session_id)
            if not session:
                return
            
            # Check if session is inactive
            time_since_activity = datetime.utcnow() - session.last_activity
            
            if time_since_activity > timedelta(seconds=self.inactivity_threshold):
                await self._send_proactive_message(session_id, "inactivity")
            
            # Check if user might need help
            elif time_since_activity > timedelta(seconds=self.engagement_interval):
                await self._send_proactive_message(session_id, "check_in")
                
        except Exception as e:
            logger.error(f"Error checking session engagement for {session_id}: {e}")
    
    async def _send_proactive_message(self, session_id: str, message_type: str):
        """Send proactive message to user"""
        try:
            # Check if user is still connected
            if session_id not in connection_manager.active_connections:
                return
            
            # Generate appropriate message
            message_content = self._generate_proactive_message(message_type)
            
            # Send message
            response = WebSocketMessage(
                message_type=MessageType.RESPONSE,
                data={
                    "type": ResponseType.PROACTIVE.value,
                    "content": message_content,
                    "session_id": session_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            await connection_manager.send_message(session_id, response)
            logger.info(f"Sent proactive message to session {session_id}: {message_type}")
            
        except Exception as e:
            logger.error(f"Error sending proactive message to {session_id}: {e}")
    
    def _generate_proactive_message(self, message_type: str) -> str:
        """Generate proactive message content"""
        messages = {
            "inactivity": [
                "Hello! I noticed you haven't been active for a while. Are you still there?",
                "Hi there! I'm here if you need any help with your phone.",
                "Hello! Would you like me to help you with anything?",
                "Hi! I'm your assistant. Just let me know if you need help with anything."
            ],
            "check_in": [
                "How are you doing? Need any help?",
                "Is everything going well? I'm here to help!",
                "Would you like to try something new? I can guide you!",
                "Hello! What would you like to do today?"
            ]
        }
        
        import random
        message_list = messages.get(message_type, messages["check_in"])
        return random.choice(message_list)
    
    async def send_encouragement(self, session_id: str, context: str = "general"):
        """Send encouraging message to user"""
        try:
            encouragement_messages = {
                "general": [
                    "Great job! You're doing well!",
                    "You're learning quickly! Keep it up!",
                    "I'm proud of your progress!",
                    "You're getting the hang of this!"
                ],
                "completion": [
                    "Excellent! You completed that step perfectly!",
                    "Well done! You're making great progress!",
                    "Perfect! You're doing amazing!",
                    "Fantastic! You've got this!"
                ],
                "struggle": [
                    "Don't worry, take your time. I'm here to help!",
                    "It's okay to take it slow. We'll get there together!",
                    "No rush! I'll guide you through this step by step.",
                    "You're doing great! Let's try again together."
                ]
            }
            
            import random
            message_list = encouragement_messages.get(context, encouragement_messages["general"])
            message_content = random.choice(message_list)
            
            response = WebSocketMessage(
                message_type=MessageType.RESPONSE,
                data={
                    "type": ResponseType.PROACTIVE.value,
                    "content": message_content,
                    "session_id": session_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            await connection_manager.send_message(session_id, response)
            logger.info(f"Sent encouragement to session {session_id}: {context}")
            
        except Exception as e:
            logger.error(f"Error sending encouragement to {session_id}: {e}")
    
    async def send_task_suggestion(self, session_id: str, user_preferences: Optional[Dict[str, Any]] = None):
        """Send task suggestions based on user preferences"""
        try:
            # Default task suggestions
            task_suggestions = [
                "Would you like to order some food?",
                "How about sending a message to someone?",
                "Would you like to make a phone call?",
                "How about checking your photos?",
                "Would you like to listen to some music?"
            ]
            
            # Customize based on user preferences
            if user_preferences:
                if user_preferences.get("favorite_apps"):
                    favorite_apps = user_preferences["favorite_apps"]
                    if "swiggy" in favorite_apps:
                        task_suggestions.insert(0, "Would you like to order food from Swiggy?")
                    if "whatsapp" in favorite_apps:
                        task_suggestions.insert(1, "How about sending a WhatsApp message?")
            
            import random
            suggestion = random.choice(task_suggestions)
            
            response = WebSocketMessage(
                message_type=MessageType.RESPONSE,
                data={
                    "type": ResponseType.PROACTIVE.value,
                    "content": suggestion,
                    "session_id": session_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            await connection_manager.send_message(session_id, response)
            logger.info(f"Sent task suggestion to session {session_id}")
            
        except Exception as e:
            logger.error(f"Error sending task suggestion to {session_id}: {e}")


# Global proactive engagement service instance
proactive_engagement_service = ProactiveEngagementService()
