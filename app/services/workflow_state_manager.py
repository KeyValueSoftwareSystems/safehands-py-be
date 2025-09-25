"""
Workflow state management service using Redis
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import redis.asyncio as redis
from app.config import settings
# from app.models.workflow_state import SeniorAssistantState  # Removed - using Dict[str, Any] instead

logger = logging.getLogger(__name__)


class WorkflowStateManager:
    """Manages workflow state persistence using Redis"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.workflow_prefix = "workflow:"
        self.interruption_prefix = "interruption:"
        self.workflow_timeout = 3600  # 1 hour
    
    async def connect(self):
        """Connect to Redis"""
        self.redis_client = redis.from_url(
            settings.redis_url,
            db=settings.redis_db,
            decode_responses=True
        )
        logger.info("✅ [WORKFLOW_STATE] Connected to Redis")
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("✅ [WORKFLOW_STATE] Disconnected from Redis")
    
    async def save_workflow_state(self, session_id: str, state: Dict[str, Any]) -> bool:
        """Save workflow state to Redis"""
        try:
            if not self.redis_client:
                await self.connect()
            
            workflow_key = f"{self.workflow_prefix}{session_id}"
            
            # Convert state to JSON-serializable format
            state_data = {
                "session_id": state.get("session_id"),
                "user_input": state.get("user_input"),
                "screen_context": state.get("screen_context"),
                "current_app": state.get("current_app"),
                "current_task": state.get("current_task"),
                "step_history": state.get("step_history", []),
                "last_activity": state.get("last_activity"),
                "metadata": state.get("metadata", {}),
                "intent": state.get("intent"),
                "confidence": state.get("confidence", 0.0),
                "guidance": state.get("guidance", []),
                "current_step": state.get("current_step"),
                "ui_element": state.get("ui_element"),
                "audio_response": state.get("audio_response"),
                "response_type": state.get("response_type"),
                "workflow_type": state.get("workflow_type"),
                "workflow_steps": state.get("workflow_steps"),
                "current_step_index": state.get("current_step_index", 0),
                "workflow_status": state.get("workflow_status", "idle"),
                "waiting_for_verification": state.get("waiting_for_verification", False),
                "workflow_context": state.get("workflow_context", {}),
                "interruption_handled": state.get("interruption_handled", False),
                "saved_at": datetime.utcnow().isoformat()
            }
            
            # Save to Redis with expiration
            await self.redis_client.setex(
                workflow_key,
                self.workflow_timeout,
                json.dumps(state_data, default=str)
            )
            
            logger.info(f"💾 [WORKFLOW_STATE] Saved workflow state for session: {session_id}")
            logger.info(f"💾 [WORKFLOW_STATE] Workflow type: {state.get('workflow_type')}")
            logger.info(f"💾 [WORKFLOW_STATE] Workflow status: {state.get('workflow_status')}")
            logger.info(f"💾 [WORKFLOW_STATE] Current step index: {state.get('current_step_index')}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ [WORKFLOW_STATE] Error saving workflow state: {e}")
            return False
    
    async def load_workflow_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load workflow state from Redis"""
        try:
            if not self.redis_client:
                await self.connect()
            
            workflow_key = f"{self.workflow_prefix}{session_id}"
            state_data = await self.redis_client.get(workflow_key)
            
            if not state_data:
                logger.info(f"📭 [WORKFLOW_STATE] No workflow state found for session: {session_id}")
                return None
            
            # Parse JSON data
            state_dict = json.loads(state_data)
            
            # Convert back to Dict format
            state = {
                "session_id": state_dict.get("session_id", session_id),
                "user_input": state_dict.get("user_input", ""),
                "screen_context": state_dict.get("screen_context"),
                "current_app": state_dict.get("current_app"),
                "current_task": state_dict.get("current_task"),
                "step_history": state_dict.get("step_history", []),
                "last_activity": state_dict.get("last_activity", ""),
                "metadata": state_dict.get("metadata", {}),
                "intent": state_dict.get("intent"),
                "confidence": state_dict.get("confidence", 0.0),
                "guidance": state_dict.get("guidance", []),
                "current_step": state_dict.get("current_step"),
                "ui_element": state_dict.get("ui_element"),
                "audio_response": state_dict.get("audio_response"),
                "response_type": state_dict.get("response_type"),
                "workflow_type": state_dict.get("workflow_type"),
                "workflow_steps": state_dict.get("workflow_steps"),
                "current_step_index": state_dict.get("current_step_index", 0),
                "workflow_status": state_dict.get("workflow_status", "idle"),
                "waiting_for_verification": state_dict.get("waiting_for_verification", False),
                "workflow_context": state_dict.get("workflow_context", {}),
                "interruption_handled": state_dict.get("interruption_handled", False)
            }
            
            logger.info(f"📂 [WORKFLOW_STATE] Loaded workflow state for session: {session_id}")
            logger.info(f"📂 [WORKFLOW_STATE] Workflow type: {state.get('workflow_type')}")
            logger.info(f"📂 [WORKFLOW_STATE] Workflow status: {state.get('workflow_status')}")
            logger.info(f"📂 [WORKFLOW_STATE] Current step index: {state.get('current_step_index')}")
            
            return state
            
        except Exception as e:
            logger.error(f"❌ [WORKFLOW_STATE] Error loading workflow state: {e}")
            return None
    
    async def delete_workflow_state(self, session_id: str) -> bool:
        """Delete workflow state from Redis"""
        try:
            workflow_key = f"{self.workflow_prefix}{session_id}"
            result = await self.redis_client.delete(workflow_key)
            
            if result > 0:
                logger.info(f"🗑️ [WORKFLOW_STATE] Deleted workflow state for session: {session_id}")
                return True
            else:
                logger.info(f"📭 [WORKFLOW_STATE] No workflow state to delete for session: {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ [WORKFLOW_STATE] Error deleting workflow state: {e}")
            return False
    
    async def save_interruption(self, session_id: str, interruption_data: Dict[str, Any]) -> bool:
        """Save interruption data for frontend escalation"""
        try:
            interruption_key = f"{self.interruption_prefix}{session_id}"
            
            interruption_data.update({
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "escalated": False
            })
            
            # Save interruption with shorter expiration (5 minutes)
            await self.redis_client.setex(
                interruption_key,
                300,  # 5 minutes
                json.dumps(interruption_data, default=str)
            )
            
            logger.info(f"🚨 [WORKFLOW_STATE] Saved interruption for session: {session_id}")
            logger.info(f"🚨 [WORKFLOW_STATE] Interruption type: {interruption_data.get('type', 'unknown')}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ [WORKFLOW_STATE] Error saving interruption: {e}")
            return False
    
    async def get_interruption(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get interruption data for frontend (only non-escalated interruptions)"""
        try:
            interruption_key = f"{self.interruption_prefix}{session_id}"
            interruption_data = await self.redis_client.get(interruption_key)
            
            if not interruption_data:
                return None
            
            interruption_dict = json.loads(interruption_data)
            
            # Only return non-escalated interruptions
            if interruption_dict.get("escalated", False):
                logger.info(f"📨 [WORKFLOW_STATE] Interruption already escalated for session: {session_id}")
                return None
            
            logger.info(f"📨 [WORKFLOW_STATE] Retrieved interruption for session: {session_id}")
            return interruption_dict
            
        except Exception as e:
            logger.error(f"❌ [WORKFLOW_STATE] Error getting interruption: {e}")
            return None
    
    async def mark_interruption_escalated(self, session_id: str) -> bool:
        """Mark interruption as escalated and delete it from Redis"""
        try:
            interruption_key = f"{self.interruption_prefix}{session_id}"
            interruption_data = await self.redis_client.get(interruption_key)
            
            if not interruption_data:
                return False
            
            # Delete the interruption data after escalation
            result = await self.redis_client.delete(interruption_key)
            
            if result > 0:
                logger.info(f"✅ [WORKFLOW_STATE] Interruption escalated and deleted for session: {session_id}")
                return True
            else:
                logger.warning(f"⚠️ [WORKFLOW_STATE] Failed to delete interruption for session: {session_id}")
                return False
            
        except Exception as e:
            logger.error(f"❌ [WORKFLOW_STATE] Error marking interruption as escalated: {e}")
            return False
    
    async def delete_interruption(self, session_id: str) -> bool:
        """Delete interruption data"""
        try:
            interruption_key = f"{self.interruption_prefix}{session_id}"
            result = await self.redis_client.delete(interruption_key)
            
            if result > 0:
                logger.info(f"🗑️ [WORKFLOW_STATE] Deleted interruption for session: {session_id}")
                return True
            else:
                logger.info(f"📭 [WORKFLOW_STATE] No interruption to delete for session: {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ [WORKFLOW_STATE] Error deleting interruption: {e}")
            return False
    
    async def get_workflow_sessions(self) -> List[str]:
        """Get all active workflow session IDs"""
        try:
            pattern = f"{self.workflow_prefix}*"
            keys = await self.redis_client.keys(pattern)
            session_ids = [key.replace(self.workflow_prefix, "") for key in keys]
            
            logger.info(f"📋 [WORKFLOW_STATE] Found {len(session_ids)} active workflow sessions")
            return session_ids
            
        except Exception as e:
            logger.error(f"❌ [WORKFLOW_STATE] Error getting workflow sessions: {e}")
            return []


# Global workflow state manager instance
workflow_state_manager = WorkflowStateManager()
