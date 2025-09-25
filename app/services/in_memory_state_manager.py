"""
In-Memory State Manager for V1 Agent
Replaces Redis usage with simple in-memory storage
"""
import logging
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class InMemoryStateManager:
    """In-memory state manager for workflow states and interruptions"""
    
    def __init__(self):
        # In-memory storage
        self.workflow_states: Dict[str, Dict[str, Any]] = {}
        self.interruptions: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        
        logger.info("🧠 [IN_MEMORY_STATE] InMemoryStateManager initialized")
    
    async def save_workflow_state(self, session_id: str, state: Dict[str, Any]) -> bool:
        """Save workflow state to memory"""
        try:
            async with self._lock:
                # Add timestamp for debugging
                state['last_updated'] = datetime.now().isoformat()
                self.workflow_states[session_id] = state.copy()
                
                logger.info(f"💾 [IN_MEMORY_STATE] Saved workflow state for session: {session_id}")
                logger.info(f"💾 [IN_MEMORY_STATE] Workflow type: {state.get('workflow_type', 'unknown')}")
                logger.info(f"💾 [IN_MEMORY_STATE] Workflow status: {state.get('workflow_status', 'unknown')}")
                logger.info(f"💾 [IN_MEMORY_STATE] Current step index: {state.get('current_step_index', 0)}")
                return True
        except Exception as e:
            logger.error(f"❌ [IN_MEMORY_STATE] Error saving workflow state: {e}")
            return False
    
    async def load_workflow_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load workflow state from memory"""
        try:
            async with self._lock:
                state = self.workflow_states.get(session_id)
                if state:
                    logger.info(f"📂 [IN_MEMORY_STATE] Loaded workflow state for session: {session_id}")
                    logger.info(f"📂 [IN_MEMORY_STATE] Workflow type: {state.get('workflow_type', 'unknown')}")
                    logger.info(f"📂 [IN_MEMORY_STATE] Workflow status: {state.get('workflow_status', 'unknown')}")
                    logger.info(f"📂 [IN_MEMORY_STATE] Current step index: {state.get('current_step_index', 0)}")
                    return state.copy()
                else:
                    logger.info(f"📭 [IN_MEMORY_STATE] No workflow state found for session: {session_id}")
                    return None
        except Exception as e:
            logger.error(f"❌ [IN_MEMORY_STATE] Error loading workflow state: {e}")
            return None
    
    async def delete_workflow_state(self, session_id: str) -> bool:
        """Delete workflow state from memory"""
        try:
            async with self._lock:
                if session_id in self.workflow_states:
                    del self.workflow_states[session_id]
                    logger.info(f"🗑️ [IN_MEMORY_STATE] Deleted workflow state for session: {session_id}")
                    return True
                else:
                    logger.info(f"📭 [IN_MEMORY_STATE] No workflow state to delete for session: {session_id}")
                    return False
        except Exception as e:
            logger.error(f"❌ [IN_MEMORY_STATE] Error deleting workflow state: {e}")
            return False
    
    async def save_interruption(self, session_id: str, interruption_data: Dict[str, Any]) -> bool:
        """Save interruption data to memory"""
        try:
            async with self._lock:
                # Add timestamp and escalation status
                interruption_data['timestamp'] = datetime.now().isoformat()
                interruption_data['escalated'] = False
                self.interruptions[session_id] = interruption_data.copy()
                
                logger.info(f"🚨 [IN_MEMORY_STATE] Saved interruption for session: {session_id}")
                logger.info(f"🚨 [IN_MEMORY_STATE] Interruption type: {interruption_data.get('type', 'unknown')}")
                logger.info(f"🚨 [IN_MEMORY_STATE] User input: {interruption_data.get('user_input', 'unknown')}")
                return True
        except Exception as e:
            logger.error(f"❌ [IN_MEMORY_STATE] Error saving interruption: {e}")
            return False
    
    async def get_interruption(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get interruption data from memory (only non-escalated interruptions)"""
        try:
            async with self._lock:
                interruption_data = self.interruptions.get(session_id)
                
                if not interruption_data:
                    return None
                
                # Only return non-escalated interruptions
                if interruption_data.get("escalated", False):
                    logger.info(f"📨 [IN_MEMORY_STATE] Interruption already escalated for session: {session_id}")
                    return None
                
                logger.info(f"📨 [IN_MEMORY_STATE] Retrieved interruption for session: {session_id}")
                return interruption_data.copy()
        except Exception as e:
            logger.error(f"❌ [IN_MEMORY_STATE] Error getting interruption: {e}")
            return None
    
    async def mark_interruption_escalated(self, session_id: str) -> bool:
        """Mark interruption as escalated and delete it from memory"""
        try:
            async with self._lock:
                if session_id in self.interruptions:
                    del self.interruptions[session_id]
                    logger.info(f"✅ [IN_MEMORY_STATE] Interruption escalated and deleted for session: {session_id}")
                    return True
                else:
                    logger.warning(f"⚠️ [IN_MEMORY_STATE] No interruption to escalate for session: {session_id}")
                    return False
        except Exception as e:
            logger.error(f"❌ [IN_MEMORY_STATE] Error marking interruption as escalated: {e}")
            return False
    
    async def get_workflow_sessions(self) -> List[str]:
        """Get all active workflow session IDs"""
        try:
            async with self._lock:
                sessions = list(self.workflow_states.keys())
                logger.info(f"📊 [IN_MEMORY_STATE] Found {len(sessions)} active workflow sessions")
                return sessions
        except Exception as e:
            logger.error(f"❌ [IN_MEMORY_STATE] Error getting workflow sessions: {e}")
            return []
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics about stored data"""
        try:
            async with self._lock:
                stats = {
                    "active_workflows": len(self.workflow_states),
                    "active_interruptions": len(self.interruptions),
                    "workflow_sessions": list(self.workflow_states.keys()),
                    "interruption_sessions": list(self.interruptions.keys())
                }
                logger.info(f"📊 [IN_MEMORY_STATE] Stats: {stats}")
                return stats
        except Exception as e:
            logger.error(f"❌ [IN_MEMORY_STATE] Error getting stats: {e}")
            return {"error": str(e)}
    
    async def clear_all(self) -> bool:
        """Clear all stored data (for testing/debugging)"""
        try:
            async with self._lock:
                self.workflow_states.clear()
                self.interruptions.clear()
                logger.info("🧹 [IN_MEMORY_STATE] Cleared all stored data")
                return True
        except Exception as e:
            logger.error(f"❌ [IN_MEMORY_STATE] Error clearing all data: {e}")
            return False


# Global instance
in_memory_state_manager = InMemoryStateManager()
