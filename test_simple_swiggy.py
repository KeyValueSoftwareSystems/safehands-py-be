#!/usr/bin/env python3
"""
Test simplified Swiggy agent
"""
import asyncio
from app.agents.simple_swiggy_agent import simple_swiggy_agent

async def test_simple_swiggy():
    """Test simplified Swiggy agent"""
    print("🍔 Testing Simplified Swiggy Agent")
    print("=" * 50)
    
    session_id = "test_simple_swiggy"
    
    # Test 1: Start workflow
    print("\n📝 Test 1: Start workflow - 'I want to order food from Swiggy'")
    response1 = await simple_swiggy_agent.process_request(session_id, "I want to order food from Swiggy")
    print(f"✅ Response Type: {response1.response_type}")
    print(f"✅ Content: {response1.content}")
    
    if "Step 1" in response1.content:
        print("🎉 SUCCESS: Workflow started correctly!")
    else:
        print("❌ FAILED: Workflow not started properly")
    
    # Test 2: User says "done" to complete step 1
    print("\n📝 Test 2: User says 'done' to complete step 1")
    response2 = await simple_swiggy_agent.process_request(session_id, "done")
    print(f"✅ Response Type: {response2.response_type}")
    print(f"✅ Content: {response2.content}")
    
    if "Step 2" in response2.content:
        print("🎉 SUCCESS: Step verification worked correctly!")
    else:
        print("❌ FAILED: Step verification not working")
    
    # Test 3: User says "done" again to complete step 2
    print("\n📝 Test 3: User says 'done' to complete step 2")
    response3 = await simple_swiggy_agent.process_request(session_id, "done")
    print(f"✅ Response Type: {response3.response_type}")
    print(f"✅ Content: {response3.content}")
    
    if "Step 3" in response3.content:
        print("🎉 SUCCESS: Step 3 displayed correctly!")
    else:
        print("❌ FAILED: Step 3 not working")
    
    # Test 4: User asks a question (interruption)
    print("\n📝 Test 4: User asks a question - 'How do I search for food?'")
    response4 = await simple_swiggy_agent.process_request(session_id, "How do I search for food?")
    print(f"✅ Response Type: {response4.response_type}")
    print(f"✅ Content: {response4.content}")
    
    if "question" in response4.content.lower() or "help" in response4.content.lower():
        print("🎉 SUCCESS: Interruption handling worked!")
    else:
        print("❌ FAILED: Interruption handling not working")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    asyncio.run(test_simple_swiggy())
