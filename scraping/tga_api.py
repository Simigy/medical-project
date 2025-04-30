"""
TGA (Therapeutic Goods Administration) API Integration

This module provides functions to search the TGA medicines database using advanced
web scraping techniques with anti-CAPTCHA measures and browser automation with human-like behavior.

TGA doesn't have a public API, so we use advanced web scraping with browser emulation.
"""

import requests
import time
from datetime import datetime
from urllib.parse import quote_plus, urljoin
import json
from bs4 import BeautifulSoup
import random
import logging
import os
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("tga_api")

# Try to import browser automation
try:
    from browser_automation import BrowserAutomationManager
    BROWSER_AUTOMATION_AVAILABLE = True
except ImportError:
    try:
        # Try to import from the current directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir not in sys.path:
            sys.path.append(script_dir)
        from browser_automation import BrowserAutomationManager
        BROWSER_AUTOMATION_AVAILABLE = True
    except ImportError:
        logger.warning("Browser automation is not available. Make sure browser_automation.py is in the same directory.")
        BROWSER_AUTOMATION_AVAILABLE = False

# Try to import CAPTCHA solver
try:
    from captcha_solver import CaptchaSolver
    CAPTCHA_SOLVER_AVAILABLE = True
except ImportError:
    try:
        # Try to import from the current directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir not in sys.path:
            sys.path.append(script_dir)
        from captcha_solver import CaptchaSolver
        CAPTCHA_SOLVER_AVAILABLE = True
    except ImportError:
        logger.warning("CAPTCHA solver is not available. Make sure captcha_solver.py is in the same directory.")
        CAPTCHA_SOLVER_AVAILABLE = False

# Base URLs for TGA
TGA_SEARCH_URL = "https://www.tga.gov.au/products/consumer-medicines-information/search"
TGA_BASE_URL = "https://www.tga.gov.au"

# List of user agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]

