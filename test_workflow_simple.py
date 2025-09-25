#!/usr/bin/env python3
"""
Simple test script to verify the workflow system
"""
import asyncio
import json
from app.agents.senior_assistant_agent import SeniorAssistantState, senior_assistant_agent

async def test_workflow():
    """Test the workflow system"""
    print("🧪 Testing Workflow System")
    print("=" * 50)
    
    # Test 1: Initial request
    print("\n📝 Test 1: Initial request - 'I want to order food from Swiggy'")
    state = SeniorAssistantState(
        session_id="test_123",
        user_input="I want to order food from Swiggy",
        screen_context=None,
        current_app=None,
        current_task=None,
        step_history=[],
        last_activity="",
        metadata={},
        intent="order_food",
        confidence=0.9,
        guidance=[],
        current_step=None,
        ui_element=None,
        audio_response=None,
        response_type=None,
        workflow_type=None,
        workflow_steps=None,
        current_step_index=0,
        workflow_status="idle",
        waiting_for_verification=False,
        workflow_context={},
        interruption_handled=False
    )
    
    try:
        response = await senior_assistant_agent.process_request(state)
        print(f"✅ Response Type: {response.response_type}")
        print(f"✅ Content: {response.content[:200]}...")
        print(f"✅ Next Step: {response.next_step}")
        
        if "Step 1" in response.content:
            print("🎉 SUCCESS: Workflow started correctly!")
        else:
            print("❌ FAILED: Workflow not started properly")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    asyncio.run(test_workflow())
