"""
Simplified Swiggy Ordering Agent with Hardcoded Conversation Flow
"""
import logging
from typing import Dict, Any, Optional, List
from app.models.schemas import AssistantResponse, ResponseType, UIElement
from app.services.in_memory_state_manager import in_memory_state_manager

logger = logging.getLogger(__name__)


class SimpleSwiggyAgent:
    """Simplified agent for Swiggy ordering with hardcoded conversation flow"""
    
    def __init__(self):
        # Define the hardcoded conversation flow
        self.conversation_steps = [
            {
                "step": 0,
                "expected_input": "I need to order food online",
                "response": """Hello! I'm here to help you order food online. 

I can see you have food delivery apps on your phone. Let me tell you about the two main options:

📱 **Swiggy** - This is a red and orange colored app with a white 'S' logo. Swiggy has many restaurants and usually delivers food quickly. They often have good discounts and offers.

📱 **Zomato** - This is a red colored app with a white spoon and fork logo. Zomato also has many restaurants and good food options.

Both apps are good for ordering food, but I'll help you with Swiggy today as it's very easy to use and reliable.

Which app would you like to use? Please type "Swiggy" or "Zomato".""",
                "next_expected": ["swiggy", "zomato"]
            },
            {
                "step": 1,
                "expected_input": "swiggy",
                "response": """Great choice! Swiggy is an excellent app for ordering food.

Now, let me help you open the Swiggy app on your phone:

📱 **Look for the Swiggy app on your phone's home screen:**
- It has a RED and ORANGE colored background
- You'll see a big white letter "S" in the middle
- The word "Swiggy" is written below it

👆 **To open the app:**
1. Find this red and orange Swiggy icon on your phone screen
2. Tap on it once with your finger
3. The app will open and show you the food ordering page

Please find the Swiggy app and tap on it to open. Once you've opened the app, please type "done" so I can help you with the next step.""",
                "next_expected": ["done"]
            },
            {
                "step": 2,
                "expected_input": "done",
                "response": """Wonderful! Now you should be on the food delivery page.

Here's what you should see on your screen:

🔍 **At the top:** There's a white search bar (text box) where you can type something like 'Sweets' or 'Pizza'

🍽️ **Below that:** You'll see a list of restaurants. Each restaurant shows:
- The restaurant name
- What kind of food they serve
- How long it takes to deliver (like "30 mins")
- Star ratings from other customers

👉 **Did you reach this screen?** 
If yes, please type 'Yes', and then I'll guide you on what to do next to find the food you want.""",
                "next_expected": ["yes"]
            },
            {
                "step": 3,
                "expected_input": "yes",
                "response": """Perfect! Now let's find the food you want to order.

You have two ways to find food:

🔍 **Option 1 - Use the Search Box (Recommended):**
1. Look at the top of your screen - you'll see a WHITE box with light gray text
2. Tap inside this white box with your finger
3. Type the name of food you want (like "biryani", "pizza", "sweets", or "chicken")
4. After typing, look for a small magnifying glass icon (🔍) and tap it
   OR your phone's keyboard might show a "Search" button - tap that

🍽️ **Option 2 - Browse Restaurants:**
You can scroll down and look at the restaurant list to find one you like

**Let's try the search method first.** Please:
1. Tap the white search box at the top
2. Type in the food you want to eat
3. Tap the search button or magnifying glass icon
4. Then type "done" once you've searched""",
                "next_expected": ["done"]
            },
            {
                "step": 4,
                "expected_input": "done",
                "response": """Excellent! Now you should see search results.

You'll notice there are **TWO TABS** at the top of your results:
📍 **"Restaurants"** tab - Shows restaurants that serve your food
🍽️ **"Dishes"** tab - Shows specific food items

Here's what to do:

**If you want to pick a specific dish:**
1. Tap on the "Dishes" tab
2. Scroll down to see different food items
3. When you find something you like, tap the "ADD" button next to it
4. If a popup appears asking about customization (like spice level), choose what you want and tap "ADD ITEM" at the bottom
5. For simple items, it will be added directly to your cart

**If you want to browse a restaurant first:**
1. Stay on the "Restaurants" tab  
2. Tap on any restaurant name you like
3. Browse their menu and add items

**After adding items to your cart:**
- You'll see a green "View Cart" button at the bottom
- Tap "View Cart" when you're ready to order

Please add the items you want and then type "done" when you've tapped "View Cart".""",
                "next_expected": ["done"]
            },
            {
                "step": 5,
                "expected_input": "done",
                "response": """Great! Now you're in the payments page.

Here's what you should see:

📋 **At the top of the page:** You can see all the food items you selected listed with their prices

💰 **At the bottom:** You'll see the total amount you need to pay

🛒 **To proceed with your order:**
Look for a button that says "Proceed to Pay" or "Place Order" at the bottom of the screen.

👆 **Tap this button** when you're happy with your order and ready to choose how to pay.

Please tap "Proceed to Pay" and then type "done" once you've done this.""",
                "next_expected": ["done"]
            },
            {
                "step": 6,
                "expected_input": "done",
                "response": """Perfect! Now you're on the payment options page.

You'll see different ways to pay for your food:

💳 **Credit/Debit Card** - Pay with your bank card
📱 **UPI** - Pay using apps like Google Pay, PhonePe, or Paytm  
💵 **Pay on Delivery (Cash)** - Pay cash when the food arrives

**I recommend choosing "Pay on Delivery" or "Cash on Delivery"** because:
- It's the safest option for you
- No need to enter card details
- You can pay the delivery person when they bring your food

👆 **Please look for "Pay on Delivery" or "Cash on Delivery"** option and tap on it.

Once you've selected this payment method, please tell me "yes, pay on delivery" so I can help you complete your order.""",
                "next_expected": ["yes, pay on delivery"]
            },
            {
                "step": 7,
                "expected_input": "yes, pay on delivery",
                "response": """Excellent choice! Pay on Delivery is the safest and easiest option.

Now you should see:

💵 **Page Title:** "Pay on Delivery" or similar text at the top

✅ **Green Button:** Look for a GREEN button at the bottom with text like:
- "Pay With Cash" 
- "Confirm Order"
- "Place Order"

👆 **Final Step:** Tap this green button to confirm and place your food order.

💰 **Important Reminder:** 
- Keep the exact cash amount ready
- When the delivery person arrives with your food, pay them the total amount shown on your screen
- They might not have change, so try to have the exact amount

**Please tap the green "Pay With Cash" button to complete your order!**

Your food will be prepared and delivered to your address. You'll get updates about your order status on the app.""",
                "next_expected": ["order_complete"]
            }
        ]
    
    async def process_request(self, session_id: str, user_input: str) -> AssistantResponse:
        """Process user request with hardcoded conversation flow"""
        logger.info(f"🍔 [SWIGGY_AGENT] ===== Processing request =====")
        logger.info(f"🍔 [SWIGGY_AGENT] Session ID: {session_id}")
        logger.info(f"🍔 [SWIGGY_AGENT] User input: '{user_input}'")
        logger.info(f"🍔 [SWIGGY_AGENT] Input length: {len(user_input)} characters")
        
        try:
            # Normalize user input for matching
            user_input_lower = user_input.lower().strip()
            
            # Load existing conversation state
            existing_state = await in_memory_state_manager.load_workflow_state(session_id)
            
            if existing_state:
                current_step = existing_state.get('current_step_index', 0)
                logger.info(f"📂 [SWIGGY_AGENT] Current conversation step: {current_step}")
                return await self._handle_conversation_step(session_id, user_input_lower, current_step)
            else:
                logger.info(f"🆕 [SWIGGY_AGENT] Starting new conversation")
                return await self._start_conversation(session_id, user_input_lower)
                
        except Exception as e:
            logger.error(f"❌ [SWIGGY_AGENT] Error in process_request: {e}")
            logger.error(f"❌ [SWIGGY_AGENT] Error type: {type(e).__name__}")
            return self._get_error_response(session_id, str(e))
    
    async def _start_conversation(self, session_id: str, user_input: str) -> AssistantResponse:
        """Start a new conversation"""
        logger.info(f"🆕 [SWIGGY_AGENT] Starting new conversation for session: {session_id}")
        
        # Check if user wants to order food (step 0)
        if self._matches_step(user_input, 0):
            logger.info(f"🆕 [SWIGGY_AGENT] User wants to order food - starting conversation")
            
            # Save initial state
            conversation_state = {
                "session_id": session_id,
                "current_step_index": 0,
                "workflow_type": "food_ordering_conversation",
                "workflow_status": "active"
            }
            await in_memory_state_manager.save_workflow_state(session_id, conversation_state)
            
            # Return first response
            step_data = self.conversation_steps[0]
            return AssistantResponse(
                session_id=session_id,
                response_type=ResponseType.INSTRUCTION,
                content=step_data["response"],
                ui_element=None,
                next_step=None
            )
        else:
            # Guide user to start the conversation
            return AssistantResponse(
                session_id=session_id,
                response_type=ResponseType.INSTRUCTION,
                content="Hello! I can help you order food online. To get started, please tell me: 'I need to order food online'",
                ui_element=None,
                next_step=None
            )
    
    async def _handle_conversation_step(self, session_id: str, user_input: str, current_step: int) -> AssistantResponse:
        """Handle ongoing conversation based on current step"""
        logger.info(f"🔄 [SWIGGY_AGENT] ===== Handling conversation step =====")
        logger.info(f"🔄 [SWIGGY_AGENT] Current step: {current_step}")
        logger.info(f"🔄 [SWIGGY_AGENT] User input: {user_input}")
        
        # Get expected inputs for the CURRENT step (not next step)
        current_step_data = self.conversation_steps[current_step]
        expected_inputs = current_step_data.get("next_expected", [])
        
        logger.info(f"🔄 [SWIGGY_AGENT] Expected inputs: {expected_inputs}")
        
        # Check if user input matches any expected input
        user_input_clean = user_input.lower().strip()
        matches = False
        for expected in expected_inputs:
            if expected.lower().strip() == user_input_clean or expected.lower().strip() in user_input_clean:
                matches = True
                break
        
        logger.info(f"🔄 [SWIGGY_AGENT] Input matches expected: {matches}")
        
        if matches:
            # Move to next step
            next_step = current_step + 1
            
            if next_step < len(self.conversation_steps):
                logger.info(f"🔄 [SWIGGY_AGENT] Advancing to step {next_step}")
                
                # Update state to next step
                conversation_state = {
                    "session_id": session_id,
                    "current_step_index": next_step,
                    "workflow_type": "food_ordering_conversation",
                    "workflow_status": "active"
                }
                await in_memory_state_manager.save_workflow_state(session_id, conversation_state)
                
                # Return response for next step
                step_data = self.conversation_steps[next_step]
                return AssistantResponse(
                    session_id=session_id,
                    response_type=ResponseType.INSTRUCTION,
                    content=step_data["response"],
                    ui_element=None,
                    next_step=None
                )
            else:
                # Conversation completed
                logger.info(f"🎉 [SWIGGY_AGENT] Conversation completed!")
                await in_memory_state_manager.delete_workflow_state(session_id)
                
                return AssistantResponse(
                    session_id=session_id,
                    response_type=ResponseType.INSTRUCTION,
                    content="🎉 Congratulations! You have successfully placed your food order! Your delicious meal will be delivered to you soon. Enjoy your food! 🍽️\n\nIf you need help with anything else, just let me know!",
                    ui_element=None,
                    next_step=None
                )
        else:
            # If user input doesn't match expected, provide guidance
            return AssistantResponse(
                session_id=session_id,
                response_type=ResponseType.INSTRUCTION,
                content=f"I'm waiting for you to respond with one of these: {', '.join(expected_inputs)}.\n\nPlease follow the instructions I gave you and then respond accordingly.",
                ui_element=None,
                next_step=None
            )
    
    def _matches_step(self, user_input: str, step_index: int) -> bool:
        """Check if user input matches expected input for a step"""
        if step_index >= len(self.conversation_steps):
            return False
            
        step_data = self.conversation_steps[step_index]
        expected_inputs = step_data.get("next_expected", [])
        
        # Normalize user input
        user_input_clean = user_input.lower().strip()
        
        # Check against expected inputs
        for expected in expected_inputs:
            if expected.lower().strip() == user_input_clean or expected.lower().strip() in user_input_clean:
                return True
        
        # For step 0, also check for variations of "order food"
        if step_index == 0:
            food_keywords = ["order food", "food online", "order", "hungry", "eat"]
            return any(keyword in user_input_clean for keyword in food_keywords)
        
        return False
    
    def _get_error_response(self, session_id: str, error_message: str) -> AssistantResponse:
        """Generate error response"""
        return AssistantResponse(
            session_id=session_id,
            response_type=ResponseType.INSTRUCTION,
            content=f"I'm sorry, something went wrong. Please try again or tell me 'I need to order food online' to start over.",
            ui_element=None,
            next_step=None
        )


# Global instance
simple_swiggy_agent = SimpleSwiggyAgent()