def search_tga_medicines(query, max_results=10, min_date=None, max_date=None, retries=3, captcha_api_key=""):
    """
    Search TGA medicines database using advanced web scraping with CAPTCHA solving and browser automation

    Args:
        query (str): The search query
        max_results (int): Maximum number of results to return
        min_date (str): Minimum date in format YYYY-MM-DD
        max_date (str): Maximum date in format YYYY-MM-DD
        retries (int): Number of retries if the scraping fails
        captcha_api_key (str): API key for CAPTCHA solving service

    Returns:
        list: List of search results
    """
    logger.info(f"Searching TGA medicines database for: {query}")

    # Try browser automation first if available
    if BROWSER_AUTOMATION_AVAILABLE:
        logger.info("Using browser automation with human-like behavior")
        results = search_tga_with_browser_automation(query, max_results, min_date, max_date, captcha_api_key)
        if results:
            return results
        logger.info("Browser automation failed, falling back to traditional scraping")

    # Build the search URL
    search_url = f"{TGA_SEARCH_URL}?query={quote_plus(query)}"

    # Make the search request with retries
    for attempt in range(retries):
        try:
            logger.info(f"  Scraping attempt {attempt + 1}/{retries}")

            # Set headers to mimic a browser and rotate user agents
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0"
            }

            # Add a random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))

            # Make the request with a longer timeout
            response = requests.get(search_url, headers=headers, timeout=30)
            response.raise_for_status()

            # Check for CAPTCHA
            if "captcha" in response.text.lower() or "robot" in response.text.lower():
                logger.info("CAPTCHA detected in response, falling back to Selenium")
                return search_tga_with_selenium(query, max_results, min_date, max_date)

            # Parse the HTML results
            return parse_tga_html_results(response.text, query, max_results, min_date, max_date)

        except Exception as e:
            logger.error(f"  Error in scraping attempt {attempt + 1}: {str(e)}")
            if attempt < retries - 1:
                wait_time = 2 ** attempt + random.uniform(1, 5)  # Exponential backoff with randomization
                logger.info(f"  Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                logger.error("  All scraping attempts failed")

                # Try Selenium as a last resort
                logger.info("  Trying with Selenium as a last resort")
                return search_tga_with_selenium(query, max_results, min_date, max_date)

def search_tga_with_browser_automation(query, max_results=10, min_date=None, max_date=None, captcha_api_key=""):
    """
    Search TGA medicines database using browser automation with human-like behavior

    Args:
        query (str): The search query
        max_results (int): Maximum number of results to return
        min_date (str): Minimum date in format YYYY-MM-DD
        max_date (str): Maximum date in format YYYY-MM-DD
        captcha_api_key (str): API key for CAPTCHA solving service

    Returns:
        list: List of search results
    """
    logger.info(f"Searching TGA with browser automation for: {query}")

    # Initialize browser automation
    browser_manager = BrowserAutomationManager(captcha_api_key=captcha_api_key)

    try:
        # Create a browser instance
        browser_id = f"tga_{int(time.time())}"
        browser_manager.create_browser(browser_id, headless=False)  # Use visible browser for better CAPTCHA handling
        browser = browser_manager.get_browser(browser_id)

        if not browser:
            logger.error("Failed to create browser instance")
            return []

        # Navigate to TGA search page
        if not browser.navigate_to(TGA_SEARCH_URL):
            logger.error(f"Failed to navigate to {TGA_SEARCH_URL}")
            return []

        # Fill the search form
        search_input_selector = "input[name='query'], input[id='edit-query'], input[type='search']"
        if not browser.fill_form({search_input_selector: query}):
            logger.error("Failed to fill search form")
            return []

        # Click the search button
        search_button_selector = "button[type='submit'], input[type='submit'], .form-submit"
        if not browser.click_element(search_button_selector):
            logger.error("Failed to click search button")
            return []

        # Check for CAPTCHA
        if "captcha" in browser.get_page_source().lower() or "robot" in browser.get_page_source().lower():
            logger.info("CAPTCHA detected, attempting to solve...")

            # Try to solve the CAPTCHA
            if not browser.solve_captcha():
                logger.error("Failed to solve CAPTCHA")
                return []

            logger.info("CAPTCHA solved successfully")

        # Extract search results
        html = browser.get_page_source()

        # Parse the HTML results
        return parse_tga_html_results(html, query, max_results, min_date, max_date)

    except Exception as e:
        logger.error(f"Error in browser automation: {str(e)}")
        return []

    finally:
        # Close the browser
        browser_manager.close_all_browsers()

def parse_tga_html_results(html_content, query, max_results, min_date=None, max_date=None):
    """
    Parse HTML search results from TGA website

    Args:
        html_content (str): HTML content to parse
        query (str): The original search query
        max_results (int): Maximum number of results to return
        min_date (str): Minimum date in format YYYY-MM-DD
        max_date (str): Maximum date in format YYYY-MM-DD

    Returns:
        list: List of search results
    """
    print("  Parsing HTML search results")
    results = []

    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Check for CAPTCHA
        if "captcha" in html_content.lower() or "robot" in html_content.lower():
            print("  CAPTCHA detected, cannot proceed with scraping")
            return []

        # Find all medicine items
        medicine_items = soup.select('.view-content .views-row, .search-results .search-result')

        if not medicine_items:
            # Try alternative selectors
            medicine_items = soup.select('article, .product-item, .medicine-item')

        print(f"  Found {len(medicine_items)} potential results in HTML")

        for i, item in enumerate(medicine_items):
            if i >= max_results:
                break

            try:
                # Extract title and URL
                title_elem = item.select_one('h2 a, h3 a, .title a, .views-field-title a')
                if not title_elem:
                    continue

                title = title_elem.get_text().strip()
                url = urljoin(TGA_BASE_URL, title_elem.get('href', ''))

                # Extract date
                date_elem = item.select_one('.date, .publication-date, .views-field-field-publication-date')
                date = date_elem.get_text().strip() if date_elem else ""

                # Try to convert to YYYY-MM-DD format
                if date:
                    try:
                        # Parse various date formats
                        date_formats = [
                            "%d/%m/%Y",
                            "%Y-%m-%d",
                            "%d %B %Y"
                        ]

                        for fmt in date_formats:
                            try:
                                date_obj = datetime.strptime(date, fmt)
                                date = date_obj.strftime("%Y-%m-%d")
                                break
                            except ValueError:
                                continue
                    except Exception:
                        pass
                else:
                    # If no date found, use current date
                    date = datetime.now().strftime("%Y-%m-%d")

                # Extract snippet
                snippet_elem = item.select_one('.summary, .description, .views-field-body')
                snippet = snippet_elem.get_text().strip() if snippet_elem else ""

                if not snippet:
                    # Try to get text from the item itself
                    snippet = item.get_text().strip()
                    # Remove the title from the snippet
                    snippet = snippet.replace(title, "").strip()

                # Limit snippet length
                if len(snippet) > 300:
                    snippet = snippet[:297] + "..."

                # Extract authors/manufacturers
                authors = []
                author_elem = item.select_one('.manufacturer, .sponsor, .views-field-field-sponsor')
                if author_elem:
                    authors.append(author_elem.get_text().strip())

                # Create the result object
                result = {
                    "id": f"tga-{hash(url) % 10000}",
                    "title": title,
                    "url": url,
                    "source": "TGA - Consumer Medicines Information",
                    "date": date,
                    "snippet": snippet,
                    "authors": authors
                }

                # Filter by date if needed
                if min_date or max_date:
                    if not date:
                        # Include results without dates
                        results.append(result)
                    else:
                        try:
                            result_date = datetime.strptime(date, "%Y-%m-%d")
                            min_date_obj = datetime.strptime(min_date, "%Y-%m-%d") if min_date else datetime(1900, 1, 1)
                            max_date_obj = datetime.strptime(max_date, "%Y-%m-%d") if max_date else datetime.now()

                            if min_date_obj <= result_date <= max_date_obj:
                                results.append(result)
                        except ValueError:
                            # Include results with unparseable dates
                            results.append(result)
                else:
                    results.append(result)

            except Exception as e:
                print(f"  Error processing HTML item {i}: {str(e)}")
                continue

        print(f"  Found {len(results)} valid results from HTML parsing")
        return results

    except Exception as e:
        print(f"  Error parsing HTML: {str(e)}")
        return []

def search_tga_with_selenium(query, max_results=10, min_date=None, max_date=None, captcha_api_key="", **kwargs):
    """
    Search TGA medicines database using Selenium for browser automation
    This is a fallback method when regular scraping fails due to CAPTCHA

    Note: This function requires Selenium to be installed:
    pip install selenium webdriver-manager

    Args:
        query (str): The search query
        max_results (int): Maximum number of results to return
        min_date (str): Minimum date in format YYYY-MM-DD
        max_date (str): Maximum date in format YYYY-MM-DD

    Returns:
        list: List of search results
    """
    print(f"Searching TGA medicines database using Selenium for: {query}")

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
    except ImportError:
        print("  Selenium is not installed. Please install it with: pip install selenium webdriver-manager")
        return []

    try:
        # Set up Chrome options
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Commented out to see the browser
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
        chrome_options.add_argument("--start-maximized")  # Start with maximized window

        # Set up the driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Navigate to the search page
        search_url = f"{TGA_SEARCH_URL}?query={quote_plus(query)}"
        driver.get(search_url)

        # Wait for the results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".view-content, .search-results"))
        )

        # Get the page source
        html_content = driver.page_source

        # Close the driver
        driver.quit()

        # Parse the HTML results
        return parse_tga_html_results(html_content, query, max_results, min_date, max_date)

    except Exception as e:
        print(f"  Error using Selenium: {str(e)}")
        return []

if __name__ == "__main__":
    # Test the scraper
    results = search_tga_medicines("paracetamol", max_results=5)
    if not results:
        print("Trying with Selenium as fallback...")
        results = search_tga_with_selenium("paracetamol", max_results=5)
    print(json.dumps(results, indent=2))
