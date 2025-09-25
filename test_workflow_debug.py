#!/usr/bin/env python3
"""
Debug test to see what's happening in the workflow
"""
import asyncio
import json
from app.agents.senior_assistant_agent import SeniorAssistantState, senior_assistant_agent

async def test_workflow_debug():
    """Debug the workflow step by step"""
    print("🧪 Debugging Workflow Step by Step")
    print("=" * 50)
    
    # Test: User says "done" to complete step 1
    print("\n📝 Test: User says 'done' to complete step 1")
    
    # Create state with workflow already started (step 1 completed, moving to step 2)
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
        current_step_index=1,  # Should be on step 2 (index 1)
        workflow_status="active",  # Should be active, not waiting_verification
        waiting_for_verification=False,
        workflow_context={},
        interruption_handled=False
    )
    
    print(f"Initial state:")
    print(f"  - Current step index: {state['current_step_index']}")
    print(f"  - Workflow status: {state['workflow_status']}")
    print(f"  - Total steps: {len(state['workflow_steps'])}")
    print(f"  - Current step should be: {state['workflow_steps'][state['current_step_index']]}")
    
    try:
        response = await senior_assistant_agent.process_request(state)
        print(f"\n✅ Response Type: {response.response_type}")
        print(f"✅ Content: {response.content[:200]}...")
        print(f"✅ Next Step: {response.next_step}")
        
        if "Step 2" in response.content:
            print("🎉 SUCCESS: Step 2 displayed correctly!")
        elif "Step 1" in response.content:
            print("❌ FAILED: Still showing Step 1")
        elif "completed" in response.content.lower():
            print("❌ FAILED: Workflow completed prematurely")
        else:
            print("❓ UNKNOWN: Unexpected response")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    asyncio.run(test_workflow_debug())
