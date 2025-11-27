# test_agent.py
import os
import sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.workflow import build_graph
from langchain_core.messages import HumanMessage

def test_agent():
    print("Testing agent with tool calls...")
    
    app = build_graph()
    
    # Test query that should trigger tool usage
    test_query = "Analyze SJVN stock and give me buy/sell recommendation"
    
    print(f"Query: {test_query}")
    print("Streaming execution...")
    
    inputs = {"messages": [HumanMessage(content=test_query)]}
    
    for event in app.stream(inputs, stream_mode="values"):
        msg = event["messages"][-1]
        
        if msg.type == "ai" and hasattr(msg, "tool_calls") and msg.tool_calls:
            print("✓ TOOL CALLS DETECTED!")
            for tc in msg.tool_calls:
                print(f"  - {tc['name']}({tc['args']})")
                
        elif msg.type == "ai" and not hasattr(msg, "tool_calls"):
            print("\n✓ FINAL RESPONSE:")
            print(msg.content)
            
        elif msg.type == "tool":
            print(f"✓ TOOL EXECUTED: {msg.name}")

if __name__ == "__main__":
    test_agent()