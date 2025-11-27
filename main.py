# main.py → FINAL PROFESSIONAL VERSION (WITH USER HOLDING LOGIC)

import os
import sys
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_core.messages import HumanMessage

from logger import logger
from src.config import Config
from src.tools import (
    resolve_stock_identity_local,
    build_stock_verdict_payload,
)
from src.workflow import build_graph


def ask_user(prompt: str) -> str:
    return input(f"{prompt.strip()} ").strip()


def ask_yes_no(prompt: str) -> bool:
    while True:
        ans = input(f"{prompt.strip()} (y/n): ").strip().lower()
        if ans in {"y", "yes"}:
            return True
        if ans in {"n", "no"}:
            return False
        print("Please respond with 'y' or 'n'.")


def prompt_stock_name() -> str:
    print("\nWhich stock should I analyze today?")
    print("Examples: irctc, irfc, niva bupa, nalco, tcs, adani power")
    return ask_user("Stock name:")


def main():
    Config.ensure_dirs()
    logger.info("=" * 90)
    logger.info("FINQUANT PRO v5.0 — THE REAL FUND MANAGER WITH PERSONAL ADVICE")
    logger.info("Now asks if you own the stock & gives perfect SL/Target/Entry")
    logger.info("=" * 90)

    print("\nWelcome to FinQuant Pro v5.0")
    print("India's smartest stock verdict engine — now with PERSONAL advice!")
    print("Type any stock name, or 'quit' to exit.")

    app = build_graph()

    while True:
        try:
            user_input = prompt_stock_name()
            if user_input.lower() in {"quit", "exit", "bye", "q", "end", "stop"}:
                print("\nThank you! All reports saved in outputs/ folder")
                logger.info("Session ended")
                break
            if not user_input:
                continue

            logger.info(f"User query → {user_input}")
            try:
                identity = resolve_stock_identity_local(user_input)
            except ValueError as exc:
                print(f"Could not understand that stock name → {exc}")
                continue

            print(
                f"\nDetected Screener: {identity['screener_name']} | "
                f"yfinance ticker: {identity['yfinance_ticker']}"
            )

            if not ask_yes_no("Use these identifiers?"):
                identity["screener_name"] = ask_user("Enter exact Screener name:") or identity["screener_name"]
                identity["yfinance_ticker"] = ask_user("Enter yfinance ticker (e.g., IRFC.NS):") or identity["yfinance_ticker"]

            print("\nFetching full Screener + technical data... (may take ~30s)")
            try:
                payload = build_stock_verdict_payload(
                    identity["screener_name"], identity["yfinance_ticker"]
                )
                tool_response = json.dumps(payload, indent=2, ensure_ascii=False)
                print("Data downloaded successfully!")
                if payload.get("saved_files"):
                    print("Saved raw fundamentals →")
                    for path in payload["saved_files"]:
                        print(f"   • {path}")
            except Exception as exc:
                logger.error(f"ultimate_stock_verdict failed: {exc}")
                print(f"Could not fetch data: {exc}")
                continue

            owns = ask_yes_no("\nDo you already own this stock?")

            final_prompt = f"""
You are India's top independent equity analyst.

User asked about: "{user_input}"
User already owns the stock: {"YES" if owns else "NO"}

Here is full data:
{tool_response}

Give PERSONAL advice in this exact format:

**Personal Recommendation**: 
   - If user owns: Hold | Book Profit | Book Loss | Average Down | Sell Immediately
   - If user does NOT own: Strong Buy | Buy | Avoid Entry

**Confidence**: High | Medium | Low

**Suggested Action**:
   - If owns: "Hold and wait" or "Book loss at ₹___" or "Average at ₹___"
   - If not owns: "Buy at ₹___" or "Avoid entry above ₹___"

**Target Price**: ₹____ – ₹____
**Stop Loss**: ₹____
**Time Horizon**: Short term | Medium term | Long term

**Key Positives** (3):
- ...

**Key Risks** (3):
- ...

**One-Line Summary**: ...

Be honest. Be practical. Use real numbers from the data.
"""

            print("\nGenerating your PERSONAL advice...")
            final_inputs = {"messages": [HumanMessage(content=final_prompt)]}
            final_verdict = None

            for event in app.stream(final_inputs, stream_mode="values"):
                msg = event["messages"][-1]
                if msg.type == "ai" and not hasattr(msg, "tool_calls"):
                    final_verdict = msg.content
                    print("\n" + "=" * 85)
                    print("           YOUR PERSONAL STOCK VERDICT")
                    print("=" * 85)
                    print(final_verdict)
                    print("=" * 85 + "\n")

            if final_verdict:
                safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in user_input)[:25]
                own_status = "OWNED" if owns else "NOT_OWNED"
                filename = f"outputs/{safe_name.upper()}_{own_status}_VERDICT_{datetime.now().strftime('%d-%m-%Y_%H%M')}.md"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"# PERSONAL VERDICT: {user_input.upper()}\n")
                    f.write(f"# Owns stock: {'YES' if owns else 'NO'}\n")
                    f.write(f"# Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}\n\n")
                    f.write(final_verdict)
                print(f"Personal verdict saved → {filename}\n")

            print("─" * 90 + "\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print("Temporary issue. Try again.")


if __name__ == "__main__":
    main()