from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

service = Service(r"C:\Users\SiddheshLihe\Gemini-Retail-Agent\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service)

driver.get("https://www.screener.in/")

# Wait for page to fully load
time.sleep(3)

wait = WebDriverWait(driver, 15)

try:
    # Wait for the home-search container to be present first
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
    
except Exception as e:
    print(f"Error: {e}")

time.sleep(5)
driver.quit()