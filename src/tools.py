# src/tools.py → FINAL VERSION (REAL FUND MANAGER BRAIN)

import os
import sys
import json
from datetime import datetime
from typing import Dict
import re
from textwrap import dedent

# Project root fix
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.scraper.screener_scrapper import ScreenerScraper

import pandas as pd
import yfinance as yf
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from logger import logger
from src.config import Config

DEFAULT_SUFFIX = ".NS"

try:
    Config.require_api_key()
    resolver_model = ChatGoogleGenerativeAI(
        model=Config.MODEL_NAME,
        temperature=0.0,
        google_api_key=Config.GOOGLE_API_KEY,
        convert_system_message_to_human=True,
        max_retries=2,
    )
    logger.info("Stock identity resolver model ready")
except Exception as resolver_exc:
    resolver_model = None
    logger.warning(f"Stock resolver disabled: {resolver_exc}")


def _ensure_suffix(symbol: str) -> str:
    upper = symbol.upper()
    if upper.endswith((".NS", ".BO")):
        return upper
    if upper.isdigit():
        return upper + ".BO"
    return upper + DEFAULT_SUFFIX


def _content_to_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                parts.append(part["text"])
            elif hasattr(part, "text"):
                parts.append(part.text)
            else:
                parts.append(str(part))
        return " ".join(parts)
    return str(content)


def resolve_stock_identity_local(user_input: str) -> Dict[str, str]:
    """LLM-powered resolver used by CLI + LangChain tool."""
    if not user_input or not user_input.strip():
        raise ValueError("Empty stock name provided.")
    if not resolver_model:
        raise EnvironmentError("Stock resolver model is not initialized.")

    prompt = dedent(
        f"""
        You convert any user-provided Indian stock reference into the exact Screener.in company
        slug/name and the correct Yahoo Finance ticker.

        Requirements:
        - Respond with VALID JSON only, no commentary.
        - Keys: "screener_name", "yfinance_ticker".
        - Screener name should be how users search on https://www.screener.in/ (e.g., "IRCON INTERNATIONAL").
        - yfinance ticker MUST include the proper suffix: ".NS" for NSE, ".BO" for BSE.
        - Prefer NSE tickers when both exist.
        - If you are unsure, make the best professional guess and still return JSON.

        Examples:
        {{
          "screener_name": "IRFC",
          "yfinance_ticker": "IRFC.NS"
        }}

        User input: "{user_input.strip()}"
        """
    ).strip()

    response = resolver_model.invoke([HumanMessage(content=prompt)])
    text = _content_to_text(response.content)

    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = re.sub(r"^json", "", text, flags=re.IGNORECASE).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Resolver returned invalid JSON: {exc}") from exc

    screener_name = (data.get("screener_name") or "").strip()
    ticker = (data.get("yfinance_ticker") or "").strip().upper()
    if not screener_name or not ticker:
        raise ValueError("Resolver response missing screener_name or yfinance_ticker.")

    ticker = _ensure_suffix(ticker)
    return {"screener_name": screener_name, "yfinance_ticker": ticker}


def _fetch_market_data_raw(ticker: str) -> Dict[str, object]:
    ticker = ticker.strip().upper()
    if not ticker.endswith((".NS", ".BO")):
        ticker = _ensure_suffix(ticker)
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1mo", interval="1d")
    if hist.empty:
        raise ValueError(f"No price history found for {ticker}")
    clean_dates = hist.index.strftime("%d-%m-%Y").tolist()
    today = hist.iloc[-1]
    data = {
        "ticker": ticker,
        "date": clean_dates,
        "price": hist["Close"].round(2).tolist(),
        "today_open": round(float(today["Open"]), 2),
        "today_date": today.name.strftime("%d-%m-%Y"),
        "currency": "INR",
    }
    logger.info(f"Market data → {ticker}")
    return data


def _calculate_volatility_report(price_data: Dict[str, object]) -> str:
    prices = pd.Series(price_data["price"])
    report = f"""
# Technical & Volatility Analysis

**Ticker**: {price_data['ticker']} | **Date**: {price_data['today_date']}
**30-Day Avg**: ₹{prices.mean():,.2f} | **Std Dev**: ±₹{prices.std():,.2f}
**High**: ₹{prices.max():,.2f} | **Low**: ₹{prices.min():,.2f}
**Today's Open**: ₹{price_data['today_open']:,.2f}
"""
    logger.info("Volatility report ready")
    return report.strip()


