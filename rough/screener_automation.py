#rough/screener_automation.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import json
import os
import time
import re

def ensure_info_json_folder():
    """Create info_json folder if it doesn't exist"""
    folder_path = "info_json"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def extract_numeric_value(text):
    """Extract numeric value from text, handling commas and percentages"""
    if not text or text.strip() == '' or text == '-':
        return None
    
    text = str(text).strip()
    
    # Remove commas and spaces
    text = text.replace(',', '').replace(' ', '')
    
    # Handle empty string after cleaning
    if text == '':
        return None
    
    # Handle percentages
    if '%' in text:
        try:
            return float(text.replace('%', '')) / 100
        except (ValueError, TypeError):
            return None
    
    # Handle numeric values
    try:
        if '.' in text:
            return float(text)
        else:
            return int(text)
    except (ValueError, TypeError):
        return text

def extract_quarters_data(driver):
    """Extract quarterly results data"""
    try:
        quarters_section = driver.find_element(By.ID, "quarters")
        table = quarters_section.find_element(By.TAG_NAME, "table")
        
        # Extract headers (quarters)
        headers = [th.text for th in table.find_elements(By.TAG_NAME, "th")[1:]]  # Skip first empty header
        
        # Extract rows data
        quarters_data = {}
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
        
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) > 0:
                metric_name = cells[0].text.strip()
                if metric_name and not metric_name.startswith("Raw PDF"):
                    values = [cell.text for cell in cells[1:]]
                    
                    # Convert to proper data types
                    processed_values = []
                    for val in values:
                        processed_val = extract_numeric_value(val)
                        processed_values.append(processed_val)
                    
                    quarters_data[metric_name] = dict(zip(headers, processed_values))
        
        return quarters_data
    except Exception as e:
        print(f"Error extracting quarters data: {e}")
        return {}

def extract_profit_loss_data(driver):
    """Extract profit and loss data"""
    try:
        pl_section = driver.find_element(By.ID, "profit-loss")
        table = pl_section.find_element(By.TAG_NAME, "table")
        
        # Extract headers (years)
        headers = [th.text for th in table.find_elements(By.TAG_NAME, "th")[1:]]  # Skip first empty header
        
        # Extract rows data
        profit_loss_data = {}
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
        
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) > 0:
                metric_name = cells[0].text.strip()
                if metric_name:
                    values = []
                    for cell in cells[1:]:
                        cell_text = cell.text.strip()
                        # Handle empty cells gracefully
                        if cell_text == '' or cell_text == '-':
                            values.append(None)
                        else:
                            values.append(cell_text)
                    
                    # Convert to proper data types
                    processed_values = []
                    for val in values:
                        if val is None:
                            processed_values.append(None)
                        else:
                            processed_val = extract_numeric_value(val)
                            processed_values.append(processed_val)
                    
                    profit_loss_data[metric_name] = dict(zip(headers, processed_values))
        
        # Extract growth metrics
        growth_data = {}
        try:
            ranges_tables = pl_section.find_elements(By.CLASS_NAME, "ranges-table")
            
            for table in ranges_tables:
                title = table.find_element(By.TAG_NAME, "th").text
                growth_data[title] = {}
                
                rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) == 2:
                        period = cells[0].text.replace(':', '').strip()
                        value = extract_numeric_value(cells[1].text)
                        growth_data[title][period] = value
        except Exception as e:
            print(f"Error extracting growth metrics: {e}")
        
        return {
            "annual_data": profit_loss_data,
            "growth_metrics": growth_data
        }
    except Exception as e:
        print(f"Error extracting profit loss data: {e}")
        return {}

def extract_balance_sheet_data(driver):
    """Extract balance sheet data"""
    try:
        bs_section = driver.find_element(By.ID, "balance-sheet")
        table = bs_section.find_element(By.TAG_NAME, "table")
        
        # Extract headers (years)
        headers = [th.text for th in table.find_elements(By.TAG_NAME, "th")[1:]]  # Skip first empty header
        
        # Extract rows data
        balance_sheet_data = {}
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
        
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) > 0:
                metric_name = cells[0].text.strip()
                if metric_name:
                    values = [cell.text for cell in cells[1:]]
                    
                    # Convert to proper data types
                    processed_values = []
                    for val in values:
                        processed_val = extract_numeric_value(val)
                        processed_values.append(processed_val)
                    
                    balance_sheet_data[metric_name] = dict(zip(headers, processed_values))
        
        return balance_sheet_data
    except Exception as e:
        print(f"Error extracting balance sheet data: {e}")
        return {}

