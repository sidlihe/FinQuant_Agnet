# test_main.py - FIXED VERSION
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.workflow import build_graph
from langchain_core.messages import HumanMessage
from src.tools import resolve_stock_identity_local

def test_main_workflow():
    print("Testing main workflow with actual data...")
    
    # Build the graph
    app = build_graph()
    
    # Resolve stock identity
    identity = resolve_stock_identity_local("SJVN")
    print(f"Stock: {identity['screener_name']} | {identity['yfinance_ticker']}")
    
    # Test prompt that should generate recommendations
    test_prompt = f"""Analyze {identity['screener_name']} stock and give specific trading advice.

CURRENT DATA:
- Stock: {identity['screener_name']} ({identity['yfinance_ticker']})
- Position: Not holding

REQUIRED RECOMMENDATION:
**VERDICT** → STRONG BUY | BUY | AVOID | STRONG SELL

**Price Targets**:
- Entry Zone: ₹_____ - ₹_____
- Stop Loss: ₹_____
- Target: ₹_____ - ₹_____

**Time Frame** → Short term | Medium term | Long term

**Reasoning**:
• [Key reason 1]
• [Key reason 2]
• [Key reason 3]

Use the ultimate_stock_verdict tool to get the data first, then analyze and give specific recommendations."""

    print(f"Query: {test_prompt[:200]}...")
    print("Executing workflow...")
    
    inputs = {"messages": [HumanMessage(content=test_prompt)]}
    
    step = 0
    for event in app.stream(inputs, stream_mode="values"):
        step += 1
        msg = event["messages"][-1]
        print(f"\n--- STEP {step} ---")
        print(f"Message type: {msg.type}")
        
        if msg.type == "ai" and hasattr(msg, "tool_calls") and msg.tool_calls:
            print("🛠️  TOOL CALLS:")
            for tc in msg.tool_calls:
                print(f"   - {tc['name']}({tc['args']})")
                
        elif msg.type == "ai" and not hasattr(msg, "tool_calls"):
            print("✅ FINAL RECOMMENDATION:")
            print("=" * 80)
            print(msg.content)
            print("=" * 80)
            
        elif msg.type == "tool":
            print(f"🔧 TOOL EXECUTED: {msg.name}")
            print(f"   Result length: {len(getattr(msg, 'content', ''))} chars")

    print(f"\nTotal steps: {step}")

if __name__ == "__main__":
    test_main_workflow()