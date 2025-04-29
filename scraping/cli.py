#!/usr/bin/env python
"""
Command-line interface for MedSearch advanced scraping utilities

This script provides a convenient way to use the advanced scraping utilities
from the command line, making it easier to test and debug scraping operations.
"""

import argparse
import json
import sys
from typing import Dict, Any, List

from utils import (
    ProxyManager,
    CaptchaSolver,
    AuthManager,
    RateLimiter,
    RetryHandler,
    AdvancedScraper
)
from config import (
    DEFAULT_PROXIES,
    CAPTCHA_CONFIG,
    AUTH_CREDENTIALS,
    get_database_config,
    get_rate_limit
)
from bs4 import BeautifulSoup


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="MedSearch Advanced Scraping CLI")
    
    # Required arguments
    parser.add_argument("--url", required=True, help="URL to scrape")
    parser.add_argument("--query", required=True, help="Search query")
    
    # Database configuration
    parser.add_argument("--database", help="Database ID to use predefined configuration")
    
    # Advanced options
    parser.add_argument("--use-proxies", action="store_true", help="Use proxy rotation")
    parser.add_argument("--use-captcha-solver", action="store_true", help="Use CAPTCHA solver")
    parser.add_argument("--use-authentication", action="store_true", help="Use authentication")
    parser.add_argument("--respect-rate-limits", action="store_true", help="Respect rate limits")
    parser.add_argument("--use-selenium", action="store_true", help="Use Selenium for JavaScript-heavy sites")
    parser.add_argument("--max-retries", type=int, default=3, help="Maximum number of retries")
    parser.add_argument("--requests-per-minute", type=int, default=10, help="Requests per minute")
    parser.add_argument("--wait-time", type=int, default=5, help="Wait time for Selenium (seconds)")
    
    # Output options
    parser.add_argument("--output", help="Output file path (JSON format)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    return parser.parse_args()


def extract_search_results(html: str, url: str, query: str) -> List[Dict[str, Any]]:
    """Extract search results from HTML"""
    results = []
    
    if not html:
        return results
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract domain for source information
    domain = url.split('//')[1].split('/')[0]
    if domain.startswith('www.'):
        domain = domain[4:]
    
    # Generic extraction logic - customize for specific sites as needed
    for result in soup.select('.search-result, .result-item, article, .item, li, tr, div.result'):
        title_elem = result.select_one('h2, h3, .title, .heading, a, strong')
        link_elem = result.select_one('a')
        snippet_elem = result.select_one('p, .description, .snippet, .summary, .content')
        date_elem = result.select_one('.date, time, .published')
        
        # Skip if no title or link found
        if not title_elem and not link_elem:
            continue
        
        title = title_elem.get_text(strip=True) if title_elem else 'No title'
        link = link_elem['href'] if link_elem and 'href' in link_elem.attrs else ''
        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
        date = date_elem.get_text(strip=True) if date_elem else ''
        
        # Ensure link is absolute
        if link and not link.startswith('http'):
            if link.startswith('/'):
                # Get domain from the original URL
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                domain_base = f"{parsed_url.scheme}://{parsed_url.netloc}"
                link = f"{domain_base}{link}"
            else:
                link = f"{url.rstrip('/')}/{link.lstrip('/')}"
        
        # Check if the result is relevant to the query
        query_terms = query.lower().split()
        result_text = f"{title} {snippet}".lower()
        
        # Simple relevance check - at least one query term must be in the result
        is_relevant = any(term in result_text for term in query_terms)
        
        if is_relevant or not query_terms:  # Include all results if no query terms
            results.append({
                'id': f"scraped-{len(results)}",
                'title': title,
                'url': link,
                'source': domain,
                'date': date,
                'snippet': snippet or 'No description available',
                'authors': [],
                'relevanceScore': 1.0
            })
    
    return results


def main():
    """Main function"""
    args = parse_arguments()
    
    # If database ID is provided, use its configuration
    if args.database:
        db_config = get_database_config(args.database)
        use_proxies = db_config.get("use_proxies", args.use_proxies)
        use_captcha_solver = db_config.get("use_captcha_solver", args.use_captcha_solver)
        use_authentication = db_config.get("use_authentication", args.use_authentication)
        respect_rate_limits = db_config.get("respect_rate_limits", args.respect_rate_limits)
        use_selenium = db_config.get("use_selenium", args.use_selenium)
        max_retries = db_config.get("max_retries", args.max_retries)
        requests_per_minute = db_config.get("requests_per_minute", args.requests_per_minute)
        wait_time = db_config.get("wait_time", args.wait_time)
    else:
        use_proxies = args.use_proxies
        use_captcha_solver = args.use_captcha_solver
        use_authentication = args.use_authentication
        respect_rate_limits = args.respect_rate_limits
        use_selenium = args.use_selenium
        max_retries = args.max_retries
        requests_per_minute = args.requests_per_minute
        wait_time = args.wait_time
    
    # Initialize components
    proxy_manager = ProxyManager(DEFAULT_PROXIES) if use_proxies else None
    captcha_solver = CaptchaSolver(CAPTCHA_CONFIG["api_key"], CAPTCHA_CONFIG["service"]) if use_captcha_solver else None
    auth_manager = AuthManager() if use_authentication else None
    rate_limiter = RateLimiter() if respect_rate_limits else None
    retry_handler = RetryHandler(max_retries=max_retries)
    
    # Initialize the scraper
    scraper = AdvancedScraper(
        proxy_manager=proxy_manager,
        captcha_solver=captcha_solver,
        auth_manager=auth_manager,
        rate_limiter=rate_limiter,
        retry_handler=retry_handler
    )
    
    # Extract domain for rate limiting
    domain = args.url.split('//')[1].split('/')[0]
    if domain.startswith('www.'):
        domain = domain[4:]
    
    # Get rate limit for this domain
    domain_rate_limit = get_rate_limit(domain) if respect_rate_limits else requests_per_minute
    
    if args.verbose:
        print(f"Scraping {args.url} for query: {args.query}")
        print(f"Configuration:")
        print(f"  - Use proxies: {use_proxies}")
        print(f"  - Use CAPTCHA solver: {use_captcha_solver}")
        print(f"  - Use authentication: {use_authentication}")
        print(f"  - Respect rate limits: {respect_rate_limits}")
        print(f"  - Use Selenium: {use_selenium}")
        print(f"  - Max retries: {max_retries}")
        print(f"  - Requests per minute: {domain_rate_limit}")
        print(f"  - Wait time: {wait_time} seconds")
    
    # Scrape the website
    if use_selenium:
        if args.verbose:
            print("Using Selenium for scraping...")
        html = scraper.scrape_with_selenium(
            url=args.url,
            wait_time=wait_time,
            use_proxy=use_proxies,
            handle_captcha=use_captcha_solver
        )
    else:
        if args.verbose:
            print("Using requests for scraping...")
        html = scraper.scrape_with_requests(
            url=args.url,
            use_proxy=use_proxies,
            respect_rate_limit=respect_rate_limits,
            requests_per_minute=domain_rate_limit,
            use_auth=use_authentication
        )
    
    # Process the results
    if html:
        results = extract_search_results(html, args.url, args.query)
        
        if args.verbose:
            print(f"Found {len(results)} results")
        
        # Output results
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            if args.verbose:
                print(f"Results saved to {args.output}")
        else:
            # Print results to stdout
            print(json.dumps(results, indent=2))
    else:
        if args.verbose:
            print("No HTML content retrieved")
        print(json.dumps([]))


if __name__ == "__main__":
    main()