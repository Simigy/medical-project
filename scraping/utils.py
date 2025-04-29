import requests
import random
import time
from typing import List, Dict, Any, Optional, Union, Callable
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# ===== PROXY ROTATION UTILITIES =====

class ProxyManager:
    """Manages a pool of proxies for rotation during web scraping"""
    
    def __init__(self, proxies: List[str] = None):
        """Initialize with a list of proxies in format 'http://user:pass@host:port'"""
        self.proxies = proxies or []
        self.current_index = 0
        self.failed_proxies = set()
    
    def add_proxy(self, proxy: str) -> None:
        """Add a new proxy to the pool"""
        if proxy not in self.proxies:
            self.proxies.append(proxy)
    
    def remove_proxy(self, proxy: str) -> None:
        """Remove a proxy from the pool"""
        if proxy in self.proxies:
            self.proxies.remove(proxy)
    
    def get_random_proxy(self) -> Optional[str]:
        """Get a random proxy from the pool"""
        available_proxies = [p for p in self.proxies if p not in self.failed_proxies]
        if not available_proxies:
            return None
        return random.choice(available_proxies)
    
    def get_next_proxy(self) -> Optional[str]:
        """Get the next proxy in rotation"""
        available_proxies = [p for p in self.proxies if p not in self.failed_proxies]
        if not available_proxies:
            return None
        
        if self.current_index >= len(available_proxies):
            self.current_index = 0
        
        proxy = available_proxies[self.current_index]
        self.current_index += 1
        return proxy
    
    def mark_proxy_failed(self, proxy: str) -> None:
        """Mark a proxy as failed"""
        self.failed_proxies.add(proxy)
    
    def reset_failed_proxies(self) -> None:
        """Reset the list of failed proxies"""
        self.failed_proxies.clear()

# ===== CAPTCHA HANDLING UTILITIES =====

