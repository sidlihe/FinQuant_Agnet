# src/nodes.py 
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.config import Config
from src.tools import COMPLEX_TOOLS
from src.state import AgentState
from logger import logger

# Initialize LLM
try:
    Config.require_api_key()
    model_name = Config.MODEL_NAME
    if model_name in ["gemini-1.5-flash", "gemini-1.5-pro"]:
        model_name = model_name + "-latest"

    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0.0,
        google_api_key=Config.GOOGLE_API_KEY,
        convert_system_message_to_human=True,
        max_retries=3
    )
    logger.info(f"Gemini LLM initialized → {model_name}")

    llm_with_tools = llm.bind_tools(COMPLEX_TOOLS)
    tool_names = [tool.name for tool in COMPLEX_TOOLS]
    logger.info(f"Tools bound → {len(tool_names)} tools: {', '.join(tool_names)}")

except Exception as e:
    logger.critical(f"Failed to initialize Gemini LLM: {e}")
    raise

def call_model_node(state: AgentState) -> Dict[str, Any]:
    """ALWAYS force tool usage for stock analysis"""
    logger.info(f"call_model_node | Messages in state: {len(state['messages'])}")
    
    # Add system message that FORCES tool usage
    system_message = SystemMessage(content="""You MUST use tools for stock analysis. 
For any stock-related query, ALWAYS use ultimate_stock_verdict tool first to get data.
NEVER give stock recommendations without using tools.
After getting tool data, analyze it and give specific buy/hold/sell advice with price targets.""")

    # Combine system message with user messages
    enhanced_messages = [system_message] + state["messages"]
    
    try:
        response = llm_with_tools.invoke(enhanced_messages)
        logger.info("Gemini responded")
        
        if hasattr(response, "tool_calls") and response.tool_calls:
            calls = [f"{tc['name']}({tc['args']})" for tc in response.tool_calls]
            logger.info(f"Tool calls → {', '.join(calls)}")
        else:
            logger.warning("No tool calls - agent responding directly")
            
        return {"messages": [response]}

    except Exception as e:
        logger.error(f"Error in call_model_node: {e}")
        return {"messages": [HumanMessage(content=f"Agent error: {e}")]}