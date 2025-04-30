"""
Browser Automation with Human-like Behavior

This module provides a browser automation tool that mimics human behavior
to avoid detection by anti-bot systems. It includes:

1. Random delays between actions
2. Natural mouse movements
3. Realistic typing patterns
4. Random scrolling behavior
5. Integration with CAPTCHA solving
"""

import time
import random
import logging
import os
import json
from typing import Optional, Dict, Any, List, Tuple, Union
from urllib.parse import urlparse, urljoin

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("browser_automation")

# Try to import Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import (
        TimeoutException, NoSuchElementException,
        ElementNotInteractableException, StaleElementReferenceException
    )

    # Try to import webdriver_manager
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        WEBDRIVER_MANAGER_AVAILABLE = True
    except ImportError:
        logger.warning("WebDriver Manager is not installed. Install with: pip install webdriver-manager")
        WEBDRIVER_MANAGER_AVAILABLE = False

    # Try to import undetected_chromedriver
    try:
        import undetected_chromedriver as uc
        UNDETECTED_CHROMEDRIVER_AVAILABLE = True
    except ImportError:
        logger.warning("Undetected ChromeDriver is not installed. Install with: pip install undetected-chromedriver")
        UNDETECTED_CHROMEDRIVER_AVAILABLE = False

    SELENIUM_AVAILABLE = True
except ImportError:
    logger.warning("Selenium is not installed. Install with: pip install selenium webdriver-manager")
    SELENIUM_AVAILABLE = False
    WEBDRIVER_MANAGER_AVAILABLE = False
    UNDETECTED_CHROMEDRIVER_AVAILABLE = False

# Try to import CAPTCHA solver
try:
    from captcha_solver import CaptchaSolver
    CAPTCHA_SOLVER_AVAILABLE = True
except ImportError:
    logger.warning("CAPTCHA solver is not available. Make sure captcha_solver.py is in the same directory.")
    CAPTCHA_SOLVER_AVAILABLE = False

