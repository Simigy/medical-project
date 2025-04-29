#!/usr/bin/env python
"""
Example script demonstrating how to use the advanced scraping utilities

This script provides a practical example of using the advanced scraping
utilities to access a medical database with various protection mechanisms.
"""

import argparse
import json
from utils import (
    ProxyManager,
    CaptchaSolver,
    AuthManager,
    RateLimiter,
    RetryHandler,
    AdvancedScraper
)
from config import get_database_config
from bs4 import BeautifulSoup


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="MedSearch Advanced Scraping Example")
    parser.add_argument("--database", default="swissmedic", help="Database ID to use")
    parser.add_argument("--query", default="paracetamol", help="Search query")
    parser.add_argument("--output", help="Output file path (JSON format)")
    return parser.parse_args()


def main():
    """Main function demonstrating advanced scraping"""
    args = parse_arguments()
    
    print(f"\n=== MedSearch Advanced Scraping Example ===")
    print(f"Database: {args.database}")
    print(f"Query: {args.query}\n")
    
    # Get database-specific configuration
    db_config = get_database_config(args.database)
    print(f"Using configuration for {args.database}:")
    for key, value in db_config.items():
        print(f"  - {key}: {value}")
    print()
    
    # Initialize components
    proxy_manager = ProxyManager()
    rate_limiter = RateLimiter()
    retry_handler = RetryHandler(max_retries=db_config.get("max_retries", 3))
    
    # Initialize the scraper
    scraper = AdvancedScraper(
        proxy_manager=proxy_manager,
        rate_limiter=rate_limiter,
        retry_handler=retry_handler
    )
    
    # Determine the URL based on the database
    if args.database == "swissmedic":
        url = f"https://www.swissmedic.ch/swissmedic/en/home/humanarzneimittel/marktueberwachung/health-professional-communication--hpc-/search.html?query={args.query}"
    elif args.database == "ema-medicines":
        url = f"https://www.ema.europa.eu/en/medicines/search?search_api_views_fulltext={args.query}"
    elif args.database == "mhra":
        url = f"https://products.mhra.gov.uk/?query={args.query}&page=1"
    else:
        url = f"https://www.google.com/search?q={args.query}+site:{args.database}"
    
    print(f"Scraping URL: {url}\n")
    
    # Scrape the website using the appropriate method
    if db_config.get("use_selenium", False):
        print("Using Selenium for scraping...")
        html = scraper.scrape_with_selenium(
            url=url,
            wait_time=db_config.get("wait_time", 5),
            use_proxy=db_config.get("use_proxies", False),
            handle_captcha=db_config.get("use_captcha_solver", False)
        )
    else:
        print("Using requests for scraping...")
        html = scraper.scrape_with_requests(
            url=url,
            use_proxy=db_config.get("use_proxies", False),
            respect_rate_limit=db_config.get("respect_rate_limits", True),
            requests_per_minute=db_config.get("requests_per_minute", 10),
            use_auth=db_config.get("use_authentication", False)
        )
    
    # Process the results
    if html:
        print("\nSuccessfully retrieved HTML content!")
        
        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract basic information
        title = soup.title.text if soup.title else "No title"
        print(f"Page title: {title}")
        
        # Count elements
        links = soup.find_all('a')
        print(f"Found {len(links)} links on the page")
        
        # Look for search results
        results = []
        
        # Generic extraction logic - customize for specific sites as needed
        for result in soup.select('.search-result, .result-item, article, .item, li, tr, div.result'):
            title_elem = result.select_one('h2, h3, .title, .heading, a, strong')
            link_elem = result.select_one('a')
            snippet_elem = result.select_one('p, .description, .snippet, .summary, .content')
            
            # Skip if no title or link found
            if not title_elem and not link_elem:
                continue
            
            title = title_elem.get_text(strip=True) if title_elem else 'No title'
            link = link_elem['href'] if link_elem and 'href' in link_elem.attrs else ''
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
            
            results.append({
                'title': title,
                'url': link,
                'snippet': snippet
            })
        
        print(f"Extracted {len(results)} potential search results")
        
        # Save results if output file specified
        if args.output and results:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to {args.output}")
            
        # Print first few results
        if results:
            print("\nFirst few results:")
            for i, result in enumerate(results[:3]):
                print(f"\nResult {i+1}:")
                print(f"Title: {result['title']}")
                print(f"URL: {result['url']}")
                if result['snippet']:
                    print(f"Snippet: {result['snippet'][:100]}...")
    else:
        print("\nFailed to retrieve HTML content!")


if __name__ == "__main__":
    main()