"""
Install all necessary dependencies for the medical database search application
"""

import subprocess
import sys
import os
import platform

def install_package(package):
    """Install a package using pip"""
    print(f"Installing {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    """Main function to install all dependencies"""
    print("Installing dependencies for medical database search application...")
    
    # Basic dependencies
    basic_deps = [
        "requests",
        "beautifulsoup4",
        "lxml",
        "python-dateutil",
        "tqdm",
        "colorama",
        "pyyaml",
        "python-dotenv"
    ]
    
    # Web scraping and browser automation dependencies
    scraping_deps = [
        "selenium",
        "webdriver-manager",
        "undetected-chromedriver",
        "playwright",
        "pyppeteer",
        "fake-useragent"
    ]
    
    # CAPTCHA solving dependencies
    captcha_deps = [
        "2captcha-python",
        "anticaptchaofficial",
        "pytesseract",
        "opencv-python"
    ]
    
    # API integration dependencies
    api_deps = [
        "requests-oauthlib",
        "requests-cache",
        "requests-html",
        "requests-toolbelt"
    ]
    
    # Install all dependencies
    for package in basic_deps + scraping_deps + captcha_deps + api_deps:
        try:
            install_package(package)
        except Exception as e:
            print(f"Error installing {package}: {e}")
            print(f"Continuing with other packages...")
    
    # Install browser drivers
    print("\nInstalling browser drivers...")
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        from webdriver_manager.firefox import GeckoDriverManager
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        
        # Install Chrome driver
        print("Installing Chrome driver...")
        ChromeDriverManager().install()
        
        # Install Firefox driver
        print("Installing Firefox driver...")
        GeckoDriverManager().install()
        
        # Install Edge driver
        print("Installing Edge driver...")
        EdgeChromiumDriverManager().install()
    except Exception as e:
        print(f"Error installing browser drivers: {e}")
    
    # Install Playwright browsers
    print("\nInstalling Playwright browsers...")
    try:
        subprocess.check_call([sys.executable, "-m", "playwright", "install"])
    except Exception as e:
        print(f"Error installing Playwright browsers: {e}")
    
    print("\nAll dependencies installed successfully!")
    print("You may need to install additional system dependencies for some packages.")
    
    # Print system-specific instructions
    system = platform.system()
    if system == "Linux":
        print("\nOn Linux, you may need to install:")
        print("  - For Tesseract OCR: sudo apt-get install tesseract-ocr")
        print("  - For Chrome: sudo apt-get install chromium-browser")
        print("  - For Firefox: sudo apt-get install firefox")
    elif system == "Darwin":  # macOS
        print("\nOn macOS, you may need to install:")
        print("  - For Tesseract OCR: brew install tesseract")
        print("  - For Chrome: brew install --cask google-chrome")
        print("  - For Firefox: brew install --cask firefox")
    elif system == "Windows":
        print("\nOn Windows, you may need to install:")
        print("  - For Tesseract OCR: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        print("  - Make sure Chrome, Firefox, or Edge is installed")
    
    print("\nTo use CAPTCHA solving services, set the following environment variables:")
    print("  - CAPTCHA_API_KEY: Your 2Captcha API key")
    print("  - ANTICAPTCHA_API_KEY: Your Anti-Captcha API key")
    print("  - CAPSOLVER_API_KEY: Your CapSolver API key")

if __name__ == "__main__":
    main()
