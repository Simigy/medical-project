/**
 * MedSearch Advanced Scraping Integration
 * 
 * This module provides an interface between the Python scraping utilities
 * and the Next.js application, allowing for advanced scraping techniques
 * to be used when accessing restricted medical databases.
 * 
 * Enhanced with official API integration, improved retry mechanisms,
 * and paywall bypass capabilities.
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import fs from 'fs';
import type { SearchResult } from '@/types';

// Import enhanced utilities
import { hasOfficialApi, searchWithOfficialApi, shouldUseOfficialApi } from './api-integration';
import { fetchWithRetry, withRetry, defaultRetryConfig } from './retry-utils';
import { findOpenAccessAlternatives, isLikelyPaywalled } from './paywall-bypass';

const execAsync = promisify(exec);

// Configuration for different scraping strategies
export interface ScrapingConfig {
  useProxies: boolean;
  useCaptchaSolver: boolean;
  useAuthentication: boolean;
  respectRateLimits: boolean;
  maxRetries: number;
  requestsPerMinute: number;
}

// Default configuration
const defaultConfig: ScrapingConfig = {
  useProxies: false,
  useCaptchaSolver: false,
  useAuthentication: false,
  respectRateLimits: true,
  maxRetries: 3,
  requestsPerMinute: 10
};

/**
 * Get the absolute path to the Python scraping utilities
 */
function getScrapingUtilsPath(): string {
  return path.join(process.cwd(), 'scraping', 'utils.py');
}

/**
 * Execute a Python script with the given arguments
 */
async function executePythonScript(scriptPath: string, args: string[]): Promise<string> {
  try {
    const { stdout, stderr } = await execAsync(`python "${scriptPath}" ${args.join(' ')}`);
    
    if (stderr) {
      console.error(`Python script error: ${stderr}`);
    }
    
    return stdout;
  } catch (error) {
    console.error('Failed to execute Python script:', error);
    throw error;
  }
}

/**
 * Create a command to run the Python scraper with the given configuration
 */
function createScrapingCommand(url: string, query: string, config: ScrapingConfig): string[] {
  const args = [
    `--url="${url}"`,
    `--query="${query}"`,
    `--use-proxies=${config.useProxies ? 'true' : 'false'}`,
    `--use-captcha-solver=${config.useCaptchaSolver ? 'true' : 'false'}`,
    `--use-authentication=${config.useAuthentication ? 'true' : 'false'}`,
    `--respect-rate-limits=${config.respectRateLimits ? 'true' : 'false'}`,
    `--max-retries=${config.maxRetries}`,
    `--requests-per-minute=${config.requestsPerMinute}`
  ];
  
  return args;
}

/**
 * Scrape a website using the advanced scraping utilities
 * Enhanced with API integration, retry mechanisms, and paywall bypass
 */
