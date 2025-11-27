# workflow.py - UPDATED
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from src.state import AgentState
from src.nodes import call_model_node  # CHANGED: import from simple_nodes
from src.tools import COMPLEX_TOOLS
from logger import logger

def build_graph():
    logger.info("Building LangGraph workflow...")

    workflow = StateGraph(AgentState)

    # Nodes
    workflow.add_node("agent", call_model_node)
    workflow.add_node("tools", ToolNode(COMPLEX_TOOLS))

    # Edges
    workflow.add_edge(START, "agent")
    workflow.add_edge("tools", "agent")

    # Conditional edge
    workflow.add_conditional_edges(
        source="agent",
        path=tools_condition,
        path_map={"tools": "tools", END: END}
    )

    graph = workflow.compile()
    logger.info("LangGraph workflow built and compiled successfully!")
    return graph


# ===================================================================
# Debug & Interactive Test Mode
# ===================================================================
if __name__ == "__main__":
    logger.info("=" * 75)
    logger.info("LANGGRAPH WORKFLOW DEBUG MODE")
    logger.info("Building and testing the full agent with real tools...")
    logger.info("=" * 75)

    # Build the agent
    app = build_graph()

    # Test query (you can change this anytime)
    user_query = "Analyze the last 30 days performance of Reliance Industries stock (RELIANCE.NS). Include volatility, today's opening price, and save a professional report."

    logger.info(f"User Query → {user_query}")
    logger.info("Streaming agent execution...")

    try:
        # Stream the full execution with events
        for event in app.stream(
            {"messages": [{"role": "user", "content": user_query}]},
            stream_mode="values"
        ):
            last_msg = event["messages"][-1]

            # Log only meaningful updates
            if last_msg.type == "ai":
                if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                    calls = [f"{tc['name']}({tc['args']})" for tc in last_msg.tool_calls]
                    logger.info(f"AGENT → Requesting tools: {', '.join(calls)}")
                else:
                    logger.info("AGENT → Final response ready")
                    print("\nFINAL ANSWER:\n")
                    print(last_msg.content)
                    print("\n" + "="*75)

            elif last_msg.type == "tool":
                logger.info(f"TOOL → {last_msg.name} executed")

    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        raise

    logger.info("Full LangGraph agent test completed successfully!")
    logger.info("Check outputs/ folder for your saved stock report.")