class HumanLikeBrowser:
    """
    Browser automation with human-like behavior
    """

    def __init__(self, headless: bool = False, proxy: str = None, user_agent: str = None,
                captcha_solver: Any = None, download_dir: str = None):
        """
        Initialize the browser

        Args:
            headless (bool): Whether to run in headless mode
            proxy (str): Proxy server to use (format: "host:port")
            user_agent (str): User agent string to use
            captcha_solver (Any): CAPTCHA solver instance
            download_dir (str): Directory to save downloaded files
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is required for browser automation")

        self.headless = headless
        self.proxy = proxy
        self.user_agent = user_agent or self._get_random_user_agent()
        self.captcha_solver = captcha_solver
        self.download_dir = download_dir or os.path.join(os.getcwd(), "downloads")

        # Create download directory if it doesn't exist
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

        # Initialize browser
        self.driver = None
        self.wait = None

    def start(self) -> None:
        """
        Start the browser
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is required for browser automation")

        # Set up Chrome options
        options = Options()

        if self.headless:
            options.add_argument("--headless")

        # Add user agent
        options.add_argument(f"user-agent={self.user_agent}")

        # Add proxy if provided
        if self.proxy:
            options.add_argument(f"--proxy-server={self.proxy}")

        # Add other options to avoid detection
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # Set download directory
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False
        }
        options.add_experimental_option("prefs", prefs)

        # Initialize the driver
        try:
            # Try using undetected_chromedriver first (best for avoiding detection)
            if UNDETECTED_CHROMEDRIVER_AVAILABLE:
                logger.info("Using undetected_chromedriver")
                import undetected_chromedriver as uc
                self.driver = uc.Chrome(options=options)

            # Fall back to webdriver_manager if available
            elif WEBDRIVER_MANAGER_AVAILABLE:
                logger.info("Using webdriver_manager")
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)

            # Fall back to regular Chrome WebDriver
            else:
                logger.info("Using regular Chrome WebDriver")
                self.driver = webdriver.Chrome(options=options)

        except Exception as e:
            logger.error(f"Error initializing Chrome driver: {e}")

            # Try Firefox as a fallback
            try:
                logger.info("Trying Firefox as fallback")
                from selenium.webdriver.firefox.service import Service as FirefoxService
                from selenium.webdriver.firefox.options import Options as FirefoxOptions

                firefox_options = FirefoxOptions()
                if self.headless:
                    firefox_options.add_argument("--headless")

                firefox_options.add_argument(f"user-agent={self.user_agent}")

                if WEBDRIVER_MANAGER_AVAILABLE:
                    from webdriver_manager.firefox import GeckoDriverManager
                    firefox_service = FirefoxService(GeckoDriverManager().install())
                    self.driver = webdriver.Firefox(service=firefox_service, options=firefox_options)
                else:
                    self.driver = webdriver.Firefox(options=firefox_options)

            except Exception as firefox_error:
                logger.error(f"Error initializing Firefox driver: {firefox_error}")
                raise Exception("Failed to initialize any WebDriver")

        # Set window size to a common resolution
        self.driver.set_window_size(1920, 1080)

        # Initialize wait
        self.wait = WebDriverWait(self.driver, 10)

        # Execute stealth JavaScript to avoid detection
        self._execute_stealth_js()

        logger.info("Browser started successfully")

    def stop(self) -> None:
        """
        Stop the browser
        """
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None
            logger.info("Browser stopped")

    def navigate_to(self, url: str, wait_for_load: bool = True) -> bool:
        """
        Navigate to a URL with human-like behavior

        Args:
            url (str): URL to navigate to
            wait_for_load (bool): Whether to wait for the page to load

        Returns:
            bool: True if navigation was successful, False otherwise
        """
        if not self.driver:
            logger.error("Browser not started")
            return False

        try:
            logger.info(f"Navigating to {url}")
            self.driver.get(url)

            # Add a random delay to simulate page loading time
            self._random_sleep(1, 3)

            if wait_for_load:
                # Wait for the page to load
                self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

                # Add another random delay
                self._random_sleep(0.5, 2)

            # Scroll a bit to simulate human behavior
            self._random_scroll()

            return True

        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}")
            return False

    def fill_form(self, form_data: Dict[str, str]) -> bool:
        """
        Fill a form with human-like typing behavior

        Args:
            form_data (Dict[str, str]): Dictionary mapping field selectors to values

        Returns:
            bool: True if form was filled successfully, False otherwise
        """
        if not self.driver:
            logger.error("Browser not started")
            return False

        try:
            for selector, value in form_data.items():
                # Find the element
                element = self._find_element(selector)
                if not element:
                    logger.error(f"Element not found: {selector}")
                    continue

                # Clear the field if it's not empty
                element.clear()

                # Type with human-like delays
                self._human_type(element, value)

                # Add a random delay between fields
                self._random_sleep(0.5, 1.5)

            return True

        except Exception as e:
            logger.error(f"Error filling form: {e}")
            return False

    def click_element(self, selector: str, wait_after: bool = True) -> bool:
        """
        Click an element with human-like behavior

        Args:
            selector (str): CSS selector or XPath of the element to click
            wait_after (bool): Whether to wait after clicking

        Returns:
            bool: True if click was successful, False otherwise
        """
        if not self.driver:
            logger.error("Browser not started")
            return False

        try:
            # Find the element
            element = self._find_element(selector)
            if not element:
                logger.error(f"Element not found: {selector}")
                return False

            # Scroll to the element
            self._scroll_to_element(element)

            # Move to the element with human-like motion
            self._human_move_to_element(element)

            # Click the element
            element.click()

            # Add a random delay after clicking
            if wait_after:
                self._random_sleep(0.5, 2)

            return True

        except Exception as e:
            logger.error(f"Error clicking element {selector}: {e}")
            return False

    def solve_captcha(self, image_selector: str = None, recaptcha: bool = False) -> bool:
        """
        Solve a CAPTCHA using the provided solver

        Args:
            image_selector (str): CSS selector or XPath of the CAPTCHA image
            recaptcha (bool): Whether this is a reCAPTCHA

        Returns:
            bool: True if CAPTCHA was solved successfully, False otherwise
        """
        if not self.driver:
            logger.error("Browser not started")
            return False

        if not self.captcha_solver:
            logger.error("No CAPTCHA solver provided")
            return False

        if not CAPTCHA_SOLVER_AVAILABLE:
            logger.error("CAPTCHA solver module not available")
            return False

        try:
            if recaptcha:
                # Handle reCAPTCHA
                return self._solve_recaptcha()
            else:
                # Handle image CAPTCHA
                return self._solve_image_captcha(image_selector)

        except Exception as e:
            logger.error(f"Error solving CAPTCHA: {e}")
            return False

    def get_page_source(self) -> str:
        """
        Get the page source

        Returns:
            str: The page source HTML
        """
        if not self.driver:
            logger.error("Browser not started")
            return ""

        return self.driver.page_source

    def get_cookies(self) -> List[Dict[str, Any]]:
        """
        Get all cookies

        Returns:
            List[Dict[str, Any]]: List of cookies
        """
        if not self.driver:
            logger.error("Browser not started")
            return []

        return self.driver.get_cookies()

    def set_cookies(self, cookies: List[Dict[str, Any]]) -> bool:
        """
        Set cookies

        Args:
            cookies (List[Dict[str, Any]]): List of cookies to set

        Returns:
            bool: True if cookies were set successfully, False otherwise
        """
        if not self.driver:
            logger.error("Browser not started")
            return False

        try:
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            return True
        except Exception as e:
            logger.error(f"Error setting cookies: {e}")
            return False

    def take_screenshot(self, filename: str = None) -> str:
        """
        Take a screenshot

        Args:
            filename (str): Filename to save the screenshot to

        Returns:
            str: Path to the screenshot file
        """
        if not self.driver:
            logger.error("Browser not started")
            return ""

        if not filename:
            filename = f"screenshot_{int(time.time())}.png"

        filepath = os.path.join(self.download_dir, filename)
        self.driver.save_screenshot(filepath)

        return filepath

    def _find_element(self, selector: str) -> Optional[Any]:
        """
        Find an element by CSS selector or XPath

        Args:
            selector (str): CSS selector or XPath

        Returns:
            Optional[Any]: The element if found, None otherwise
        """
        try:
            # Try CSS selector first
            return self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        except:
            try:
                # Try XPath if CSS selector fails
                return self.wait.until(EC.presence_of_element_located((By.XPATH, selector)))
            except:
                return None

    def _human_type(self, element: Any, text: str) -> None:
        """
        Type text with human-like delays

        Args:
            element (Any): Element to type into
            text (str): Text to type
        """
        # Focus on the element
        element.click()

        # Type each character with a random delay
        for char in text:
            # Random delay between keystrokes (50-200ms)
            time.sleep(random.uniform(0.05, 0.2))

            # Type the character
            element.send_keys(char)

        # Add a final delay
        time.sleep(random.uniform(0.2, 0.5))

    def _human_move_to_element(self, element: Any) -> None:
        """
        Move to an element with human-like motion

        Args:
            element (Any): Element to move to
        """
        # Get current mouse position
        action = ActionChains(self.driver)

        # Add some randomness to the movement
        action.move_to_element_with_offset(
            element,
            random.randint(-10, 10),  # Random X offset
            random.randint(-10, 10)   # Random Y offset
        )

        # Execute the action
        action.perform()

        # Add a small delay
        time.sleep(random.uniform(0.1, 0.3))

    def _random_scroll(self, min_scrolls: int = 1, max_scrolls: int = 5) -> None:
        """
        Perform random scrolling

        Args:
            min_scrolls (int): Minimum number of scroll actions
            max_scrolls (int): Maximum number of scroll actions
        """
        num_scrolls = random.randint(min_scrolls, max_scrolls)

        for _ in range(num_scrolls):
            # Random scroll distance
            scroll_distance = random.randint(100, 500)

            # Scroll down or up (80% chance of scrolling down)
            if random.random() < 0.8:
                self.driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
            else:
                self.driver.execute_script(f"window.scrollBy(0, -{scroll_distance});")

            # Random delay between scrolls
            time.sleep(random.uniform(0.3, 1.0))

    def _scroll_to_element(self, element: Any) -> None:
        """
        Scroll to an element with human-like behavior

        Args:
            element (Any): Element to scroll to
        """
        # Get element position
        location = element.location

        # Scroll to element with a slight offset
        offset = random.randint(-50, 50)
        self.driver.execute_script(f"window.scrollTo(0, {location['y'] + offset});")

        # Add a small delay
        time.sleep(random.uniform(0.2, 0.5))

    def _random_sleep(self, min_seconds: float, max_seconds: float) -> None:
        """
        Sleep for a random amount of time

        Args:
            min_seconds (float): Minimum sleep time in seconds
            max_seconds (float): Maximum sleep time in seconds
        """
        time.sleep(random.uniform(min_seconds, max_seconds))

    def _get_random_user_agent(self) -> str:
        """
        Get a random user agent string

        Returns:
            str: Random user agent string
        """
        user_agents = [
            # Chrome on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            # Firefox on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            # Chrome on macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            # Safari on macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            # Edge on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59"
        ]

        return random.choice(user_agents)

    def _execute_stealth_js(self) -> None:
        """
        Execute JavaScript to avoid detection
        """
        # Overwrite the navigator properties
        js_script = """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });

        // Overwrite the plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });

        // Overwrite the languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        """

        try:
            self.driver.execute_script(js_script)
        except Exception as e:
            logger.error(f"Error executing stealth JS: {e}")

    def _solve_image_captcha(self, image_selector: str) -> bool:
        """
        Solve an image CAPTCHA

        Args:
            image_selector (str): CSS selector or XPath of the CAPTCHA image

        Returns:
            bool: True if CAPTCHA was solved successfully, False otherwise
        """
        # Find the CAPTCHA image
        image_element = self._find_element(image_selector)
        if not image_element:
            logger.error(f"CAPTCHA image not found: {image_selector}")
            return False

        # Get the image URL
        image_url = image_element.get_attribute("src")

        # Find the input field (usually near the image)
        input_selector = "input[name*='captcha'], input[id*='captcha'], input[class*='captcha']"
        input_element = self._find_element(input_selector)

        if not input_element:
            logger.error("CAPTCHA input field not found")
            return False

        # Solve the CAPTCHA
        solution = self.captcha_solver.solve_image_captcha(image_url=image_url)

        if not solution:
            logger.error("Failed to solve CAPTCHA")
            return False

        # Enter the solution
        self._human_type(input_element, solution)

        # Find and click the submit button
        submit_selector = "button[type='submit'], input[type='submit']"
        submit_element = self._find_element(submit_selector)

        if not submit_element:
            logger.error("Submit button not found")
            return False

        # Click the submit button
        submit_element.click()

        # Wait for the page to load
        self._random_sleep(1, 3)

        # Check if CAPTCHA was solved successfully
        # This is a simple check - you might need to customize this based on the website
        if "captcha" in self.driver.page_source.lower():
            logger.error("CAPTCHA solution was incorrect")
            return False

        logger.info("CAPTCHA solved successfully")
        return True

    def _solve_recaptcha(self) -> bool:
        """
        Solve a reCAPTCHA

        Returns:
            bool: True if reCAPTCHA was solved successfully, False otherwise
        """
        try:
            # Find the reCAPTCHA iframe
            iframe = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='recaptcha']")))

            # Switch to the iframe
            self.driver.switch_to.frame(iframe)

            # Click the checkbox
            checkbox = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".recaptcha-checkbox")))
            checkbox.click()

            # Switch back to the main content
            self.driver.switch_to.default_content()

            # Check if we need to solve a challenge
            time.sleep(2)

            # Look for the challenge iframe
            challenge_iframe = self.driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha/api2/bframe']")

            if challenge_iframe:
                # We need to solve the challenge
                self.driver.switch_to.frame(challenge_iframe[0])

                # Get the site key
                site_key = self.driver.execute_script(
                    "return document.querySelector('.g-recaptcha').getAttribute('data-sitekey')"
                )

                # Get the page URL
                page_url = self.driver.current_url

                # Solve the reCAPTCHA
                solution = self.captcha_solver.solve_recaptcha(site_key, page_url)

                if not solution:
                    logger.error("Failed to solve reCAPTCHA")
                    return False

                # Enter the solution
                self.driver.execute_script(f"document.getElementById('g-recaptcha-response').innerHTML = '{solution}';")

                # Submit the solution
                self.driver.execute_script("document.getElementById('recaptcha-verify-button').click();")

                # Switch back to the main content
                self.driver.switch_to.default_content()

            # Wait for the page to load
            self._random_sleep(1, 3)

            logger.info("reCAPTCHA solved successfully")
            return True

        except Exception as e:
            logger.error(f"Error solving reCAPTCHA: {e}")
            return False

