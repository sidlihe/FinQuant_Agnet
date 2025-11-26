# main.py
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.workflow import build_graph
from langchain_core.messages import HumanMessage
from logger import logger


def main():
    logger.info("=" * 90)
    logger.info("FINQUANT RETAIL AGENT v2.0 — PROFESSIONAL MODE")
    logger.info("LLM decides ticker format (IRFC.NS, RELIANCE.NS, etc.) — Most Realistic & Robust")
    logger.info("=" * 90)

    print("\nFinQuant Pro Agent Ready! (Real Indian Stocks | Real Data)")
    print("Just type any stock name — I will understand:")
    print("   → irfc, IRFC, Indian Railway Finance")
    print("   → tcs, TCS, Tata Consultancy")
    print("   → reliance, Reliance Industries")
    print("   → sbi bank, hdfc, adani power")
    print("   → Type 'quit' to exit\n")

    app = build_graph()

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in {"quit", "exit", "bye", "q"}:
                print("See you! All reports saved in outputs/ folder.")
                logger.info("Session ended by user")
                break
            if not user_input:
                continue

            # CRITICAL: Send RAW user input directly to LLM
            # Let Gemini decide if it's IRFC.NS or RELIANCE.NS
            smart_prompt = f"""
You are a professional Indian stock analyst.
The user said: "{user_input}"

Your job:
1. Understand which stock they mean (e.g., 'irfc' → IRFC.NS, 'reliance' → RELIANCE.NS)
2. Use your tools to:
   - Fetch real 30-day data
   - Calculate volatility, average, high/low
   - Show today's opening price
   - Save a beautiful Markdown report automatically

Do NOT assume the ticker format. Always call fetch_market_data with correct .NS suffix.
Be accurate and professional.
"""

            logger.info(f"Raw User Input → {user_input}")
            logger.info("Sending raw query to LLM for natural understanding...")

            print("\nAnalyzing your request...")
            inputs = {"messages": [HumanMessage(content=smart_prompt)]}

            for event in app.stream(inputs, config={"recursion_limit": 30}, stream_mode="values"):
                msg = event["messages"][-1]

                if msg.type == "ai":
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        calls = [f"{tc['name']}({tc['args']})" for tc in msg.tool_calls]
                        print(f"Agent → Using tools: {', '.join(calls)}")
                    else:
                        # Only print final meaningful response
                        if len(msg.content.strip()) > 50:
                            print(f"\n{msg.content}\n")

                elif msg.type == "tool":
                    tool_name = getattr(msg, "name", "tool")
                    if tool_name == "save_report_to_disk":
                        print("Professional report saved to outputs/ folder!")
                    else:
                        print(f"Tool executed: {tool_name}")

            print("─" * 70 + "\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print("Sorry, something went wrong. Try again.")


if __name__ == "__main__":
    main()