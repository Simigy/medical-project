# MedSearch Advanced Scraping Utilities

This module provides advanced scraping capabilities for the MedSearch application, enabling access to restricted medical databases through techniques like proxy rotation, CAPTCHA handling, authentication, rate limiting, and retry mechanisms.

## Features

### Proxy Rotation
- Automatically rotates between multiple proxy servers to avoid IP-based blocking
- Tracks failed proxies and removes them from rotation
- Supports both random and sequential proxy selection

### CAPTCHA Handling
- Integrates with third-party CAPTCHA solving services (2Captcha, AntiCaptcha)
- Automatically detects and solves CAPTCHAs during scraping
- Configurable timeout and retry settings

### Authentication
- Supports automated login to password-protected databases
- Stores and manages cookies and session tokens
- Uses Selenium for JavaScript-heavy authentication flows

### Rate Limiting
- Implements intelligent rate limiting to avoid triggering anti-scraping measures
- Database-specific rate limit configurations
- Automatic throttling based on domain

### Retry Mechanisms
- Exponential backoff with jitter for failed requests
- Configurable maximum retries and delay settings
- Detailed error reporting

## Usage

### From Python

```python
from utils import AdvancedScraper, ProxyManager, RateLimiter, RetryHandler
from config import get_database_config

# Initialize components
proxy_manager = ProxyManager()
rate_limiter = RateLimiter()
retry_handler = RetryHandler(max_retries=3)

# Initialize the scraper
scraper = AdvancedScraper(
    proxy_manager=proxy_manager,
    rate_limiter=rate_limiter,
    retry_handler=retry_handler
)

# Get database-specific configuration
db_config = get_database_config('swissmedic')

# Scrape a website
html = scraper.scrape_with_requests(
    url="https://www.swissmedic.ch/search",
    use_proxy=db_config['use_proxies'],
    respect_rate_limit=db_config['respect_rate_limits'],
    requests_per_minute=db_config['requests_per_minute']
)

# Process the results
if html:
    # Parse the HTML and extract data
    # ...
```

### From Command Line

The `cli.py` script provides a convenient command-line interface:

```bash
python cli.py --url="https://www.swissmedic.ch/search" \
              --query="paracetamol" \
              --database="swissmedic" \
              --output="results.json" \
              --verbose
```

### From Next.js API

The scraping utilities are integrated with the MedSearch application through the `/api/scrape/advanced-route` endpoint and the `lib/scraping` module:

```typescript
import { scrapeWithAdvancedTechniques, getDatabaseScrapingConfig } from "@/lib/scraping";

// Get database-specific configuration
const scrapingConfig = getDatabaseScrapingConfig(databaseId);

// Perform advanced scraping
const results = await scrapeWithAdvancedTechniques(url, query, scrapingConfig);
```

## Configuration

The `config.py` file contains database-specific configurations for scraping:

```python
# Example configuration for Swissmedic
"swissmedic": {
    "use_proxies": True,
    "use_captcha_solver": False,
    "use_authentication": False,
    "respect_rate_limits": True,
    "requests_per_minute": 5,
    "max_retries": 5,
    "use_selenium": True,
    "wait_time": 5,  # seconds
}
```

## Adding New Databases

To add support for a new database:

1. Add the database URL pattern to `getDatabaseUrlForId` in `lib/api/api-service.ts`
2. Add database-specific configuration to `DATABASE_CONFIGS` in `scraping/config.py`
3. Add the database ID to `advancedScrapingDatabases` in `lib/scraping/index.ts`

## Security Considerations

- API keys for CAPTCHA solving services should be stored securely
- Proxy credentials should not be committed to the repository
- Authentication credentials should be stored in environment variables or a secure vault

## Troubleshooting

- If a database consistently fails to scrape, check if the site has changed its structure
- For JavaScript-heavy sites, ensure `use_selenium` is set to `True` in the configuration
- If you encounter CAPTCHA issues, verify your CAPTCHA solving service API key
- For rate limiting issues, try reducing the `requests_per_minute` value