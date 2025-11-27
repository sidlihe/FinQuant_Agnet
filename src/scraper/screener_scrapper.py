# src/scraper/screener_scraper.py
import os
import json
import time
import re
import logging
from typing import Dict, Any

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def extract_numeric_value(text):
    if not text or str(text).strip() in {"", "-", "NA"}:
        return None
    cleaned = str(text).replace(",", "").replace(" ", "").strip()
    if "%" in cleaned:
        try:
            return float(cleaned.replace("%", "")) / 100
        except:
            return None
    try:
        return float(cleaned) if "." in cleaned else int(cleaned)
    except:
        return cleaned


DEFAULT_DRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "chromedriver-win64/chromedriver.exe")


class ScreenerScraper:
    def __init__(self, chromedriver_path: str = DEFAULT_DRIVER_PATH, headless: bool = True):
        self.driver = None
        self.wait = None
        self.chromedriver_path = chromedriver_path
        self.headless = headless
        self.query_used = None  # Store original user query

    def start(self):
        logger.info("Starting headless Chrome...")
        service = Service(self.chromedriver_path)
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])

        try:
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 20)
        except Exception as exc:
            logger.error(f"Unable to start ChromeDriver at {self.chromedriver_path}: {exc}")
            raise

    def search_company(self, query: str):
        self.query_used = query.strip()  # Save original query
        logger.info(f"Searching: {query}")
        if not self.driver:
            raise RuntimeError("Driver not started. Call start() before search.")

        self.driver.get("https://www.screener.in/")
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "home-search")))
        home_search = self.driver.find_element(By.CLASS_NAME, "home-search")
        search_box = home_search.find_element(By.CSS_SELECTOR, "input[aria-label='Search for a company']")

        self.driver.execute_script("arguments[0].focus();", search_box)
        self.driver.execute_script("arguments[0].value = arguments[1];", search_box, query)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", search_box)
        search_box.send_keys(Keys.RETURN)

        self.wait.until(EC.presence_of_element_located((By.ID, "profit-loss")))
        self.wait.until(EC.presence_of_element_located((By.ID, "analysis")))
        logger.info("Company page loaded")

    def get_company_name(self) -> str:
        try:
            return self.driver.find_element(By.TAG_NAME, "h1").text.strip()
        except:
            return self.query_used or "Unknown_Company"

    def get_safe_filename(self) -> str:
        """
        Generate predictable, clean filename using:
        1. Original user query (e.g., 'irfc', 'TCS', 'hdfc bank')
        2. Fallback to h1 if query is too generic
        3. Always append date in DD-MM-YYYY format
        """
        base = self.query_used or "stock"
        clean = re.sub(r"[^\w\s\-]", "", base, flags=re.UNICODE).strip()
        clean = re.sub(r"\s+", "_", clean)
        if not clean or len(clean) < 2:
            clean = self.get_company_name().split()[0]  # e.g., "Indian" → from full name

        date_str = time.strftime("%d-%m-%Y")  # ← DD-MM-YYYY as you wanted
        return f"{clean.upper()}_{date_str}"

    def _extract_table(self, section_id: str) -> Dict:
        try:
            table = self.driver.find_element(By.CSS_SELECTOR, f"#{section_id} table")
            headers = [th.text.strip() for th in table.find_elements(By.TAG_NAME, "th")[1:]]
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            data = {}
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if cells:
                    key = cells[0].text.strip()
                    if key and "Raw PDF" not in key:
                        values = [extract_numeric_value(c.text) for c in cells[1:]]
                        data[key] = dict(zip(headers, values))
            return data
        except Exception as e:
            logger.warning(f"{section_id} → skipped")
            return {}

    def _extract_shareholding(self) -> Dict:
        try:
            data = {"quarterly": {}, "yearly": {}}
            for period, tab_id in [("quarterly", "quarterly-shp"), ("yearly", "yearly-shp")]:
                table = self.driver.find_element(By.ID, tab_id).find_element(By.TAG_NAME, "table")
                headers = [th.text.strip() for th in table.find_elements(By.TAG_NAME, "th")[1:]]
                rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if cells and not cells[0].text.strip().startswith("No. of Shareholders"):
                        key = cells[0].text.strip()
                        values = [extract_numeric_value(c.text) for c in cells[1:]]
                        data[period][key] = dict(zip(headers, values))
            return data
        except:
            return {"quarterly": {}, "yearly": {}}

    def _extract_analysis(self) -> Dict:
        try:
            pros = [li.text.strip() for li in self.driver.find_elements(By.CSS_SELECTOR, "#analysis .pros li")]
            cons = [li.text.strip() for li in self.driver.find_elements(By.CSS_SELECTOR, "#analysis .cons li")]
            return {"pros": pros, "cons": cons}
        except:
            return {"pros": [], "cons": []}

    def extract_all(self) -> Dict[str, Any]:
        logger.info("Extracting all data...")
        return {
            "metadata": {
                "company": self.get_company_name(),
                "user_query": self.query_used,
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "url": self.driver.current_url
            },
            "quarters": self._extract_table("quarters"),
            "profit_loss": self._extract_table("profit-loss"),
            "balance_sheet": self._extract_table("balance-sheet"),
            "shareholding": self._extract_shareholding(),
            "analysis": self._extract_analysis()
        }

    def save_data(self, data: Dict, folder: str = "info_json") -> list:
        os.makedirs(folder, exist_ok=True)
        base_name = self.get_safe_filename()  # ← Clean, predictable name

        saved = []
        sections = ["quarters", "profit_loss", "balance_sheet", "shareholding", "analysis"]
        for sec in sections:
            path = os.path.join(folder, f"{base_name}_{sec}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data[sec], f, indent=2, ensure_ascii=False)
            saved.append(path)

        full_path = os.path.join(folder, f"{base_name}_FULL.json")
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        saved.append(full_path)

        logger.info(f"Data saved → {base_name} (DD-MM-YYYY format)")
        return saved

    def quit(self):
        if self.driver:
            self.driver.quit()