class BrowserAutomationManager:
    """
    Manager for browser automation
    """

    def __init__(self, captcha_api_key: str = "", captcha_service: str = "2captcha"):
        """
        Initialize the browser automation manager

        Args:
            captcha_api_key (str): API key for the CAPTCHA solving service
            captcha_service (str): CAPTCHA solving service to use
        """
        # Initialize CAPTCHA solver if available
        self.captcha_solver = None

        if CAPTCHA_SOLVER_AVAILABLE:
            try:
                from captcha_solver import CaptchaSolver
                self.captcha_solver = CaptchaSolver(api_key=captcha_api_key, service=captcha_service)
                logger.info(f"CAPTCHA solver initialized with service: {captcha_service}")
            except Exception as e:
                logger.error(f"Error initializing CAPTCHA solver: {e}")
        else:
            logger.warning("CAPTCHA solver module not available. Some websites may not be accessible.")

            # Try to import the module directly
            try:
                import sys
                import os

                # Add the current directory to the path
                current_dir = os.path.dirname(os.path.abspath(__file__))
                if current_dir not in sys.path:
                    sys.path.append(current_dir)

                # Try importing again
                from captcha_solver import CaptchaSolver
                self.captcha_solver = CaptchaSolver(api_key=captcha_api_key, service=captcha_service)
                logger.info(f"CAPTCHA solver initialized with service: {captcha_service}")
            except Exception as e:
                logger.error(f"Error importing CAPTCHA solver module: {e}")

        # Initialize browser instances
        self.browsers = {}

    def create_browser(self, browser_id: str, headless: bool = False, proxy: str = None,
                     user_agent: str = None, download_dir: str = None) -> bool:
        """
        Create a new browser instance

        Args:
            browser_id (str): ID for the browser instance
            headless (bool): Whether to run in headless mode
            proxy (str): Proxy server to use
            user_agent (str): User agent string to use
            download_dir (str): Directory to save downloaded files

        Returns:
            bool: True if browser was created successfully, False otherwise
        """
        if not SELENIUM_AVAILABLE:
            logger.error("Selenium is not installed. Cannot create browser.")
            return False

        if browser_id in self.browsers:
            logger.warning(f"Browser with ID {browser_id} already exists")
            return False

        try:
            # Check if we need to install Selenium
            if not SELENIUM_AVAILABLE:
                logger.warning("Attempting to install Selenium and WebDriver Manager...")
                try:
                    import subprocess
                    import sys
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium", "webdriver-manager"])
                    logger.info("Selenium and WebDriver Manager installed successfully!")

                    # Re-import Selenium
                    from selenium import webdriver
                    from selenium.webdriver.chrome.service import Service
                    from selenium.webdriver.chrome.options import Options
                    from selenium.webdriver.common.by import By
                    from selenium.webdriver.support.ui import WebDriverWait
                    from selenium.webdriver.support import expected_conditions as EC

                    # Update the global variables
                    globals()['webdriver'] = webdriver
                    globals()['Service'] = Service
                    globals()['Options'] = Options
                    globals()['By'] = By
                    globals()['WebDriverWait'] = WebDriverWait
                    globals()['EC'] = EC
                    globals()['SELENIUM_AVAILABLE'] = True
                except Exception as install_error:
                    logger.error(f"Error installing Selenium: {install_error}")
                    return False

            # Create the browser
            browser = HumanLikeBrowser(
                headless=headless,
                proxy=proxy,
                user_agent=user_agent,
                captcha_solver=self.captcha_solver,
                download_dir=download_dir
            )

            # Start the browser
            try:
                browser.start()
                self.browsers[browser_id] = browser
                logger.info(f"Browser with ID {browser_id} created successfully")
                return True
            except Exception as start_error:
                logger.error(f"Error starting browser: {start_error}")
                return False

        except Exception as e:
            logger.error(f"Error creating browser: {e}")
            return False

    def get_browser(self, browser_id: str) -> Optional[HumanLikeBrowser]:
        """
        Get a browser instance by ID

        Args:
            browser_id (str): ID of the browser instance

        Returns:
            Optional[HumanLikeBrowser]: The browser instance if found, None otherwise
        """
        return self.browsers.get(browser_id)

    def close_browser(self, browser_id: str) -> bool:
        """
        Close a browser instance

        Args:
            browser_id (str): ID of the browser instance

        Returns:
            bool: True if browser was closed successfully, False otherwise
        """
        browser = self.browsers.get(browser_id)

        if not browser:
            logger.warning(f"Browser with ID {browser_id} not found")
            return False

        try:
            browser.stop()
            del self.browsers[browser_id]
            return True

        except Exception as e:
            logger.error(f"Error closing browser: {e}")
            return False

    def close_all_browsers(self) -> None:
        """
        Close all browser instances
        """
        for browser_id in list(self.browsers.keys()):
            self.close_browser(browser_id)

# Example usage
if __name__ == "__main__":
    # Create a browser automation manager
    manager = BrowserAutomationManager()

    # Create a browser instance
    manager.create_browser("browser1", headless=False)

    # Get the browser instance
    browser = manager.get_browser("browser1")

    if browser:
        # Navigate to a website
        browser.navigate_to("https://example.com")

        # Fill a form
        browser.fill_form({
            "input[name='username']": "testuser",
            "input[name='password']": "testpassword"
        })

        # Click a button
        browser.click_element("button[type='submit']")

        # Take a screenshot
        browser.take_screenshot("example.png")

        # Get the page source
        html = browser.get_page_source()
        print(f"Page source length: {len(html)}")

    # Close all browsers
    manager.close_all_browsers()