def extract_shareholding_data(driver):
    """Extract shareholding pattern data"""
    try:
        shp_section = driver.find_element(By.ID, "shareholding")
        
        shareholding_data = {
            "quarterly": {},
            "yearly": {}
        }
        
        # Extract quarterly data
        quarterly_tab = shp_section.find_element(By.ID, "quarterly-shp")
        quarterly_table = quarterly_tab.find_element(By.TAG_NAME, "table")
        
        # Quarterly headers
        q_headers = [th.text for th in quarterly_table.find_elements(By.TAG_NAME, "th")[1:]]
        
        # Quarterly rows
        q_rows = quarterly_table.find_elements(By.CSS_SELECTOR, "tbody tr")
        for row in q_rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) > 0:
                holder_type = cells[0].text.strip()
                if holder_type and not holder_type.startswith("No. of Shareholders"):
                    values = [extract_numeric_value(cell.text) for cell in cells[1:]]
                    shareholding_data["quarterly"][holder_type] = dict(zip(q_headers, values))
        
        # Extract yearly data
        yearly_tab = shp_section.find_element(By.ID, "yearly-shp")
        yearly_table = yearly_tab.find_element(By.TAG_NAME, "table")
        
        # Yearly headers
        y_headers = [th.text for th in yearly_table.find_elements(By.TAG_NAME, "th")[1:]]
        
        # Yearly rows
        y_rows = yearly_table.find_elements(By.CSS_SELECTOR, "tbody tr")
        for row in y_rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) > 0:
                holder_type = cells[0].text.strip()
                if holder_type and not holder_type.startswith("No. of Shareholders"):
                    values = [extract_numeric_value(cell.text) for cell in cells[1:]]
                    shareholding_data["yearly"][holder_type] = dict(zip(y_headers, values))
        
        return shareholding_data
    except Exception as e:
        print(f"Error extracting shareholding data: {e}")
        return {}

def extract_analysis_data(driver):
    """Extract pros and cons analysis"""
    try:
        analysis_section = driver.find_element(By.ID, "analysis")
        
        analysis_data = {
            "pros": [],
            "cons": []
        }
        
        # Extract pros
        pros_section = analysis_section.find_element(By.CLASS_NAME, "pros")
        pros_items = pros_section.find_elements(By.TAG_NAME, "li")
        analysis_data["pros"] = [item.text for item in pros_items]
        
        # Extract cons
        cons_section = analysis_section.find_element(By.CLASS_NAME, "cons")
        cons_items = cons_section.find_elements(By.TAG_NAME, "li")
        analysis_data["cons"] = [item.text for item in cons_items]
        
        return analysis_data
    except Exception as e:
        print(f"Error extracting analysis data: {e}")
        return {}

def save_json_data(folder_path, filename, data):
    """Save data as JSON file"""
    file_path = os.path.join(folder_path, f"{filename}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved: {file_path}")

def main():
    # Setup Chrome driver
    service = Service(r"C:\Users\SiddheshLihe\Gemini-Retail-Agent\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    
    wait = WebDriverWait(driver, 20)
    folder_path = ensure_info_json_folder()
    
    try:
        # Navigate to screener.in
        driver.get("https://www.screener.in/")
        
        # Wait for page to load
        time.sleep(3)
        
        # Search for IRFC
        home_search = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "home-search"))
        )
        
        # Then find the input within that container
        search_box = home_search.find_element(By.CSS_SELECTOR, "input[aria-label='Search for a company']")
        
        # Use JavaScript to focus and set value
        driver.execute_script("arguments[0].focus();", search_box)
        driver.execute_script("arguments[0].value = 'IRFC';", search_box)
        
        # Trigger input events
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", search_box)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', {bubbles: true}));", search_box)
        
        # Press Enter
        search_box.send_keys(Keys.RETURN)
        
        print("Search completed successfully!")
        
        # Wait for company page to load
        print("Waiting for company page to load...")
        time.sleep(5)
        
        # Extract all data sections
        print("Extracting quarterly results...")
        quarters_data = extract_quarters_data(driver)
        save_json_data(folder_path, "quarterly_results", quarters_data)
        
        print("Extracting profit & loss data...")
        profit_loss_data = extract_profit_loss_data(driver)
        save_json_data(folder_path, "profit_loss", profit_loss_data)
        
        print("Extracting balance sheet data...")
        balance_sheet_data = extract_balance_sheet_data(driver)
        save_json_data(folder_path, "balance_sheet", balance_sheet_data)
        
        print("Extracting shareholding pattern...")
        shareholding_data = extract_shareholding_data(driver)
        save_json_data(folder_path, "shareholding", shareholding_data)
        
        print("Extracting analysis...")
        analysis_data = extract_analysis_data(driver)
        save_json_data(folder_path, "analysis", analysis_data)
        
        print("\nAll data has been successfully extracted and saved!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Close the browser
        time.sleep(2)
        driver.quit()

if __name__ == "__main__":
    main()