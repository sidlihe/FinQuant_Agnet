# test_tools.py
import os
import sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# from src.scraper.screener_scrapper import ScreenerScraper

from src.tools import resolve_stock_identity_local, ultimate_stock_verdict

# Test if tools work
print("Testing stock identity resolver...")
try:
    identity = resolve_stock_identity_local("SJVN")
    print(f"✓ Identity resolved: {identity}")
    
    print("Testing ultimate_stock_verdict...")
    result = ultimate_stock_verdict.invoke({
        "screener_name": identity["screener_name"],
        "yfinance_ticker": identity["yfinance_ticker"]
    })
    print(f"✓ Tool executed successfully")
    print(f"Result length: {len(result)}")
    
except Exception as e:
    print(f"✗ Tool failed: {e}")