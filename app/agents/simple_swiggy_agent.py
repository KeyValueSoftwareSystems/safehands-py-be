"""
Simplified Swiggy Ordering Agent for Demo
"""
import logging
from typing import Dict, Any, Optional, List
from app.models.schemas import AssistantResponse, ResponseType, UIElement
from app.services.in_memory_state_manager import in_memory_state_manager
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)


class SimpleSwiggyAgent:
    """Simplified agent for Swiggy ordering demo"""
    
    def __init__(self):
        self.swiggy_steps = [
            "Open the Swiggy app on your phone",
            "Search for the food you want to order",
            "Select a restaurant from the results",
            "Choose the items you want to order",
            "Add items to your cart",
            "Review your order and proceed to checkout",
            "Enter your delivery address",
            "Select payment method and place order"
        ]
        self.ai_service = AIService()
    
    async def process_request(self, session_id: str, user_input: str) -> AssistantResponse:
        """Process user request with simple state machine"""
        logger.info(f"🍔 [SWIGGY_AGENT] ===== Processing request =====")
        logger.info(f"🍔 [SWIGGY_AGENT] Session ID: {session_id}")
        logger.info(f"🍔 [SWIGGY_AGENT] User input: '{user_input}'")
        logger.info(f"🍔 [SWIGGY_AGENT] Input length: {len(user_input)} characters")
        
        try:
            # Load existing state from memory
            existing_state = await in_memory_state_manager.load_workflow_state(session_id)
            
            if existing_state:
                current_step = existing_state.get('current_step_index', 0)
                workflow_status = existing_state.get('workflow_status', 'unknown')
                logger.info(f"📂 [SWIGGY_AGENT] Loaded existing state:")
                logger.info(f"📂 [SWIGGY_AGENT]   - Current step: {current_step}")
                logger.info(f"📂 [SWIGGY_AGENT]   - Workflow status: {workflow_status}")
                logger.info(f"📂 [SWIGGY_AGENT]   - Workflow type: {existing_state.get('workflow_type', 'none')}")
                return await self._handle_existing_workflow(session_id, user_input, existing_state)
            else:
                logger.info(f"🆕 [SWIGGY_AGENT] No existing state found - starting new workflow")
                return await self._start_new_workflow(session_id, user_input)
                
        except Exception as e:
            logger.error(f"❌ [SWIGGY_AGENT] Error in process_request: {e}")
            logger.error(f"❌ [SWIGGY_AGENT] Error type: {type(e).__name__}")
            return self._get_error_response(session_id, str(e))
    
    async def _start_new_workflow(self, session_id: str, user_input: str) -> AssistantResponse:
        """Start a new Swiggy ordering workflow"""
        logger.info(f"🆕 [SWIGGY_AGENT] Starting new workflow for session: {session_id}")
        
        # Check if user wants to order food
        is_swiggy_request = self._is_swiggy_request(user_input)
        logger.info(f"🆕 [SWIGGY_AGENT] Is Swiggy request: {is_swiggy_request}")
        
        if not is_swiggy_request:
            logger.info(f"🆕 [SWIGGY_AGENT] Not a Swiggy request - providing guidance")
            return AssistantResponse(
                session_id=session_id,
                response_type=ResponseType.INSTRUCTION,
                content="I can help you order food from Swiggy! Just say 'I want to order food from Swiggy' to get started.",
                ui_element=None,
                next_step=None
            )
        
        # Start workflow
        logger.info(f"🆕 [SWIGGY_AGENT] Creating new workflow state")
        workflow_state = {
            "session_id": session_id,
            "user_input": user_input,
            "workflow_type": "swiggy_order_food",
            "workflow_steps": self.swiggy_steps,
            "current_step_index": 0,
            "workflow_status": "active",
            "waiting_for_verification": True,
            "workflow_context": {},
            "interruption_handled": False
        }
        logger.info(f"🆕 [SWIGGY_AGENT] Workflow state created with {len(self.swiggy_steps)} steps")
        
        # Save to memory
        logger.info(f"🆕 [SWIGGY_AGENT] Saving workflow state to memory")
        await in_memory_state_manager.save_workflow_state(session_id, workflow_state)
        logger.info(f"🆕 [SWIGGY_AGENT] Workflow state saved successfully")
        
        # Generate first step
        current_step = self.swiggy_steps[0]
        content = f"Step 1 of {len(self.swiggy_steps)}: {current_step}\n\nLet me know when you've completed this step by saying 'done' or 'next'."
        logger.info(f"🆕 [SWIGGY_AGENT] Generated first step: {current_step}")
        
        response = AssistantResponse(
            session_id=session_id,
            response_type=ResponseType.INSTRUCTION,
            content=content,
            ui_element=None,
            next_step=None
        )
        logger.info(f"🆕 [SWIGGY_AGENT] Returning response with content length: {len(content)}")
        return response
    
    async def _handle_existing_workflow(self, session_id: str, user_input: str, state: Dict[str, Any]) -> AssistantResponse:
        """Handle existing workflow state"""
        current_step_index = state.get('current_step_index', 0)
        workflow_status = state.get('workflow_status', 'idle')
        workflow_type = state.get('workflow_type', 'unknown')
        
        logger.info(f"🔄 [SWIGGY_AGENT] ===== Handling existing workflow =====")
        logger.info(f"🔄 [SWIGGY_AGENT] Current step: {current_step_index}")
        logger.info(f"🔄 [SWIGGY_AGENT] Workflow status: {workflow_status}")
        logger.info(f"🔄 [SWIGGY_AGENT] Workflow type: {workflow_type}")
        
        # Check if user is confirming a step
        is_verification = self._is_verification_response(user_input)
        logger.info(f"🔄 [SWIGGY_AGENT] Is verification response: {is_verification}")
        if is_verification:
            logger.info(f"🔄 [SWIGGY_AGENT] Handling step verification")
            return await self._handle_step_verification(session_id, user_input, state)
        
        # Check if user is asking a question (interruption)
        is_interruption = self._is_interruption(user_input)
        logger.info(f"🔄 [SWIGGY_AGENT] Is interruption: {is_interruption}")
        if is_interruption:
            logger.info(f"🔄 [SWIGGY_AGENT] Handling interruption")
            return await self._handle_interruption(session_id, user_input, state)
        
        # Check if user wants to start a new workflow
        is_new_workflow = self._is_swiggy_request(user_input)
        logger.info(f"🔄 [SWIGGY_AGENT] Is new workflow request: {is_new_workflow}")
        if is_new_workflow:
            logger.info(f"🔄 [SWIGGY_AGENT] Starting new workflow")
            return await self._start_new_workflow(session_id, user_input)
        
        # Default response
        logger.info(f"🔄 [SWIGGY_AGENT] Providing default response")
        return AssistantResponse(
            session_id=session_id,
            response_type=ResponseType.INSTRUCTION,
            content="I'm here to help you with your Swiggy order. Say 'done' when you complete a step, or ask me any questions!",
            ui_element=None,
            next_step=None
        )
    
    async def _handle_step_verification(self, session_id: str, user_input: str, state: Dict[str, Any]) -> AssistantResponse:
        """Handle step verification"""
        current_step_index = state.get('current_step_index', 0)
        workflow_steps = state.get('workflow_steps', self.swiggy_steps)
        
        logger.info(f"✅ [SWIGGY_AGENT] ===== Handling step verification =====")
        logger.info(f"✅ [SWIGGY_AGENT] Current step index: {current_step_index}")
        logger.info(f"✅ [SWIGGY_AGENT] Total steps: {len(workflow_steps)}")
        logger.info(f"✅ [SWIGGY_AGENT] Step {current_step_index + 1} completed, advancing to step {current_step_index + 2}")
        
        # Advance to next step
        next_step_index = current_step_index + 1
        
        if next_step_index >= len(workflow_steps):
            # Workflow completed
            logger.info(f"🎉 [SWIGGY_AGENT] ===== Workflow completed! =====")
            logger.info(f"🎉 [SWIGGY_AGENT] All {len(workflow_steps)} steps completed successfully")
            
            # Clear workflow state
            logger.info(f"🎉 [SWIGGY_AGENT] Clearing workflow state from memory")
            await in_memory_state_manager.delete_workflow_state(session_id)
            logger.info(f"🎉 [SWIGGY_AGENT] Workflow state cleared")
            
            return AssistantResponse(
                session_id=session_id,
                response_type=ResponseType.INSTRUCTION,
                content="🎉 Excellent! You've completed all the steps successfully! Your Swiggy order should be on its way. Is there anything else I can help you with?",
                ui_element=None,
                next_step=None
            )
        else:
            # Continue to next step
            current_step = workflow_steps[next_step_index]
            content = f"Step {next_step_index + 1} of {len(workflow_steps)}: {current_step}\n\nLet me know when you've completed this step by saying 'done' or 'next'."
            logger.info(f"✅ [SWIGGY_AGENT] Moving to step {next_step_index + 1}: {current_step}")
            
            # Update state
            state['current_step_index'] = next_step_index
            state['workflow_status'] = 'active'
            state['waiting_for_verification'] = True
            logger.info(f"✅ [SWIGGY_AGENT] Updated state - new step index: {next_step_index}")
            
            # Save to memory
            logger.info(f"✅ [SWIGGY_AGENT] Saving updated state to memory")
            await in_memory_state_manager.save_workflow_state(session_id, state)
            logger.info(f"✅ [SWIGGY_AGENT] State saved successfully")
            
            response = AssistantResponse(
                session_id=session_id,
                response_type=ResponseType.INSTRUCTION,
                content=content,
                ui_element=None,
                next_step=None
            )
            logger.info(f"✅ [SWIGGY_AGENT] Returning response for step {next_step_index + 1}")
            return response
    
    async def _handle_interruption(self, session_id: str, user_input: str, state: Dict[str, Any]) -> AssistantResponse:
        """Handle user questions/interruptions using LLM"""
        current_step_index = state.get('current_step_index', 0)
        workflow_steps = state.get('workflow_steps', self.swiggy_steps)
        current_step = workflow_steps[current_step_index] if current_step_index < len(workflow_steps) else "Unknown"
        
        logger.info(f"🚨 [SWIGGY_AGENT] ===== Handling interruption =====")
        logger.info(f"🚨 [SWIGGY_AGENT] User question: '{user_input}'")
        logger.info(f"🚨 [SWIGGY_AGENT] Current step: {current_step_index + 1} - {current_step}")
        logger.info(f"🚨 [SWIGGY_AGENT] Total steps: {len(workflow_steps)}")
        
        # Save interruption to Redis for frontend escalation
        interruption_data = {
            "type": "workflow_interruption",
            "user_input": user_input,
            "workflow_type": "swiggy_order_food",
            "current_step_index": current_step_index,
            "current_step": current_step,
            "total_steps": len(workflow_steps),
            "workflow_status": state.get('workflow_status', 'unknown')
        }
        
        logger.info(f"🚨 [SWIGGY_AGENT] Saving interruption data to memory")
        await in_memory_state_manager.save_interruption(session_id, interruption_data)
        logger.info(f"🚨 [SWIGGY_AGENT] Interruption saved successfully")
        
        # Generate contextual response using LLM
        try:
            logger.info(f"🤖 [SWIGGY_AGENT] Generating LLM response for interruption")
            response = await self._generate_interruption_response(user_input, current_step, current_step_index, workflow_steps)
            logger.info(f"🤖 [SWIGGY_AGENT] LLM response generated successfully")
            logger.info(f"🤖 [SWIGGY_AGENT] Response length: {len(response)} characters")
        except Exception as e:
            logger.error(f"❌ [SWIGGY_AGENT] Error generating LLM response: {e}")
            logger.error(f"❌ [SWIGGY_AGENT] Error type: {type(e).__name__}")
            # Fallback to simple response
            response = f"I understand you have a question about: '{user_input}'\n\nYou're currently on Step {current_step_index + 1}: {current_step}\n\nI'm here to help! What would you like to know about this step?"
            logger.info(f"❌ [SWIGGY_AGENT] Using fallback response")
        
        response_obj = AssistantResponse(
            session_id=session_id,
            response_type=ResponseType.INSTRUCTION,
            content=response,
            ui_element=None,
            next_step=None
        )
        logger.info(f"🚨 [SWIGGY_AGENT] Returning interruption response")
        return response_obj
    
    async def _generate_interruption_response(self, user_question: str, current_step: str, current_step_index: int, workflow_steps: List[str]) -> str:
        """Generate contextual response using LLM for user questions during workflow"""
        logger.info(f"🤖 [SWIGGY_AGENT] ===== Generating LLM response =====")
        logger.info(f"🤖 [SWIGGY_AGENT] User question: '{user_question}'")
        logger.info(f"🤖 [SWIGGY_AGENT] Current step: {current_step_index + 1} - {current_step}")
        logger.info(f"🤖 [SWIGGY_AGENT] Total workflow steps: {len(workflow_steps)}")
        
        # Create context for the LLM
        workflow_context = "\n".join([f"{i+1}. {step}" for i, step in enumerate(workflow_steps)])
        logger.info(f"🤖 [SWIGGY_AGENT] Created workflow context with {len(workflow_steps)} steps")
        
        prompt = f"""You are a helpful assistant guiding a user through ordering food from Swiggy. The user is currently on step {current_step_index + 1} of {len(workflow_steps)}.

Current Step: {current_step}

Complete Workflow:
{workflow_context}

User's Question: "{user_question}"

Please provide a helpful, specific answer to their question while keeping them focused on the current step. Be encouraging and provide practical guidance. Keep your response concise (2-3 sentences) and actionable.

Response:"""

        logger.info(f"🤖 [SWIGGY_AGENT] Prompt length: {len(prompt)} characters")
        logger.info(f"🤖 [SWIGGY_AGENT] Calling OpenAI API with gpt-3.5-turbo")

        try:
            response = await self.ai_service.generate_text(
                prompt=prompt,
                model="gpt-3.5-turbo",
                max_tokens=150,
                temperature=0.7
            )
            logger.info(f"🤖 [SWIGGY_AGENT] OpenAI API response received")
            logger.info(f"🤖 [SWIGGY_AGENT] Response length: {len(response)} characters")
            logger.info(f"🤖 [SWIGGY_AGENT] Response preview: {response[:100]}...")
            return response.strip()
        except Exception as e:
            logger.error(f"❌ [SWIGGY_AGENT] Error generating LLM response: {e}")
            logger.error(f"❌ [SWIGGY_AGENT] Error type: {type(e).__name__}")
            raise e
    
    def _is_swiggy_request(self, user_input: str) -> bool:
        """Check if user wants to order from Swiggy"""
        swiggy_keywords = ['swiggy', 'order food', 'order from swiggy', 'food delivery', 'swiggy order']
        user_lower = user_input.lower()
        result = any(keyword in user_lower for keyword in swiggy_keywords)
        logger.debug(f"🔍 [SWIGGY_AGENT] _is_swiggy_request('{user_input}') = {result}")
        return result
    
    def _is_verification_response(self, user_input: str) -> bool:
        """Check if user is confirming a step"""
        verification_responses = ['done', 'next', 'completed', 'finished', 'yes', 'ok', 'ready', 'continue']
        user_lower = user_input.lower().strip()
        result = any(response in user_lower for response in verification_responses)
        logger.debug(f"🔍 [SWIGGY_AGENT] _is_verification_response('{user_input}') = {result}")
        return result
    
    def _is_interruption(self, user_input: str) -> bool:
        """Check if user is asking a question"""
        # First check for verification responses - these are NOT interruptions
        if self._is_verification_response(user_input):
            logger.debug(f"🔍 [SWIGGY_AGENT] _is_interruption('{user_input}') = False (verification response)")
            return False
        
        # Then check for interruption keywords
        interruption_keywords = [
            'how', 'what', 'where', 'why', 'when', 'which', 'can you', 'could you',
            'help', 'explain', 'show', 'tell me', 'i don\'t understand', 'confused',
            'stuck', 'problem', 'error', 'not working', 'can\'t find', 'difficult'
        ]
        
        user_lower = user_input.lower()
        result = any(keyword in user_lower for keyword in interruption_keywords)
        logger.debug(f"🔍 [SWIGGY_AGENT] _is_interruption('{user_input}') = {result}")
        return result
    
    def _get_error_response(self, session_id: str, error_message: str) -> AssistantResponse:
        """Get error response"""
        logger.error(f"❌ [SWIGGY_AGENT] Creating error response for session: {session_id}")
        logger.error(f"❌ [SWIGGY_AGENT] Error message: {error_message}")
        return AssistantResponse(
            session_id=session_id,
            response_type=ResponseType.ERROR,
            content=f"I'm sorry, I encountered an error: {error_message}. Please try again.",
            ui_element=None,
            next_step=None
        )


# Global instance
simple_swiggy_agent = SimpleSwiggyAgent()
