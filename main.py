# main.py - PROFESSIONAL WORKING VERSION
import os
import sys
import json
import re
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logger import logger
from src.config import Config
from src.tools import resolve_stock_identity_local, ultimate_stock_verdict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

def clear_folders():
    """Clear previous analysis files"""
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
    """Initialize LLM for professional recommendations"""
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

def generate_professional_recommendation(stock_data: dict, owns_stock: bool, buy_price: float = 0) -> str:
    """Generate professional fund manager-style recommendation"""
    
    llm = get_recommendation_llm()
    if not llm:
        return "Error: Cannot initialize recommendation engine"
    
    # Extract data
    technical_report = stock_data.get('technical_report', '')
    fundamental = stock_data.get('fundamental_snapshot', '')
    metadata = stock_data.get('metadata', {})
    
    # Parse current price
    current_price = 0
    price_match = re.search(r"Today['']?s?\s+Open\s*:\s*₹?\s*([0-9,]+\.?[0-9]*)", technical_report, re.IGNORECASE)
    if price_match:
        current_price = float(price_match.group(1).replace(",", ""))
    
    # Professional prompt for fund manager style
    if owns_stock and buy_price > 0:
        pl_percent = ((current_price - buy_price) / buy_price * 100) if current_price > 0 else 0
        pl_status = "PROFIT" if pl_percent > 0 else "LOSS"
        
        prompt = f"""
ACT AS A RUTHLESS FUND MANAGER. Analyze this holding and give brutal, no-nonsense advice.

📊 POSITION ANALYSIS:
- Stock: {metadata.get('company_name', 'N/A')} 
- Current: ₹{current_price:,.2f} | Your Buy: ₹{buy_price:,.2f}
- P/L: {pl_percent:+.1f}% ({pl_status})
- Holding: EXISTING POSITION

📈 TECHNICALS:
{technical_report}

🏛️  FUNDAMENTALS:
{fundamental}

🎯 REQUIRED FORMAT - BE SPECIFIC:

**PORTFOLIO DECISION** → HOLD | BOOK PROFIT | CUT LOSS | AVERAGE DOWN

**CONFIDENCE** → High (80%+) | Medium (60-80%) | Low (<60%)

**ACTION PLAN**:
- Immediate Action: [HOLD/EXIT/AVERAGE]
- Stop Loss: ₹_____ (____% risk)
- Price Target: ₹_____ (____% upside)
- Time Horizon: [1-3 months | 3-6 months | 6-12 months]

**QUANTITATIVE RATIONALE**:
1. [Technical reason with numbers]
2. [Fundamental reason with metrics] 
3. [Risk/reward assessment]

**RISK RATING** → Low | Medium | High

**PRIORITY** → High Priority | Medium Priority | Low Priority

Use exact numbers from data. No fluff. Be brutally honest about the position."""
    else:
        prompt = f"""
ACT AS A RUTHLESS FUND MANAGER. Analyze this stock and give brutal, no-nonsense entry advice.

📊 STOCK ANALYSIS:
- Stock: {metadata.get('company_name', 'N/A')}
- Current Price: ₹{current_price:,.2f}
- Position: NEW ENTRY

📈 TECHNICALS:
{technical_report}

🏛️  FUNDAMENTALS:
{fundamental}

🎯 REQUIRED FORMAT - BE SPECIFIC:

**ENTRY DECISION** → STRONG BUY | BUY | NEUTRAL | AVOID | STRONG SELL

**CONFIDENCE** → High (80%+) | Medium (60-80%) | Low (<60%)

**ENTRY STRATEGY**:
- Buy Zone: ₹_____ - ₹_____ 
- Stop Loss: ₹_____ (____% risk)
- Target: ₹_____ (____% upside)
- Position Size: [Full | Half | Quarter]
- Time Horizon: [1-3 months | 3-6 months | 6-12 months]

**QUANTITATIVE RATIONALE**:
1. [Technical setup with numbers]
2. [Fundamental strength/weakness with metrics]
3. [Market timing assessment]

**RISK RATING** → Low | Medium | High

**PRIORITY** → High Priority | Medium Priority | Low Priority

Use exact numbers from data. No fluff. Be brutally honest about the opportunity."""
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content
    except Exception as e:
        return f"Error generating recommendation: {e}"