class CaptchaSolver:
    """Handles CAPTCHA solving using third-party services"""
    
    def __init__(self, api_key: str = None, service: str = '2captcha'):
        """Initialize with API key for the CAPTCHA solving service"""
        self.api_key = api_key
        self.service = service.lower()
        
    def solve_recaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve a reCAPTCHA using the configured service"""
        if not self.api_key:
            print("No API key provided for CAPTCHA solving")
            return None
            
        if self.service == '2captcha':
            return self._solve_with_2captcha(site_key, page_url)
        elif self.service == 'anticaptcha':
            return self._solve_with_anticaptcha(site_key, page_url)
        else:
            print(f"Unsupported CAPTCHA solving service: {self.service}")
            return None
    
    def _solve_with_2captcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve reCAPTCHA using 2Captcha service"""
        try:
            # Submit the CAPTCHA
            url = "http://2captcha.com/in.php"
            params = {
                'key': self.api_key,
                'method': 'userrecaptcha',
                'googlekey': site_key,
                'pageurl': page_url,
                'json': 1
            }
            
            response = requests.post(url, params=params)
            data = response.json()
            
            if data.get('status') != 1:
                print(f"Failed to submit CAPTCHA: {data.get('error_text')}")
                return None
                
            request_id = data.get('request')
            
            # Wait for the result
            for _ in range(30):  # Try for 5 minutes (30 * 10 seconds)
                time.sleep(10)  # Wait 10 seconds between checks
                
                result_url = f"http://2captcha.com/res.php?key={self.api_key}&action=get&id={request_id}&json=1"
                result_response = requests.get(result_url)
                result_data = result_response.json()
                
                if result_data.get('status') == 1:
                    return result_data.get('request')
                    
                if result_data.get('request') != 'CAPCHA_NOT_READY':
                    print(f"CAPTCHA solving failed: {result_data.get('request')}")
                    return None
            
            print("CAPTCHA solving timed out")
            return None
            
        except Exception as e:
            print(f"Error solving CAPTCHA with 2Captcha: {e}")
            return None
    
    def _solve_with_anticaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve reCAPTCHA using AntiCaptcha service"""
        # Implementation for AntiCaptcha would go here
        print("AntiCaptcha implementation not yet available")
        return None

# ===== AUTHENTICATION UTILITIES =====

class AuthManager:
    """Manages authentication for websites requiring login"""
    
    def __init__(self, driver_path: str = None):
        """Initialize with path to webdriver"""
        self.driver_path = driver_path
        self.cookies = {}
        self.tokens = {}
    
    def login_with_selenium(self, url: str, username: str, password: str, 
                           username_selector: str, password_selector: str, 
                           submit_selector: str) -> Dict[str, str]:
        """Perform login using Selenium and return cookies"""
        options = Options()
        options.headless = True
        
        driver = webdriver.Chrome(executable_path=self.driver_path, options=options) if self.driver_path else webdriver.Chrome(options=options)
        
        try:
            driver.get(url)
            
            # Wait for the login form to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, username_selector))
            )
            
            # Fill in the login form
            driver.find_element(By.CSS_SELECTOR, username_selector).send_keys(username)
            driver.find_element(By.CSS_SELECTOR, password_selector).send_keys(password)
            driver.find_element(By.CSS_SELECTOR, submit_selector).click()
            
            # Wait for login to complete (adjust the wait condition as needed)
            time.sleep(5)
            
            # Get cookies
            selenium_cookies = driver.get_cookies()
            cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
            
            # Store cookies for this domain
            domain = url.split('//')[1].split('/')[0]
            self.cookies[domain] = cookies
            
            return cookies
            
        except Exception as e:
            print(f"Error during login: {e}")
            return {}
            
        finally:
            driver.quit()
    
    def get_cookies_for_domain(self, url: str) -> Dict[str, str]:
        """Get stored cookies for a domain"""
        domain = url.split('//')[1].split('/')[0]
        return self.cookies.get(domain, {})

# ===== RATE LIMITING UTILITIES =====

class RateLimiter:
    """Manages rate limiting for API requests"""
    
    def __init__(self):
        """Initialize the rate limiter"""
        self.request_timestamps = {}
    
    def wait_if_needed(self, domain: str, requests_per_minute: int) -> None:
        """Wait if necessary to respect rate limits"""
        if domain not in self.request_timestamps:
            self.request_timestamps[domain] = []
            return
            
        # Get timestamps from the last minute
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Filter timestamps to only include those from the last minute
        self.request_timestamps[domain] = [
            ts for ts in self.request_timestamps[domain] if ts > minute_ago
        ]
        
        # Check if we need to wait
        if len(self.request_timestamps[domain]) >= requests_per_minute:
            # Calculate wait time - wait until the oldest request is more than a minute old
            wait_time = 60 - (current_time - self.request_timestamps[domain][0])
            if wait_time > 0:
                print(f"Rate limit reached for {domain}. Waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
                
                # After waiting, clear old timestamps and start fresh
                self.request_timestamps[domain] = []
    
    def record_request(self, domain: str) -> None:
        """Record a request to a domain"""
        if domain not in self.request_timestamps:
            self.request_timestamps[domain] = []
            
        self.request_timestamps[domain].append(time.time())

# ===== RETRY HANDLING UTILITIES =====

class RetryHandler:
    """Handles retry logic for failed requests with exponential backoff and jitter"""
    
    def __init__(self, max_retries: int = 3, initial_delay: float = 1.0, 
                 max_delay: float = 30.0, backoff_factor: float = 2.0, 
                 jitter_factor: float = 0.25):
        """Initialize with retry parameters
        
        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            backoff_factor: Multiplier for exponential backoff
            jitter_factor: Amount of randomness (0-1) to add to delay
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter_factor = jitter_factor
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter"""
        # Calculate exponential backoff
        delay = self.initial_delay * (self.backoff_factor ** attempt)
        
        # Cap at maximum delay
        delay = min(delay, self.max_delay)
        
        # Add jitter to prevent thundering herd problem
        jitter_amount = delay * self.jitter_factor
        delay += (random.random() * jitter_amount * 2) - jitter_amount
        
        return delay
    
    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute a function with retry logic using exponential backoff"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                # If this was the last attempt, re-raise the exception
                if attempt == self.max_retries:
                    break
                
                # Calculate delay with exponential backoff and jitter
                wait_time = self._calculate_delay(attempt)
                
                print(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
        
        # If we get here, all retries failed
        raise Exception(f"All {self.max_retries + 1} attempts failed. Last error: {last_exception}")

# ===== ADVANCED SCRAPER CLASS =====

class AdvancedScraper:
    """Advanced scraper with proxy rotation, CAPTCHA handling, authentication, rate limiting, and retries"""
    
    def __init__(self, 
                 proxy_manager: ProxyManager = None,
                 captcha_solver: CaptchaSolver = None,
                 auth_manager: AuthManager = None,
                 rate_limiter: RateLimiter = None,
                 retry_handler: RetryHandler = None,
                 driver_path: str = None):
        """Initialize with optional utility managers"""
        self.proxy_manager = proxy_manager or ProxyManager()
        self.captcha_solver = captcha_solver
        self.auth_manager = auth_manager or AuthManager(driver_path)
        self.rate_limiter = rate_limiter or RateLimiter()
        self.retry_handler = retry_handler or RetryHandler()
        self.driver_path = driver_path
        
        # Default headers to mimic a browser
        self.default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        return url.split('//')[1].split('/')[0]
    
    def scrape_with_requests(self, url: str, params: Dict[str, Any] = None, 
                            headers: Dict[str, str] = None, 
                            use_proxy: bool = True,
                            respect_rate_limit: bool = True,
                            requests_per_minute: int = 10,
                            use_auth: bool = False) -> Optional[str]:
        """Scrape a website using requests with advanced features"""
        domain = self._get_domain(url)
        
        # Apply rate limiting if enabled
        if respect_rate_limit:
            self.rate_limiter.wait_if_needed(domain, requests_per_minute)
        
        # Merge default headers with provided headers
        merged_headers = {**self.default_headers, **(headers or {})}
        
        # Add authentication cookies if needed
        if use_auth:
            cookies = self.auth_manager.get_cookies_for_domain(url)
        else:
            cookies = None
        
        # Set up proxy if enabled
        if use_proxy and self.proxy_manager.proxies:
            proxy = self.proxy_manager.get_next_proxy()
            proxies = {'http': proxy, 'https': proxy} if proxy else None
        else:
            proxies = None
        
        # Define the request function to be retried
        def make_request():
            response = requests.get(
                url, 
                params=params, 
                headers=merged_headers,
                proxies=proxies,
                cookies=cookies,
                timeout=15
            )
            response.raise_for_status()
            
            # Check for CAPTCHA
            if 'captcha' in response.text.lower():
                raise Exception("CAPTCHA detected")
                
            return response.text
        
        try:
            # Execute with retry logic
            html = self.retry_handler.execute_with_retry(make_request)
            
            # Record successful request for rate limiting
            if respect_rate_limit:
                self.rate_limiter.record_request(domain)
                
            return html
            
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")
            
            # If using a proxy and it failed, mark it as failed
            if use_proxy and proxies:
                self.proxy_manager.mark_proxy_failed(proxy)
                
            return None
    
    def scrape_with_selenium(self, url: str, wait_time: int = 5, 
                            use_proxy: bool = True,
                            handle_captcha: bool = False,
                            site_key: str = None) -> Optional[str]:
        """Scrape a website using Selenium for JavaScript-heavy sites"""
        options = Options()
        options.headless = True
        
        # Add proxy if enabled
        if use_proxy and self.proxy_manager.proxies:
            proxy = self.proxy_manager.get_next_proxy()
            if proxy:
                options.add_argument(f'--proxy-server={proxy}')
        
        # Initialize the driver
        driver = webdriver.Chrome(executable_path=self.driver_path, options=options) if self.driver_path else webdriver.Chrome(options=options)
        
        try:
            # Navigate to the URL
            driver.get(url)
            
            # Wait for the page to load
            time.sleep(wait_time)
            
            # Handle CAPTCHA if needed
            if handle_captcha and 'captcha' in driver.page_source.lower() and self.captcha_solver and site_key:
                captcha_response = self.captcha_solver.solve_recaptcha(site_key, url)
                if captcha_response:
                    # Execute JavaScript to set the CAPTCHA response
                    driver.execute_script(
                        f"document.getElementById('g-recaptcha-response').innerHTML='{captcha_response}';"
                    )
                    # Submit the form (adjust selector as needed)
                    submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
                    submit_button.click()
                    time.sleep(wait_time)  # Wait for page to load after CAPTCHA
            
            # Get the page source
            html = driver.page_source
            return html
            
        except Exception as e:
            print(f"Failed to scrape {url} with Selenium: {e}")
            
            # If using a proxy and it failed, mark it as failed
            if use_proxy and self.proxy_manager.proxies:
                self.proxy_manager.mark_proxy_failed(proxy)
                
            return None
            
        finally:
            driver.quit()

# ===== USAGE EXAMPLES =====

def example_usage():
    """Example of how to use the advanced scraping utilities"""
    # Initialize proxy manager with a list of proxies
    proxies = [
        "http://user:pass@proxy1.example.com:8080",
        "http://user:pass@proxy2.example.com:8080",
    ]
    proxy_manager = ProxyManager(proxies)
    
    # Initialize CAPTCHA solver
    captcha_solver = CaptchaSolver(api_key="your_2captcha_api_key")
    
    # Initialize auth manager
    auth_manager = AuthManager(driver_path="path/to/chromedriver")
    
    # Initialize rate limiter and retry handler
    rate_limiter = RateLimiter()
    retry_handler = RetryHandler(max_retries=5)
    
    # Create the advanced scraper
    scraper = AdvancedScraper(
        proxy_manager=proxy_manager,
        captcha_solver=captcha_solver,
        auth_manager=auth_manager,
        rate_limiter=rate_limiter,
        retry_handler=retry_handler,
        driver_path="path/to/chromedriver"
    )
    
    # Example: Scrape a website with requests
    html = scraper.scrape_with_requests(
        url="https://www.example.com",
        use_proxy=True,
        respect_rate_limit=True,
        requests_per_minute=10
    )
    
    if html:
        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        # Extract data as needed
        print(soup.title.text)
    
    # Example: Scrape a JavaScript-heavy website with Selenium
    html = scraper.scrape_with_selenium(
        url="https://www.example.com/js-heavy-page",
        wait_time=5,
        use_proxy=True,
        handle_captcha=True,
        site_key="recaptcha-site-key"
    )
    
    if html:
        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        # Extract data as needed
        print(soup.title.text)

# Run the example if this file is executed directly
if __name__ == "__main__":
    # This is just an example and won't run by default
    # example_usage()
    pass