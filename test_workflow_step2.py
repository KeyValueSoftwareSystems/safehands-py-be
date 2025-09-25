#!/usr/bin/env python3
"""
Test step verification in the workflow system
"""
import asyncio
import json
from app.agents.senior_assistant_agent import SeniorAssistantState, senior_assistant_agent

async def test_step_verification():
    """Test step verification"""
    print("🧪 Testing Step Verification")
    print("=" * 50)
    
    # Test 2: User says "done" to complete step 1
    print("\n📝 Test 2: User says 'done' to complete step 1")
    state = SeniorAssistantState(
        session_id="test_123",
        user_input="done",
        screen_context=None,
        current_app=None,
        current_task=None,
        step_history=[],
        last_activity="",
        metadata={},
        intent="verification",
        confidence=0.9,
        guidance=[],
        current_step=None,
        ui_element=None,
        audio_response=None,
        response_type=None,
        workflow_type="swiggy_order_food",
        workflow_steps=[
            "Open the Swiggy app on your phone",
            "Search for the food you want to order",
            "Select a restaurant from the results",
            "Choose the items you want to order",
            "Add items to your cart",
            "Review your order and proceed to checkout",
            "Enter your delivery address",
            "Select payment method and place order"
        ],
        current_step_index=0,  # Currently on step 1
        workflow_status="waiting_verification",
        waiting_for_verification=True,
        workflow_context={},
        interruption_handled=False
    )
    
    try:
        response = await senior_assistant_agent.process_request(state)
        print(f"✅ Response Type: {response.response_type}")
        print(f"✅ Content: {response.content[:200]}...")
        print(f"✅ Next Step: {response.next_step}")
        
        if "Step 2" in response.content:
            print("🎉 SUCCESS: Step verification worked correctly!")
        else:
            print("❌ FAILED: Step verification not working properly")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    asyncio.run(test_step_verification())