def display_welcome():
    """Professional welcome banner"""
    print("\n" + "═" * 80)
    print("           🏛️  FINQUANT PRO - PROFESSIONAL FUND MANAGER AI")
    print("═" * 80)
    print("   Institutional-Grade Analysis • Brutally Honest • Data-Driven")
    print("═" * 80)

def main():
    Config.ensure_dirs()
    clear_folders()
    
    display_welcome()
    
    while True:
        try:
            print("\n📈 STOCK ANALYSIS MENU")
            print("────────────────────────────────────────────────────────────────")
            user_input = ask_user("Enter stock name (or 'quit' to exit):").strip()
            
            if user_input.lower() in {"quit", "exit", "q"}:
                print("\n🎯 Analysis complete. Check outputs/ folder for detailed reports.")
                break

            # Step 1: Stock Identification
            print("\n🔍 Identifying stock...")
            identity = resolve_stock_identity_local(user_input)
            print(f"✅ Identified: {identity['screener_name']} | {identity['yfinance_ticker']}")
            
            if not ask_yes_no("Proceed with this stock?"):
                identity["screener_name"] = ask_user("Enter correct name:") or identity["screener_name"]
                identity["yfinance_ticker"] = ask_user("Enter correct ticker:") or identity["yfinance_ticker"]

            # Step 2: Data Collection
            print("\n📊 Collecting market data...")
            tool_result = ultimate_stock_verdict.invoke({
                "screener_name": identity["screener_name"],
                "yfinance_ticker": identity["yfinance_ticker"]
            })
            stock_data = json.loads(tool_result)
            print("✅ Data collection complete")

            # Step 3: Position Analysis
            owns_stock = ask_yes_no("\n💼 Do you currently hold this stock?")
            buy_price = 0
            if owns_stock:
                buy_price = ask_float("Enter your average buy price (₹):")

            # Step 4: Professional Analysis
            print("\n🤔 Generating professional recommendation...")
            recommendation = generate_professional_recommendation(stock_data, owns_stock, buy_price)
            
            # Display results
            print("\n" + "═" * 80)
            print("                    🎯 PROFESSIONAL VERDICT")
            print("═" * 80)
            print(recommendation)
            print("═" * 80)

            # Step 5: Save professional report
            safe_name = "".join(c if c.isalnum() else "_" for c in user_input.upper())
            status = "HOLDING" if owns_stock else "ANALYSIS"
            timestamp = datetime.now().strftime('%d-%b-%Y_%H%M')
            filename = f"outputs/{safe_name}_{status}_{timestamp}.md"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"# PROFESSIONAL STOCK ANALYSIS: {user_input.upper()}\n")
                f.write(f"# Analysis Date: {datetime.now().strftime('%d %B %Y %H:%M')}\n")
                f.write(f"# Position: {'EXISTING HOLDER' if owns_stock else 'NEW ENTRY ANALYSIS'}\n")
                if owns_stock:
                    f.write(f"# Average Buy Price: ₹{buy_price:,.2f}\n")
                f.write(f"# Generated by: FinQuant Pro AI Fund Manager\n")
                f.write("\n" + "=" * 80 + "\n\n")
                f.write(recommendation)
            
            print(f"\n💾 Professional report saved: {filename}")
            print("────────────────────────────────────────────────────────────────")

        except Exception as e:
            logger.error(f"Analysis error: {e}")
            print(f"❌ Analysis error: {e}")
            print("🔄 Restarting analysis...\n")
            continue

if __name__ == "__main__":
    main()