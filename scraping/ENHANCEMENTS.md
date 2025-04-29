# MedSearch Scraping Enhancements

This document outlines the recent enhancements made to the MedSearch scraping utilities to improve reliability, efficiency, and data access capabilities.

## 1. Official API Integration

We've implemented a system that prioritizes official APIs over web scraping when available:

- Added `api-integration.ts` utility that checks if a database has an official API
- Automatically uses official APIs (like FDA's API) instead of scraping when possible
- Falls back to scraping only when API access fails or is unavailable
- Configured API-specific parameters for optimal results

### Benefits

- More reliable data access
- Reduced risk of being blocked by websites
- Better compliance with terms of service
- Faster and more efficient data retrieval

## 2. Enhanced Retry Mechanisms

We've implemented sophisticated retry logic to handle temporary unavailability:

- Added exponential backoff with jitter to prevent thundering herd problems
- Configurable retry parameters (max retries, initial delay, max delay, etc.)
- Improved error handling and reporting
- Implemented in both TypeScript (for Next.js) and Python (for scraping utilities)

### Example Usage

```typescript
// TypeScript
import { fetchWithRetry } from '@/lib/scraping';

const response = await fetchWithRetry('https://example.com', {
  method: 'GET',
  headers: { 'Content-Type': 'application/json' }
});
```

```python
# Python
from scraper import fetch_with_retry

response = fetch_with_retry('https://example.com', retries=3)
if response:
    # Process the response
    print(response.text)
```

## 3. Paywall Bypass Capabilities

We've added utilities to find open-access alternatives to paywalled content:

- Detection of common paywall domains
- Integration with open access sources like:
  - PubMed Central
  - Unpaywall
  - arXiv, bioRxiv, medRxiv
  - Directory of Open Access Journals
- Confidence scoring for alternative sources

### How It Works

1. The system detects if a URL is likely behind a paywall
2. It searches for open-access alternatives using DOI, title, or author information
3. Results are ranked by confidence and returned to the user

## Implementation Details

### New Files

- `api-integration.ts`: Handles official API integration and fallback logic
- `retry-utils.ts`: Provides enhanced retry mechanisms with exponential backoff
- `paywall-bypass.ts`: Implements open-access alternative finding

### Modified Files

- `index.ts`: Updated to integrate new utilities and improve scraping workflow
- `utils.py`: Enhanced retry handler with exponential backoff and jitter
- `scraper.py`: Added fetch_with_retry function for more reliable requests

## Usage in MedSearch

These enhancements are automatically used by the MedSearch application when performing searches. The system will:

1. First try to use official APIs when available
2. Fall back to scraping with retry mechanisms if needed
3. Attempt to find open-access alternatives for paywalled content

No changes to the existing API are required - all improvements are backward compatible.