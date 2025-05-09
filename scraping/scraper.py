import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import random

# List to store the scraped data
scraped_data = []

# Function to fetch with retry mechanism
def fetch_with_retry(url, headers=None, retries=3, initial_delay=1.0, max_delay=30.0, backoff_factor=2.0, jitter_factor=0.25):
    """Fetch a URL with retry mechanism using exponential backoff and jitter
    
    Args:
        url: URL to fetch
        headers: Request headers
        retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Multiplier for exponential backoff
        jitter_factor: Amount of randomness (0-1) to add to delay
        
    Returns:
        Response object if successful, None otherwise
    """
    headers = headers or {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    for attempt in range(retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()  # Check for HTTP errors
            return response
        except requests.exceptions.RequestException as e:
            # If this was the last attempt, return None
            if attempt >= retries:
                print(f"Error: All {retries + 1} attempts to fetch {url} failed. Last error: {e}")
                return None
            
            # Calculate delay with exponential backoff
            delay = initial_delay * (backoff_factor ** attempt)
            
            # Cap at maximum delay
            delay = min(delay, max_delay)
            
            # Add jitter to prevent thundering herd problem
            jitter_amount = delay * jitter_factor
            delay += (random.random() * jitter_amount * 2) - jitter_amount
            
            print(f"Error on attempt {attempt + 1}: {e}")
            print(f"Retrying in {delay:.2f} seconds...")
            time.sleep(delay)

# Function to scrape a static site using Requests + BeautifulSoup
def scrape_static_site(url, headers):
    try:
        # Fetch the page with retry mechanism
        response = fetch_with_retry(url, headers)
        if not response:
            return  # All retries failed

        # Parse the page content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Example: Extract warnings (adjust selectors based on the actual HTML structure)
        for item in soup.select('.list-group-item'):  # Adjust the CSS selector
            title = item.select_one('h3').get_text(strip=True) if item.select_one('h3') else "No title"
            date = item.select_one('.date').get_text(strip=True) if item.select_one('.date') else "No date"
            link = item.find('a', href=True)['href'] if item.find('a', href=True) else None

            # Ensure the link is complete
            if link and not link.startswith('http'):
                link = f"https://www.example.com{link}"

            scraped_data.append({
                'Title': title,
                'Date': date,
                'Link': link
            })
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")

# Function to scrape a dynamic site using Selenium
def scrape_dynamic_site(url):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(5)  # Allow time for content to load

        # Extract content using BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Example: Extract warnings (adjust the selectors based on page content)
        for item in soup.select('.list-group-item'):  # Adjust the CSS selector
            title = item.select_one('h3').get_text(strip=True) if item.select_one('h3') else "No title"
            date = item.select_one('.date').get_text(strip=True) if item.select_one('.date') else "No date"
            link = item.find('a', href=True)['href'] if item.find('a', href=True) else None

            # Ensure the link is complete
            if link and not link.startswith('http'):
                link = f"https://www.example.com{link}"

            scraped_data.append({
                'Title': title,
                'Date': date,
                'Link': link
            })

    except Exception as e:
        print(f"Error fetching {url} with Selenium: {e}")
    finally:
        driver.quit()

# Define the headers for Requests (to mimic a browser request)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Example URLs for static and dynamic sites
static_url = "https://www.example.com/static-page"
dynamic_url = "https://www.example.com/dynamic-page"

# Scrape static and dynamic sites
scrape_static_site(static_url, headers)
scrape_dynamic_site(dynamic_url)

# Convert scraped data to DataFrame
df = pd.DataFrame(scraped_data)

# Save the data to a CSV file
df.to_csv('scraped_data.csv', index=False)
print(f"Success! Saved {len(df)} records to CSV.")


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import pandas as pd

# Set up headless Chrome options
options = Options()
options.headless = True

# Set path to chromedriver
driver = webdriver.Chrome(executable_path=r"C:\Users\sim_i\OneDrive\Desktop\medsearch\scraping\chromedriver-win64\chromedriver.exe", options=options)

# Example URL for scraping
url = "https://www.swissmedic.ch/swissmedic/en/home/humanarzneimittel/marktueberwachung/health-professional-communication--hpc-.html"

# Get the page content using Selenium
try:
    driver.get(url)
    time.sleep(5)  # Allow time for page to load

    # Get the page source after dynamic content is loaded
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Example scraping logic (adjust CSS selectors as necessary)
    warnings = []
    for item in soup.select('.list-group-item'):  # Example CSS selector, update according to Swissmedic structure
        title = item.select_one('h3').get_text(strip=True) if item.select_one('h3') else "No title"
        date = item.select_one('.date').get_text(strip=True) if item.select_one('.date') else "No date"
        link = item.find('a', href=True)['href'] if item.find('a', href=True) else None

        if link and not link.startswith('http'):
            link = f"https://www.swissmedic.ch{link}"

        warnings.append({
            'Title': title,
            'Date': date,
            'Link': link
        })

    # Convert to DataFrame and save as CSV
    df = pd.DataFrame(warnings)
    df.to_csv('swissmedic_drug_warnings.csv', index=False)
    print(f"Success! Saved {len(df)} warnings to CSV.")

except Exception as e:
    print(f"Error: {e}")

finally:
    driver.quit()  # Close the driver when done
