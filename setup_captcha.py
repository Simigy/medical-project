"""
Set up CAPTCHA solver environment variables
"""

import os
import sys
import json
import argparse

def main():
    """
    Set up CAPTCHA solver environment variables
    """
    parser = argparse.ArgumentParser(description="Set up CAPTCHA solver environment variables")
    parser.add_argument("--api-key", help="API key for the CAPTCHA solving service")
    parser.add_argument("--service", default="2captcha", choices=["2captcha", "anticaptcha", "capsolver", "local"],
                        help="CAPTCHA solving service to use")
    args = parser.parse_args()
    
    # Get the API key
    api_key = args.api_key
    if not api_key:
        api_key = input("Enter your CAPTCHA API key: ")
    
    # Get the service
    service = args.service
    if not service:
        service = input("Enter the CAPTCHA service (2captcha, anticaptcha, capsolver, local): ")
    
    # Set the environment variables
    os.environ["CAPTCHA_API_KEY"] = api_key
    
    # Set the service-specific environment variable
    if service == "2captcha":
        os.environ["TWOCAPTCHA_API_KEY"] = api_key
    elif service == "anticaptcha":
        os.environ["ANTICAPTCHA_API_KEY"] = api_key
    elif service == "capsolver":
        os.environ["CAPSOLVER_API_KEY"] = api_key
    
    # Save the environment variables to a .env file
    with open(".env", "w") as f:
        f.write(f"CAPTCHA_API_KEY={api_key}\n")
        f.write(f"CAPTCHA_SERVICE={service}\n")
        
        if service == "2captcha":
            f.write(f"TWOCAPTCHA_API_KEY={api_key}\n")
        elif service == "anticaptcha":
            f.write(f"ANTICAPTCHA_API_KEY={api_key}\n")
        elif service == "capsolver":
            f.write(f"CAPSOLVER_API_KEY={api_key}\n")
    
    print(f"CAPTCHA solver environment variables set up successfully for {service}")
    print(f"API key: {api_key}")
    print("Environment variables saved to .env file")
    
    # Test the CAPTCHA solver
    try:
        from scraping.captcha_solver import CaptchaSolver
        solver = CaptchaSolver(api_key=api_key, service=service)
        print(f"CAPTCHA solver initialized with service: {service}")
        print("CAPTCHA solver is ready to use")
    except Exception as e:
        print(f"Error initializing CAPTCHA solver: {e}")
        print("Please make sure you have installed the required dependencies")
        print("Run: pip install 2captcha-python anticaptchaofficial")

if __name__ == "__main__":
    main()
