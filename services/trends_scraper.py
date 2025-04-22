import time
import pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import Logger

class TrendsScraper:
    """Class to scrape trending topics from Google Trends"""
    
    def __init__(self, driver_path=None):
        """
        Initialize the trends scraper with optional driver path
        
        Args:
            driver_path (str, optional): Path to the Chrome driver executable
        """
        self.logger = Logger(__name__)
        self.driver_path = driver_path
        self.trending_topics = []
        
    def _initialize_driver(self):
        """Initialize and return a Chrome webdriver"""
        try:
            if self.driver_path:
                service = Service(executable_path=self.driver_path)
                driver = webdriver.Chrome(service=service)
            else:
                # Use default driver location if not specified
                driver = webdriver.Chrome()
                
            return driver
        except Exception as e:
            self.logger.error(f"Failed to initialize webdriver: {e}")
            raise
    
    def get_trending_topics(self):
        """
        Scrape and return the current trending topics from Google Trends
        
        Returns:
            list: List of trending topics
        """
        self.logger.info("Fetching trending topics from Google Trends")
        driver = None
        
        try:
            driver = self._initialize_driver()
            driver.get("https://trends.google.com/trending?geo=US")
            
            # Add longer waits for better reliability
            wait = WebDriverWait(driver, 30)
            
            # Wait for the main Export button to be clickable and click it
            self.logger.debug("Looking for Export button...")
            export_button = wait.until(EC.element_to_be_clickable((By.XPATH, 
                "//button[.//span[contains(text(), 'Export')] or .//span[@jsname='V67aGc' and contains(text(), 'Export')]]")))
            
            self.logger.debug("Clicking Export button...")
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
                self.logger.debug(f"Trying selector: {selector}")
                try:
                    # Check if the element exists and is visible
                    elements = driver.find_elements(By.XPATH, selector)
                    if elements:
                        self.logger.debug(f"Found {len(elements)} elements with selector {selector}")
                        for i, elem in enumerate(elements):
                            if elem.is_displayed():
                                self.logger.debug(f"Element {i} is displayed, clicking it...")
                                elem.click()
                                clipboard_option = elem
                                break
                    if clipboard_option:
                        break
                except Exception as e:
                    self.logger.debug(f"Error with selector {selector}: {e}")
            
            if not clipboard_option:
                self.logger.warning("Could not find clipboard option with any selector. Taking screenshot for debugging...")
                driver.save_screenshot("debug_screenshot.png")
                # Try JavaScript click as a last resort
                self.logger.debug("Attempting JavaScript click...")
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
            trending_content = pyperclip.paste()
            
            # Process the clipboard content into a list of trending topics
            self.trending_topics = self._process_trending_content(trending_content)
            self.logger.info(f"Retrieved {len(self.trending_topics)} trending topics")
            
            # Save to file for reference
            with open("trending_topics.txt", "w", encoding="utf-8") as f:
                f.write(trending_content)
                
            return self.trending_topics

        except Exception as e:
            self.logger.error(f"Error occurred while scraping trending topics: {e}")
            if driver:
                driver.save_screenshot("error_screenshot.png")
            return []
            
        finally:
            # Close the browser
            if driver:
                driver.quit()
    
    def _process_trending_content(self, content):
        """
        Process clipboard content into a list of trending topics
        
        Args:
            content (str): Raw clipboard content from Google Trends
            
        Returns:
            list: Processed list of trending topics
        """
        # Basic processing - split by newlines and filter empty strings
        # This may need adjustment based on the actual format of the clipboard data
        if not content or content.strip() == "":
            return []
            
        topics = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Filter out any headers or non-topic content
        # This depends on the exact format of the clipboard content
        # You may need to adjust this filtering logic
        filtered_topics = []
        for topic in topics:
            # Skip header lines or metadata
            if topic.startswith("Google Trends") or ":" in topic:
                continue
            # Skip any numeric-only entries which might be ranks
            if topic.isdigit():
                continue
            filtered_topics.append(topic)
            
        return filtered_topics
    
    def get_best_trending_topic(self):
        """
        Return the best trending topic (currently simply returns the first topic)
        
        Returns:
            str: Best trending topic or empty string if none available
        """
        # If we haven't fetched topics yet, do so now
        if not self.trending_topics:
            self.get_trending_topics()
            
        # Return the first topic as the "best" one
        # This could be enhanced with more sophisticated selection logic
        if self.trending_topics:
            self.logger.info(f"Selected best trending topic: {self.trending_topics[0]}")
            return self.trending_topics[0]
        else:
            self.logger.warning("No trending topics available")
            return ""