export async function scrapeWithAdvancedTechniques(
  url: string, 
  query: string, 
  config: Partial<ScrapingConfig> = {},
  databaseId?: string
): Promise<SearchResult[]> {
  // If database ID is provided and it has an official API, use that instead
  if (databaseId && shouldUseOfficialApi(databaseId)) {
    try {
      console.log(`Using official API for ${databaseId} instead of scraping`);
      return await searchWithOfficialApi(databaseId, query);
    } catch (error) {
      console.error(`Error using official API for ${databaseId}:`, error);
      console.log('Falling back to scraping...');
    }
  }
  
  // Merge default config with provided config
  const mergedConfig: ScrapingConfig = { ...defaultConfig, ...config };
  
  // Check if URL is likely paywalled
  if (isLikelyPaywalled(url)) {
    console.log(`URL ${url} appears to be behind a paywall, searching for open access alternatives...`);
    try {
      // This would need additional metadata about the article
      const openAccessResults = await findOpenAccessAlternatives(null, query);
      if (openAccessResults.length > 0) {
        console.log(`Found ${openAccessResults.length} open access alternatives`);
        // Convert open access results to search results
        return openAccessResults.map(result => ({
          id: `oa-${Math.random().toString(36).substring(7)}`,
          title: result.title,
          url: result.url,
          source: `Open Access (via ${result.source})`,
          date: new Date().toISOString().split('T')[0],
          snippet: `Open access version found via ${result.source}`,
          authors: [],
          relevanceScore: result.confidence
        }));
      }
    } catch (error) {
      console.error('Error finding open access alternatives:', error);
    }
  }
  
  try {
    // Use retry mechanism for better reliability
    return await withRetry(async () => {
      // Create a temporary script that uses our utils.py
      const tempScriptPath = path.join(process.cwd(), 'scraping', 'temp_scraper.py');
    const scriptContent = `
import sys
import json
import argparse
from utils import AdvancedScraper, ProxyManager, RateLimiter, RetryHandler
from bs4 import BeautifulSoup

# Parse command line arguments
parser = argparse.ArgumentParser(description='Advanced web scraping')
parser.add_argument('--url', required=True, help='URL to scrape')
parser.add_argument('--query', required=True, help='Search query')
parser.add_argument('--use-proxies', default='false', help='Use proxy rotation')
parser.add_argument('--use-captcha-solver', default='false', help='Use CAPTCHA solver')
parser.add_argument('--use-authentication', default='false', help='Use authentication')
parser.add_argument('--respect-rate-limits', default='true', help='Respect rate limits')
parser.add_argument('--max-retries', type=int, default=3, help='Maximum number of retries')
parser.add_argument('--requests-per-minute', type=int, default=10, help='Requests per minute')
args = parser.parse_args()

# Convert string arguments to boolean
use_proxies = args.use_proxies.lower() == 'true'
use_captcha_solver = args.use_captcha_solver.lower() == 'true'
use_authentication = args.use_authentication.lower() == 'true'
respect_rate_limits = args.respect_rate_limits.lower() == 'true'

# Initialize components
proxy_manager = ProxyManager()
rate_limiter = RateLimiter()
retry_handler = RetryHandler(max_retries=args.max_retries)

# Initialize the scraper
scraper = AdvancedScraper(
    proxy_manager=proxy_manager,
    rate_limiter=rate_limiter,
    retry_handler=retry_handler
)

# Determine if we should use requests or selenium based on the URL
# For this example, we'll use a simple heuristic
use_selenium = False
if 'javascript-heavy-site.com' in args.url or 'requires-js.org' in args.url:
    use_selenium = True

# Scrape the website
if use_selenium:
    html = scraper.scrape_with_selenium(
        url=args.url,
        use_proxy=use_proxies,
        handle_captcha=use_captcha_solver
    )
else:
    html = scraper.scrape_with_requests(
        url=args.url,
        use_proxy=use_proxies,
        respect_rate_limit=respect_rate_limits,
        requests_per_minute=args.requests_per_minute,
        use_auth=use_authentication
    )

# Process the results
results = []
if html:
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract data based on the URL/site structure
    # This is a simplified example - you would need to customize this for each site
    
    # Example: Extract search results from a generic page
    for result in soup.select('.search-result, .result-item, article, .item'):
        title_elem = result.select_one('h2, h3, .title, .heading')
        link_elem = result.select_one('a')
        snippet_elem = result.select_one('p, .description, .snippet, .summary')
        date_elem = result.select_one('.date, time, .published')
        
        title = title_elem.get_text(strip=True) if title_elem else 'No title'
        url = link_elem['href'] if link_elem and 'href' in link_elem.attrs else ''
        snippet = snippet_elem.get_text(strip=True) if snippet_elem else 'No description'
        date = date_elem.get_text(strip=True) if date_elem else ''
        
        # Ensure URL is absolute
        if url and not url.startswith('http'):
            if url.startswith('/'):
                # Get domain from the original URL
                from urllib.parse import urlparse
                parsed_url = urlparse(args.url)
                domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
                url = f"{domain}{url}"
            else:
                url = f"{args.url.rstrip('/')}/{url.lstrip('/')}"
        
        results.append({
            'id': f"scraped-{len(results)}",
            'title': title,
            'url': url,
            'source': 'Scraped Result',
            'date': date,
            'snippet': snippet,
            'authors': [],
            'relevanceScore': 1.0
        })

# Output results as JSON
print(json.dumps(results))
`;

    // Write the temporary script
    fs.writeFileSync(tempScriptPath, scriptContent);

    try {
      // Execute the script
      const args = createScrapingCommand(url, query, mergedConfig);
      const output = await executePythonScript(tempScriptPath, args);
      
      // Parse the results
      const results: SearchResult[] = JSON.parse(output);
      return results;
    } finally {
      // Clean up the temporary script
      if (fs.existsSync(tempScriptPath)) {
        fs.unlinkSync(tempScriptPath);
      }
    }
    }, {
      maxRetries: mergedConfig.maxRetries,
      initialDelayMs: 2000,
      backoffFactor: 2,
      jitterFactor: 0.3
    });
  } catch (error) {
    console.error('Error during advanced scraping:', error);
    return [];
  }
}

