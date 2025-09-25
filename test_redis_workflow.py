#!/usr/bin/env python3
"""
Test Redis-based workflow with step verification
"""
import asyncio
from app.agents.senior_assistant_agent import SeniorAssistantState, senior_assistant_agent

async def test_redis_workflow():
    """Test Redis workflow with step verification"""
    print("🧪 Testing Redis-Based Workflow with Step Verification")
    print("=" * 60)
    
    session_id = "test_redis_workflow"
    
    # Test 1: Start workflow
    print("\n📝 Test 1: Start workflow - 'I want to order food from Swiggy'")
    state1 = SeniorAssistantState(
        session_id=session_id,
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
        response1 = await senior_assistant_agent.process_request(state1)
        print(f"✅ Response Type: {response1.response_type}")
        print(f"✅ Content: {response1.content[:100]}...")
        
        if "Step 1" in response1.content:
            print("🎉 SUCCESS: Workflow started correctly!")
        else:
            print("❌ FAILED: Workflow not started properly")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 2: User says "done" to complete step 1
    print("\n📝 Test 2: User says 'done' to complete step 1")
    state2 = SeniorAssistantState(
        session_id=session_id,  # Same session ID
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
        workflow_type=None,  # Will be loaded from Redis
        workflow_steps=None,  # Will be loaded from Redis
        current_step_index=0,  # Will be loaded from Redis
        workflow_status="idle",  # Will be loaded from Redis
        waiting_for_verification=False,  # Will be loaded from Redis
        workflow_context={},
        interruption_handled=False
    )
    
    try:
        response2 = await senior_assistant_agent.process_request(state2)
        print(f"✅ Response Type: {response2.response_type}")
        print(f"✅ Content: {response2.content[:100]}...")
        
        if "Step 2" in response2.content:
            print("🎉 SUCCESS: Step verification worked correctly!")
        elif "Step 1" in response2.content:
            print("❌ FAILED: Still showing Step 1 - step not advanced")
        elif "completed" in response2.content.lower():
            print("❌ FAILED: Workflow completed prematurely")
        else:
            print("❓ UNKNOWN: Unexpected response")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 3: User says "done" again to complete step 2
    print("\n📝 Test 3: User says 'done' to complete step 2")
    state3 = SeniorAssistantState(
        session_id=session_id,  # Same session ID
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
        workflow_type=None,  # Will be loaded from Redis
        workflow_steps=None,  # Will be loaded from Redis
        current_step_index=0,  # Will be loaded from Redis
        workflow_status="idle",  # Will be loaded from Redis
        waiting_for_verification=False,  # Will be loaded from Redis
        workflow_context={},
        interruption_handled=False
    )
    
    try:
        response3 = await senior_assistant_agent.process_request(state3)
        print(f"✅ Response Type: {response3.response_type}")
        print(f"✅ Content: {response3.content[:100]}...")
        
        if "Step 3" in response3.content:
            print("🎉 SUCCESS: Step 3 displayed correctly!")
        elif "Step 2" in response3.content:
            print("❌ FAILED: Still showing Step 2 - step not advanced")
        elif "completed" in response3.content.lower():
            print("❌ FAILED: Workflow completed prematurely")
        else:
            print("❓ UNKNOWN: Unexpected response")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_redis_workflow())
