# src/nodes.py
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Your project imports
from src.config import Config
from src.tools import COMPLEX_TOOLS
from src.state import AgentState
from logger import logger


# ===================================================================
# Initialize Gemini LLM (2025-Ready)
# ===================================================================
try:
    Config.require_api_key()
    # Auto-fix outdated model names
    if Config.MODEL_NAME in ["gemini-1.5-flash", "gemini-1.5-pro"]:
        fixed = Config.MODEL_NAME + "-latest"
        logger.warning(f"Old model name detected: {Config.MODEL_NAME} → using {fixed}")
        model_name = fixed
    else:
        model_name = Config.MODEL_NAME

    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0.0,
        google_api_key=Config.GOOGLE_API_KEY,
        convert_system_message_to_human=True,
        max_retries=3
    )
    logger.info(f"Gemini LLM initialized → {model_name}")

    # Bind tools and log their names dynamically
    llm_with_tools = llm.bind_tools(COMPLEX_TOOLS)
    tool_names = [tool.name for tool in COMPLEX_TOOLS]
    logger.info(f"Tools bound → {len(tool_names)} tools: {', '.join(tool_names)}")

except Exception as e:
    logger.critical(f"Failed to initialize Gemini LLM: {e}")
    logger.critical("Check your GOOGLE_API_KEY and internet connection")
    raise


# ===================================================================
# LangGraph Node: Call Gemini with Tools
# ===================================================================
def call_model_node(state: AgentState) -> Dict[str, Any]:
    """Sends messages to Gemini and returns response with possible tool calls."""
    logger.info(f"call_model_node | Messages in state: {len(state['messages'])}")

    try:
        response = llm_with_tools.invoke(state["messages"])
        logger.info("Gemini responded successfully")

        if hasattr(response, "tool_calls") and response.tool_calls:
            calls = [f"{tc['name']}({tc['args']})" for tc in response.tool_calls]
            logger.info(f"Tool calls → {', '.join(calls)}")
        else:
            logger.info("Final response (no tool calls)")

        return {"messages": [response]}

    except Exception as e:
        logger.error(f"Error in call_model_node: {e}")
        return {"messages": [HumanMessage(content=f"Agent error: {e}")]}


# ===================================================================
# Debug & Test Block
# ===================================================================
if __name__ == "__main__":
    logger.info("=" * 75)
    logger.info("DEBUG MODE: Testing nodes.py independently")
    logger.info("=" * 75)

    test_query = "Analyze the last 30 days performance of Reliance Industries (RELIANCE.NS) including today's opening price in INR."

    logger.info(f"Test Query → {test_query}")
    test_state = {"messages": [HumanMessage(content=test_query)]}

    result = call_model_node(test_state)
    final_msg = result["messages"][-1]

    logger.info("GEMINI RESPONSE:")
    logger.info("-" * 60)
    logger.info(final_msg.content[:1500] + ("..." if len(final_msg.content) > 1500 else ""))
    logger.info("-" * 60)

    if hasattr(final_msg, "tool_calls") and final_msg.tool_calls:
        logger.info("TOOL CALLS REQUESTED:")
        for tc in final_msg.tool_calls:
            logger.info(f"   → {tc['name']} | Args: {tc['args']}")

    logger.info("nodes.py debug test completed!")