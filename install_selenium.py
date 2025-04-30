"""
Install Selenium and WebDriver Manager for browser automation
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    print(f"Installing {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    """Main function to install Selenium and WebDriver Manager"""
    print("Installing Selenium and WebDriver Manager...")
    
    # Install Selenium and WebDriver Manager
    try:
        install_package("selenium")
        install_package("webdriver-manager")
        print("Selenium and WebDriver Manager installed successfully!")
    except Exception as e:
        print(f"Error installing Selenium and WebDriver Manager: {e}")
        return False
    
    # Install undetected-chromedriver for better anti-bot protection
    try:
        install_package("undetected-chromedriver")
        print("Undetected ChromeDriver installed successfully!")
    except Exception as e:
        print(f"Error installing undetected-chromedriver: {e}")
    
    # Install CAPTCHA solving libraries
    try:
        install_package("2captcha-python")
        print("2captcha-python installed successfully!")
    except Exception as e:
        print(f"Error installing 2captcha-python: {e}")
    
    print("\nAll dependencies installed successfully!")
    print("You can now use browser automation with Selenium.")
    
    return True

if __name__ == "__main__":
    main()
