# simple_advisor.py - DIRECT RECOMMENDATION ENGINE
import os
import sys
import json
import re
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from logger import logger
from src.config import Config
from src.tools import resolve_stock_identity_local, ultimate_stock_verdict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

def clear_folders():
    folders = ["./info_json", "./outputs"]
    for folder in folders:
        if not os.path.exists(folder):
            continue
        try:
            for file in os.listdir(folder):
                if file.endswith(('.json', '.md')):
                    os.remove(os.path.join(folder, file))
        except Exception as e:
            logger.error(f"Failed to clear {folder}: {e}")

def ask_user(prompt: str) -> str:
    return input(f"{prompt} ").strip()

def ask_yes_no(prompt: str) -> bool:
    while True:
        ans = input(f"{prompt} (y/n): ").strip().lower()
        if ans in {"y", "yes", "1", "yep"}:
            return True
        if ans in {"n", "no", "0", "nope"}:
            return False
        print("Please type y or n")

def ask_float(prompt: str) -> float:
    while True:
        val = input(f"{prompt} ").strip().replace("₹", "").replace(",", "")
        try:
            return float(val)
        except:
            print("Enter a valid number (e.g. 135.5)")

def get_recommendation_llm():
    """Initialize simple LLM for recommendations only"""
    try:
        Config.require_api_key()
        llm = ChatGoogleGenerativeAI(
            model=Config.MODEL_NAME,
            temperature=0.0,
            google_api_key=Config.GOOGLE_API_KEY,
            convert_system_message_to_human=True,
            max_retries=2
        )
        return llm
    except Exception as e:
        logger.error(f"LLM init failed: {e}")
        return None

def analyze_stock_data(stock_data: dict, owns_stock: bool, buy_price: float = 0) -> str:
    """Generate recommendation from stock data"""
    
    llm = get_recommendation_llm()
    if not llm:
        return "Error: Cannot initialize recommendation engine"
    
    # Extract key data
    technical_report = stock_data.get('technical_report', '')
    fundamental = stock_data.get('fundamental_snapshot', '')
    metadata = stock_data.get('metadata', {})
    
    # Parse technical data for current price
    current_price = 0
    price_match = re.search(r"Today['']?s?\s+Open\s*:\s*₹?\s*([0-9,]+\.?[0-9]*)", technical_report, re.IGNORECASE)
    if price_match:
        current_price = float(price_match.group(1).replace(",", ""))
    
    # Build analysis prompt
    if owns_stock and buy_price > 0:
        pl_percent = ((current_price - buy_price) / buy_price * 100) if current_price > 0 else 0
        prompt = f"""
You are a ruthless Indian fund manager. Analyze this stock for an EXISTING HOLDER and give specific advice.

STOCK: {metadata.get('company_name', 'N/A')}
CURRENT PRICE: ₹{current_price:,.2f}
BUY PRICE: ₹{buy_price:,.2f}
P/L: {pl_percent:+.1f}%

TECHNICAL ANALYSIS:
{technical_report}

FUNDAMENTAL SNAPSHOT:
{fundamental}

GIVE SPECIFIC RECOMMENDATION IN THIS EXACT FORMAT:

**VERDICT** → HOLD | BOOK PROFIT | SELL | AVERAGE DOWN

**Confidence** → High | Medium | Low

**Action Plan**:
- **Current Position**: Hold {buy_price} | Exit completely | Average down
- **Stop Loss**: ₹_____
- **Price Target**: ₹_____ - ₹_____
- **Time Frame**: 1-3 months

**Key Reasons**:
• [Based on technicals]
• [Based on fundamentals] 
• [Risk assessment]

**Risk Level** → Low | Medium | High

Be brutally honest. Use numbers from the data."""
    else:
        prompt = f"""
You are a ruthless Indian fund manager. Analyze this stock for a NEW BUYER and give specific advice.

STOCK: {metadata.get('company_name', 'N/A')}
CURRENT PRICE: ₹{current_price:,.2f}

TECHNICAL ANALYSIS:
{technical_report}

FUNDAMENTAL SNAPSHOT:
{fundamental}

GIVE SPECIFIC RECOMMENDATION IN THIS EXACT FORMAT:

**VERDICT** → STRONG BUY | BUY | AVOID | STRONG SELL

**Confidence** → High | Medium | Low

**Entry Strategy**:
- **Buy Zone**: ₹_____ - ₹_____
- **Stop Loss**: ₹_____
- **Target**: ₹_____ - ₹_____
- **Time Frame**: 1-3 months

**Key Reasons**:
• [Based on technicals]
• [Based on fundamentals]
• [Risk assessment]

**Risk Level** → Low | Medium | High

Be brutally honest. Use numbers from the data."""
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content
    except Exception as e:
        return f"Error generating recommendation: {e}"

def main():
    Config.ensure_dirs()
    clear_folders()
    
    print("\n" + "═" * 80)
    print("           SIMPLE STOCK ADVISOR - DIRECT RECOMMENDATIONS")
    print("═" * 80)
    print("No complex agents • Direct analysis • Clear recommendations\n")
    
    while True:
        try:
            print("Which stock to analyze?")
            user_input = ask_user("Stock name (or 'quit'):").strip()
            if user_input.lower() in {"quit", "exit", "q"}:
                break

            # Step 1: Resolve stock identity
            print("🔍 Resolving stock...")
            identity = resolve_stock_identity_local(user_input)
            print(f"✅ Found: {identity['screener_name']} | {identity['yfinance_ticker']}")
            
            if not ask_yes_no("Is this correct?"):
                identity["screener_name"] = ask_user("Correct name:") or identity["screener_name"]
                identity["yfinance_ticker"] = ask_user("Correct ticker:") or identity["yfinance_ticker"]

            # Step 2: Fetch data using tool
            print("📊 Fetching stock data...")
            tool_result = ultimate_stock_verdict.invoke({
                "screener_name": identity["screener_name"],
                "yfinance_ticker": identity["yfinance_ticker"]
            })
            stock_data = json.loads(tool_result)
            print("✅ Data fetched successfully")

            # Step 3: Get user position
            owns_stock = ask_yes_no("\nDo you own this stock?")
            buy_price = 0
            if owns_stock:
                buy_price = ask_float("Your buy price (₹):")

            # Step 4: Generate recommendation
            print("\n🤔 Analyzing data and generating recommendation...")
            recommendation = analyze_stock_data(stock_data, owns_stock, buy_price)
            
            print("\n" + "═" * 80)
            print("                    FINAL RECOMMENDATION")
            print("═" * 80)
            print(recommendation)
            print("═" * 80)

            # Step 5: Save report
            safe_name = "".join(c if c.isalnum() else "_" for c in user_input.upper())
            status = "OWNED" if owns_stock else "NOT_OWNED"
            filename = f"outputs/{safe_name}_{status}_{datetime.now().strftime('%d-%b-%Y_%H%M')}.md"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"# RECOMMENDATION: {user_input.upper()}\n")
                f.write(f"# Date: {datetime.now().strftime('%d %B %Y %H:%M')}\n")
                f.write(f"# Position: {'OWNING' if owns_stock else 'NOT OWNING'}\n")
                if owns_stock:
                    f.write(f"# Buy Price: ₹{buy_price:,.2f}\n")
                f.write("\n" + recommendation)
            
            print(f"\n💾 Saved: {filename}")
            print("\n" + "=" * 80 + "\n")

        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"❌ Error: {e}")
            print("🔄 Restarting...\n")
            continue

if __name__ == "__main__":
    main()