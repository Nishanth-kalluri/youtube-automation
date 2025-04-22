from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pyperclip

service = Service(executable_path=r"C:\Users\the_b\youtube-automation\chromedriver.exe")
driver = webdriver.Chrome(service=service)

driver.get("https://trends.google.com/trending?geo=US")

# Add longer waits and more debugging
wait = WebDriverWait(driver, 30)  # Increase timeout to 30 seconds

try:
    # Wait for the main Export button to be clickable and click it
    print("Looking for Export button...")
    export_button = wait.until(EC.element_to_be_clickable((By.XPATH, 
        "//button[.//span[contains(text(), 'Export')] or .//span[@jsname='V67aGc' and contains(text(), 'Export')]]")))
    
    print("Clicking Export button...")
    export_button.click()
    
    # Give the dropdown some time to appear
    time.sleep(2)
    
    # Try multiple selectors for the clipboard option
    selectors = [
        # By data attribute
        "//li[@data-action='clipboard']",
        # By text content
        "//li[.//span[contains(text(), 'Copy to clipboard')]]",
        # By icon and text
        "//li[.//span[contains(text(), 'Copy to clipboard')] and .//span[contains(@class, 'google-symbols') and contains(text(), 'content_copy')]]",
        # Using the class structure from your HTML
        "//span[contains(@class, 'W7g1Rb-rymPhb-fpDzbe-fmcmS') and text()='Copy to clipboard']/ancestor::li"
    ]
    
    clipboard_option = None
    for selector in selectors:
        print(f"Trying selector: {selector}")
        try:
            # Check if the element exists and is visible
            elements = driver.find_elements(By.XPATH, selector)
            if elements:
                print(f"Found {len(elements)} elements with selector {selector}")
                for i, elem in enumerate(elements):
                    if elem.is_displayed():
                        print(f"Element {i} is displayed, clicking it...")
                        elem.click()
                        clipboard_option = elem
                        break
            if clipboard_option:
                break
        except Exception as e:
            print(f"Error with selector {selector}: {e}")
    
    if not clipboard_option:
        print("Could not find clipboard option with any selector. Taking screenshot for debugging...")
        driver.save_screenshot("debug_screenshot.png")
        # Try JavaScript click as a last resort
        print("Attempting JavaScript click...")
        driver.execute_script("""
            var items = document.querySelectorAll('li');
            for(var i=0; i<items.length; i++) {
                if(items[i].textContent.includes('Copy to clipboard')) {
                    items[i].click();
                    return true;
                }
            }
            return false;
        """)
    
    # Give the page a moment to copy the content to clipboard
    time.sleep(3)
    
    # Get the clipboard content
    trending_topics = pyperclip.paste()
    
    print("Retrieved trending topics:")
    print(trending_topics)
    
    # Save to file
    with open("trending_topics.txt", "w", encoding="utf-8") as f:
        f.write(trending_topics)

except Exception as e:
    print(f"Error occurred: {e}")
    driver.save_screenshot("error_screenshot.png")
    
finally:
    # Close the browser
    driver.quit()