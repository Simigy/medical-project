# Configuration file for advanced scraping utilities

# Default proxies to use for rotation
# Format: "http://user:pass@host:port"
DEFAULT_PROXIES = [
    # Add your proxies here
    # Example: "http://user:pass@proxy1.example.com:8080",
]

# CAPTCHA solving service configuration
CAPTCHA_CONFIG = {
    "service": "2captcha",  # Options: "2captcha", "anticaptcha"
    "api_key": "",  # Your API key for the CAPTCHA solving service
}

# Rate limiting configuration
RATE_LIMITS = {
    # Default rate limits for different domains
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

# Database-specific scraping configurations
DATABASE_CONFIGS = {
    "swissmedic": {
        "use_proxies": True,
        "use_captcha_solver": False,
        "use_authentication": False,
        "respect_rate_limits": True,
        "requests_per_minute": 5,
        "max_retries": 5,
        "use_selenium": True,
        "wait_time": 5,  # seconds to wait for page load in Selenium
    },
    "ema-medicines": {
        "use_proxies": True,
        "use_captcha_solver": False,
        "use_authentication": False,
        "respect_rate_limits": True,
        "requests_per_minute": 10,
        "max_retries": 3,
        "use_selenium": False,
    },
    "mhra": {
        "use_proxies": False,
        "use_captcha_solver": False,
        "use_authentication": False,
        "respect_rate_limits": True,
        "requests_per_minute": 15,
        "max_retries": 3,
        "use_selenium": False,
    },
    "tga": {
        "use_proxies": True,
        "use_captcha_solver": False,
        "use_authentication": False,
        "respect_rate_limits": True,
        "requests_per_minute": 8,
        "max_retries": 4,
        "use_selenium": True,
        "wait_time": 3,
    },
    "medsafe": {
        "use_proxies": False,
        "use_captcha_solver": False,
        "use_authentication": False,
        "respect_rate_limits": True,
        "requests_per_minute": 20,
        "max_retries": 2,
        "use_selenium": False,
    },
    "lakemedelsverket": {
        "use_proxies": True,
        "use_captcha_solver": False,
        "use_authentication": False,
        "respect_rate_limits": True,
        "requests_per_minute": 10,
        "max_retries": 3,
        "use_selenium": True,
        "wait_time": 4,
    },
}

# Function to get database-specific configuration
def get_database_config(database_id):
    """Get the scraping configuration for a specific database"""
    return DATABASE_CONFIGS.get(database_id, {
        "use_proxies": False,
        "use_captcha_solver": False,
        "use_authentication": False,
        "respect_rate_limits": True,
        "requests_per_minute": 10,
        "max_retries": 3,
        "use_selenium": False,
        "wait_time": 5,
    })

# Function to get rate limit for a domain
def get_rate_limit(domain):
    """Get the rate limit for a specific domain"""
    # Extract the base domain
    if domain.startswith('www.'):
        domain = domain[4:]
    
    # Check for domain in rate limits
    for key in RATE_LIMITS:
        if key in domain:
            return RATE_LIMITS[key]
    
    # Return default rate limit if no match
    return RATE_LIMITS["default"]