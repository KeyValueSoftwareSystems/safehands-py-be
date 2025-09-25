#!/usr/bin/env python3
"""
Test workflow steps generation
"""
import asyncio
from app.agents.senior_assistant_agent import SeniorAssistantAgent

async def test_workflow_steps():
    """Test workflow steps generation"""
    print("🧪 Testing Workflow Steps Generation")
    print("=" * 50)
    
    agent = SeniorAssistantAgent()
    
    # Test workflow steps generation
    workflow_steps = await agent._generate_workflow_steps("swiggy_order_food", {})
    
    print(f"Generated {len(workflow_steps)} workflow steps:")
    for i, step in enumerate(workflow_steps):
        print(f"  {i}: {step}")
    
    print(f"\nStep indices: 0 to {len(workflow_steps) - 1}")
    print(f"Total steps: {len(workflow_steps)}")
    
    # Test index comparison
    for i in range(len(workflow_steps) + 2):
        is_complete = i >= len(workflow_steps)
        print(f"Index {i}: {'COMPLETE' if is_complete else 'CONTINUE'}")

if __name__ == "__main__":
    asyncio.run(test_workflow_steps())