/**
 * Configure proxy settings for the scraper
 */
export async function configureProxies(proxies: string[]): Promise<boolean> {
  try {
    // Create a temporary script to configure proxies
    const tempScriptPath = path.join(process.cwd(), 'scraping', 'configure_proxies.py');
    const scriptContent = `
import json
import sys
import os

# Get the proxies from command line
proxies_json = sys.argv[1]
proxies = json.loads(proxies_json)

# Save proxies to a configuration file
config_dir = os.path.join(os.path.dirname(__file__), 'config')
os.makedirs(config_dir, exist_ok=True)

with open(os.path.join(config_dir, 'proxies.json'), 'w') as f:
    json.dump(proxies, f)

print("Proxies configured successfully")
`;

    // Write the temporary script
    fs.writeFileSync(tempScriptPath, scriptContent);

    try {
      // Execute the script
      const proxiesJson = JSON.stringify(proxies);
      await executePythonScript(tempScriptPath, [proxiesJson]);
      return true;
    } finally {
      // Clean up the temporary script
      if (fs.existsSync(tempScriptPath)) {
        fs.unlinkSync(tempScriptPath);
      }
    }
  } catch (error) {
    console.error('Error configuring proxies:', error);
    return false;
  }
}

/**
 * Get database-specific scraping configuration
 */
export function getDatabaseScrapingConfig(databaseId: string): ScrapingConfig {
  // Define database-specific configurations
  const databaseConfigs: Record<string, Partial<ScrapingConfig>> = {
    'swissmedic': {
      useProxies: true,
      respectRateLimits: true,
      requestsPerMinute: 5,
      maxRetries: 5
    },
    'ema-medicines': {
      useProxies: true,
      respectRateLimits: true,
      requestsPerMinute: 10
    },
    'mhra': {
      useProxies: false,
      respectRateLimits: true,
      requestsPerMinute: 15
    },
    'tga': {
      useProxies: true,
      respectRateLimits: true,
      requestsPerMinute: 8
    },
    'medsafe': {
      useProxies: false,
      respectRateLimits: true,
      requestsPerMinute: 20
    },
    'fda-drugs': {
      // FDA has an official API, so we'll use minimal scraping settings
      useProxies: false,
      respectRateLimits: true,
      requestsPerMinute: 30,
      maxRetries: 2
    }
  };
  
  // Return database-specific config or default
  return { ...defaultConfig, ...(databaseConfigs[databaseId] || {}) };
}

/**
 * Check if a database requires advanced scraping techniques
 */
export function requiresAdvancedScraping(databaseId: string): boolean {
  // If the database has an official API, we don't need advanced scraping
  if (shouldUseOfficialApi(databaseId)) {
    return false;
  }
  
  // List of databases that require advanced scraping
  const advancedScrapingDatabases = [
    'swissmedic',
    'ema-medicines',
    'mhra',
    'tga',
    'medsafe',
    'lakemedelsverket'
  ];
  
  return advancedScrapingDatabases.includes(databaseId);
}

/**
 * Export enhanced utilities for use in other modules
 */
export {
  hasOfficialApi,
  searchWithOfficialApi,
  shouldUseOfficialApi,
  fetchWithRetry,
  withRetry,
  defaultRetryConfig,
  findOpenAccessAlternatives,
  isLikelyPaywalled
};