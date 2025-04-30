"""
Configuration for Medical Database Access

This module provides configuration settings for accessing various medical databases,
including API keys, rate limits, and access methods.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("config")

# Default proxies to use for rotation
# Format: "http://user:pass@host:port"
DEFAULT_PROXIES = [
    # Add your proxies here
    # Example: "http://user:pass@proxy1.example.com:8080",
]

# CAPTCHA solving service configuration
CAPTCHA_CONFIG = {
    "service": "2captcha",  # Options: "2captcha", "anticaptcha", "capsolver", "local"
    "api_key": os.environ.get("CAPTCHA_API_KEY", ""),  # Get from environment variable
    "timeout": 120,
    "retry_count": 2
}

# API Keys for various services
API_KEYS = {
    "pubmed": os.environ.get("PUBMED_API_KEY", ""),  # PubMed E-utilities API key (optional)
    "fda": os.environ.get("FDA_API_KEY", ""),     # OpenFDA API key (optional)
    "captcha": {
        "2captcha": os.environ.get("CAPTCHA_API_KEY", ""),  # 2Captcha API key
        "anticaptcha": os.environ.get("ANTICAPTCHA_API_KEY", ""),  # Anti-Captcha API key
        "capsolver": os.environ.get("CAPSOLVER_API_KEY", "")  # CapSolver API key
    },
    # Commercial data providers
    "commercial": {
        "drugbank": os.environ.get("DRUGBANK_API_KEY", ""),  # DrugBank API key
        "rxnav": os.environ.get("RXNAV_API_KEY", ""),     # RxNav API key
        "chembl": os.environ.get("CHEMBL_API_KEY", "")     # ChEMBL API key
    }
}

# Rate limiting configuration
RATE_LIMITS = {
    # Default rate limits for different domains
    "pubmed": 10,
    "fda": 40,
    "ema": 20,
    "mhra": 20,
    "tga": 10,
    "drugbank": 30,
    "rxnav": 20,
    "chembl": 15,
    "swissmedic.ch": 5,  # requests per minute
    "ema.europa.eu": 10,
    "mhra.gov.uk": 15,
    "tga.gov.au": 8,
    "medsafe.govt.nz": 20,
    "lakemedelsverket.se": 10,
    "default": 10,  # Default for any domain not specified
}

# Authentication credentials for different websites
# Format: {"domain": {"username": "user", "password": "pass"}}
AUTH_CREDENTIALS = {
    # Add your credentials here
    # Example: "secure-database.com": {"username": "user", "password": "pass"},
}

# Retry configuration
RETRY_CONFIG = {
    "max_retries": 3,
    "base_delay": 2.0,  # seconds
    "max_delay": 30.0,  # seconds
}

# User agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.55",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]

# Access methods for each database
ACCESS_METHODS = {
    "pubmed": ["api", "browser", "selenium"],
    "fda-drugs": ["api", "browser"],
    "ema-medicines": ["api", "browser", "selenium"],
    "mhra": ["api", "browser", "selenium"],
    "tga-cmi": ["browser", "selenium"],
    "tga": ["browser", "selenium"],
    "drugbank": ["api"],
    "rxnav": ["api"],
    "chembl": ["api"],
    "swissmedic": ["browser", "selenium"],
    "medsafe": ["browser"],
    "lakemedelsverket": ["browser", "selenium"],
}

# Database-specific scraping configurations
DATABASE_CONFIGS = {
    "pubmed": {
        "name": "PubMed",
        "url": "https://pubmed.ncbi.nlm.nih.gov/",
        "api_url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/",
        "use_proxies": False,
        "use_captcha_solver": True,
        "use_authentication": False,
        "respect_rate_limits": True,
        "requests_per_minute": 10,
        "max_retries": 3,
        "use_selenium": True,
        "wait_time": 5,
        "timeout": 30
    },
    "fda-drugs": {
        "name": "FDA Drugs",
        "url": "https://www.accessdata.fda.gov/scripts/cder/daf/",
        "api_url": "https://api.fda.gov/drug/",
        "use_proxies": False,
        "use_captcha_solver": False,
        "use_authentication": False,
        "respect_rate_limits": True,
        "requests_per_minute": 40,
        "max_retries": 3,
        "use_selenium": False,
        "timeout": 30
    },
    "ema-medicines": {
        "name": "EMA Medicines",
        "url": "https://www.ema.europa.eu/en/medicines/",
        "api_url": "https://www.ema.europa.eu/en/medicines/api/medicines",
        "use_proxies": True,
        "use_captcha_solver": True,
        "use_authentication": False,
        "respect_rate_limits": True,
        "requests_per_minute": 20,
        "max_retries": 3,
        "use_selenium": True,
        "wait_time": 5,
        "timeout": 30
    },
    "mhra": {
        "name": "MHRA",
        "url": "https://products.mhra.gov.uk/",
        "api_url": "https://products.mhra.gov.uk/api/search",
        "use_proxies": False,
        "use_captcha_solver": True,
        "use_authentication": False,
        "respect_rate_limits": True,
        "requests_per_minute": 15,
        "max_retries": 3,
        "use_selenium": True,
        "wait_time": 5,
        "timeout": 30
    },
    "tga-cmi": {
        "name": "TGA - Consumer Medicines Information",
        "url": "https://www.tga.gov.au/products/consumer-medicines-information/search",
        "api_url": "",  # No official API
        "use_proxies": True,
        "use_captcha_solver": True,
        "use_authentication": False,
        "respect_rate_limits": True,
        "requests_per_minute": 8,
        "max_retries": 4,
        "use_selenium": True,
        "wait_time": 3,
        "timeout": 30
    },
    "tga": {
        "name": "TGA",
        "url": "https://www.tga.gov.au/",
        "api_url": "",  # No official API
        "use_proxies": True,
        "use_captcha_solver": True,
        "use_authentication": False,
        "respect_rate_limits": True,
        "requests_per_minute": 8,
        "max_retries": 4,
        "use_selenium": True,
        "wait_time": 3,
        "timeout": 30
    },
    "drugbank": {
        "name": "DrugBank",
        "url": "https://go.drugbank.com/",
        "api_url": "https://api.drugbank.com/v1/",
        "use_proxies": False,
        "use_captcha_solver": False,
        "use_authentication": True,
        "respect_rate_limits": True,
        "requests_per_minute": 30,
        "max_retries": 3,
        "use_selenium": False,
        "timeout": 30
    },
    "rxnav": {
        "name": "RxNav",
        "url": "https://mor.nlm.nih.gov/RxNav/",
        "api_url": "https://rxnav.nlm.nih.gov/REST/",
        "use_proxies": False,
        "use_captcha_solver": False,
        "use_authentication": False,
        "respect_rate_limits": True,
        "requests_per_minute": 20,
        "max_retries": 3,
        "use_selenium": False,
        "timeout": 30
    },
    "chembl": {
        "name": "ChEMBL",
        "url": "https://www.ebi.ac.uk/chembl/",
        "api_url": "https://www.ebi.ac.uk/chembl/api/",
        "use_proxies": False,
        "use_captcha_solver": False,
        "use_authentication": False,
        "respect_rate_limits": True,
        "requests_per_minute": 15,
        "max_retries": 3,
        "use_selenium": False,
        "timeout": 30
    },
    "swissmedic": {
        "name": "Swissmedic",
        "url": "https://www.swissmedic.ch/",
        "api_url": "",  # No official API
        "use_proxies": True,
        "use_captcha_solver": False,
        "use_authentication": False,
        "respect_rate_limits": True,
        "requests_per_minute": 5,
        "max_retries": 5,
        "use_selenium": True,
        "wait_time": 5,
        "timeout": 30
    },
    "medsafe": {
        "name": "Medsafe",
        "url": "https://www.medsafe.govt.nz/",
        "api_url": "",  # No official API
        "use_proxies": False,
        "use_captcha_solver": False,
        "use_authentication": False,
        "respect_rate_limits": True,
        "requests_per_minute": 20,
        "max_retries": 2,
        "use_selenium": False,
        "timeout": 30
    },
    "lakemedelsverket": {
        "name": "Läkemedelsverket",
        "url": "https://www.lakemedelsverket.se/",
        "api_url": "",  # No official API
        "use_proxies": True,
        "use_captcha_solver": False,
        "use_authentication": False,
        "respect_rate_limits": True,
        "requests_per_minute": 10,
        "max_retries": 3,
        "use_selenium": True,
        "wait_time": 4,
        "timeout": 30
    },
}

# Browser automation settings
BROWSER_CONFIG = {
    "headless": False,  # Set to False to see the browser and handle CAPTCHAs better
    "user_agent_rotation": True,
    "proxy_rotation": False,
    "proxy_list": DEFAULT_PROXIES,
    "download_dir": "downloads",
    "screenshot_dir": "screenshots",
    "window_size": {
        "width": 1920,
        "height": 1080
    },
    "slow_mo": 50,  # Slow down operations by 50ms for more human-like behavior
    "browser_type": "chrome",  # Options: chrome, firefox, edge
    "stealth_mode": True,  # Enable stealth mode to avoid detection
    "disable_webdriver": True,  # Disable webdriver flags to avoid detection
    "disable_automation": True,  # Disable automation flags to avoid detection
    "use_undetected_chromedriver": True  # Use undetected-chromedriver if available
}

# Function to get database-specific configuration
def get_database_config(database_id):
    """
    Get the scraping configuration for a specific database

    Args:
        database_id (str): Database ID

    Returns:
        dict: Database configuration
    """
    return DATABASE_CONFIGS.get(database_id, {
        "name": database_id.upper(),
        "url": f"https://www.{database_id.lower()}.com/",
        "api_url": "",
        "use_proxies": False,
        "use_captcha_solver": False,
        "use_authentication": False,
        "respect_rate_limits": True,
        "requests_per_minute": 10,
        "max_retries": 3,
        "use_selenium": False,
        "wait_time": 5,
        "timeout": 30
    })

# Function to get rate limit for a domain or database ID
def get_rate_limit(domain_or_id):
    """
    Get the rate limit for a specific domain or database ID

    Args:
        domain_or_id (str): Domain or database ID

    Returns:
        int: Rate limit in requests per minute
    """
    # Check if it's a database ID first
    if domain_or_id in RATE_LIMITS:
        return RATE_LIMITS[domain_or_id]

    # Extract the base domain if it's a domain
    if domain_or_id.startswith('www.'):
        domain_or_id = domain_or_id[4:]

    # Check for domain in rate limits
    for key in RATE_LIMITS:
        if key in domain_or_id:
            return RATE_LIMITS[key]

    # Return default rate limit if no match
    return RATE_LIMITS["default"]

# Function to get API key for a service
def get_api_key(service):
    """
    Get API key for a specific service

    Args:
        service (str): Service name

    Returns:
        str: API key
    """
    # Check if it's a captcha service
    if service in ["2captcha", "anticaptcha", "capsolver"]:
        return API_KEYS["captcha"].get(service, "")

    # Check if it's a commercial data provider
    if service in ["drugbank", "rxnav", "chembl"]:
        return API_KEYS["commercial"].get(service, "")

    # Otherwise, it's a regular API
    return API_KEYS.get(service, "")

# Function to get available access methods for a database
def get_access_methods(database_id):
    """
    Get available access methods for a specific database

    Args:
        database_id (str): Database ID

    Returns:
        list: List of access methods
    """
    return ACCESS_METHODS.get(database_id, ["browser"])

# Function to get browser automation configuration
def get_browser_config():
    """
    Get browser automation configuration

    Returns:
        dict: Browser configuration
    """
    return BROWSER_CONFIG

# Function to get CAPTCHA solving configuration
def get_captcha_config():
    """
    Get CAPTCHA solving configuration

    Returns:
        dict: CAPTCHA configuration
    """
    return CAPTCHA_CONFIG