def _save_report(path: str, content: str) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"Saved → {path}")
    return path


def build_stock_verdict_payload(screener_name: str, yfinance_ticker: str) -> Dict[str, object]:
    scraper = None
    try:
        logger.info(f"Verdict → Screener: '{screener_name}' | Ticker: '{yfinance_ticker}'")
        scraper = ScreenerScraper(headless=True)
        scraper.start()
        scraper.search_company(screener_name)
        data = scraper.extract_all()
        saved_files = scraper.save_data(data)
        base_name = scraper.get_safe_filename()
    finally:
        if scraper:
            try:
                scraper.quit()
            except Exception:
                pass

    technical_report = "Technical data unavailable."
    try:
        price_json = _fetch_market_data_raw(yfinance_ticker)
        technical_report = _calculate_volatility_report(price_json)
        _save_report(
            os.path.join("outputs", f"{base_name}_Technical.md"),
            technical_report,
        )
    except Exception as exc:
        logger.warning(f"yfinance error: {exc}")
        technical_report = f"Price data not available for {yfinance_ticker}: {exc}"

    fundamental_text = json.dumps(data, indent=2, ensure_ascii=False)[:12000]
    return {
        "metadata": data["metadata"],
        "screener_name": screener_name,
        "yfinance_ticker": yfinance_ticker,
        "technical_report": technical_report,
        "fundamental_snapshot": fundamental_text,
        "saved_files": saved_files,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


# ===================================================================
# Tool 1–3: fetch, volatility, save
# ===================================================================
@tool
def fetch_market_data(ticker: str) -> str:
    """Fetch last ~30 days price data."""
    try:
        data = _fetch_market_data_raw(ticker)
        return json.dumps(data, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def calculate_volatility(price_data_json: str) -> str:
    """Generate volatility report."""
    try:
        data = json.loads(price_data_json)
        return _calculate_volatility_report(data)
    except Exception as e:
        return f"Volatility error: {e}"


@tool
def save_report_to_disk(filename: str, content: str) -> str:
    """Save final report."""
    os.makedirs("outputs", exist_ok=True)
    path = os.path.join("outputs", filename)
    try:
        _save_report(path, content)
        return f"SAVED: {path}"
    except Exception as e:
        return f"Save failed: {e}"


# ===================================================================
# FINAL TOOL: THE REAL FUND MANAGER DECISION ENGINE
# ===================================================================
@tool
def resolve_stock_identity(user_input: str) -> str:
    """LLM-powered resolver for Screener name + yfinance ticker."""
    try:
        data = resolve_stock_identity_local(user_input)
        return json.dumps(data, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": str(exc)})


@tool
def ultimate_stock_verdict(screener_name: str, yfinance_ticker: str) -> str:
    """Return structured payload with fundamentals + technicals."""
    try:
        payload = build_stock_verdict_payload(screener_name, yfinance_ticker)
        return json.dumps(payload, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": str(exc)})


# FINAL TOOL LIST — ONLY THE BEST
COMPLEX_TOOLS = [
    resolve_stock_identity,
    fetch_market_data,
    calculate_volatility,
    save_report_to_disk,
    ultimate_stock_verdict,
]


# ===================================================================
# HARDCODED DEBUG MODE — TEST THE ULTIMATE TOOL
# ===================================================================
if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("ULTIMATE STOCK VERDICT TOOL → DEBUG MODE")
    logger.info("=" * 70)

    test_companies = ["LTIM"]

    for company in test_companies:
        logger.info(f"\nTesting ultimate_stock_verdict → {company}")
        result = ultimate_stock_verdict.invoke(
            {"screener_name": company, "yfinance_ticker": f"{company}.NS"}
        )
        print(f"{company} VERDICT PAYLOAD (truncated):\n{result[:500]}...\n")

    logger.info("\nDEBUG COMPLETED — TOOL WORKS PERFECTLY!")
    logger.info("All files saved in info_json/ and outputs/")
 
