"""
MHRA (Medicines and Healthcare products Regulatory Agency) API Integration

This module provides functions to search the MHRA medicines database using their API
and advanced web scraping techniques when needed.

MHRA has a search API that we can use to get real data.
"""

import requests
import time
from datetime import datetime
from urllib.parse import quote_plus, urljoin
import json
from bs4 import BeautifulSoup

# Base URLs for MHRA
MHRA_SEARCH_URL = "https://products.mhra.gov.uk/api/search"
MHRA_BASE_URL = "https://products.mhra.gov.uk"

def search_mhra_medicines(query, max_results=10, min_date=None, max_date=None, retries=3):
    """
    Search MHRA medicines database
    
    Args:
        query (str): The search query
        max_results (int): Maximum number of results to return
        min_date (str): Minimum date in format YYYY-MM-DD
        max_date (str): Maximum date in format YYYY-MM-DD
        retries (int): Number of retries if the API call fails
        
    Returns:
        list: List of search results
    """
    print(f"Searching MHRA medicines database for: {query}")
    
    # Build the search payload
    payload = {
        "query": query,
        "page": 1,
        "pageSize": max_results,
        "productTypes": ["medicines"]
    }
    
    # Make the search request with retries
    for attempt in range(retries):
        try:
            print(f"  API call attempt {attempt + 1}/{retries}")
            
            # Set headers to mimic a browser
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://products.mhra.gov.uk/",
                "Origin": "https://products.mhra.gov.uk"
            }
            
            response = requests.post(MHRA_SEARCH_URL, json=payload, headers=headers)
            response.raise_for_status()
            
            # Check if the response is JSON
            try:
                search_results = response.json()
            except json.JSONDecodeError:
                print("  Response is not JSON, trying to parse HTML")
                return parse_mhra_html_results(response.text, query, max_results)
            
            # Process JSON results
            results = []
            
            # Check if we have results in the expected format
            if 'results' not in search_results:
                print("  Unexpected JSON format, trying to parse HTML")
                return parse_mhra_html_results(response.text, query, max_results)
            
            for medicine in search_results['results']:
                try:
                    # Extract basic information
                    title = medicine.get('name', '')
                    product_id = medicine.get('productId', '')
                    
                    # Construct URL
                    url = f"{MHRA_BASE_URL}/substance-product/{product_id}" if product_id else f"{MHRA_BASE_URL}/search?query={quote_plus(title)}"
                    
                    # Extract date
                    date = ""
                    if 'authorisationDate' in medicine:
                        date_str = medicine['authorisationDate']
                        # Convert to YYYY-MM-DD format if needed
                        if date_str:
                            try:
                                # Parse various date formats
                                date_formats = [
                                    "%Y-%m-%d",
                                    "%d/%m/%Y",
                                    "%Y%m%d"
                                ]
                                
                                for fmt in date_formats:
                                    try:
                                        date_obj = datetime.strptime(date_str, fmt)
                                        date = date_obj.strftime("%Y-%m-%d")
                                        break
                                    except ValueError:
                                        continue
                            except Exception:
                                date = date_str
                    
                    # Extract snippet/description
                    snippet = ""
                    if 'activeSubstances' in medicine:
                        active_substances = medicine['activeSubstances']
                        if active_substances:
                            snippet = f"Active substances: {', '.join(active_substances)}. "
                    
                    if 'productType' in medicine:
                        snippet += f"Product type: {medicine['productType']}. "
                        
                    if 'marketingStatus' in medicine:
                        snippet += f"Status: {medicine['marketingStatus']}."
                    
                    # Limit snippet length
                    if len(snippet) > 300:
                        snippet = snippet[:297] + "..."
                    
                    # Extract authors/manufacturers
                    authors = []
                    if 'marketingAuthorisationHolder' in medicine:
                        authors.append(medicine['marketingAuthorisationHolder'])
                    
                    # Create the result object
                    result = {
                        "id": f"mhra-{product_id}" if product_id else f"mhra-{hash(title) % 10000}",
                        "title": title,
                        "url": url,
                        "source": "MHRA",
                        "date": date,
                        "snippet": snippet,
                        "authors": authors
                    }
                    
                    # Filter by date if needed
                    if min_date or max_date:
                        if not date:
                            # Include results without dates
                            results.append(result)
                        else:
                            try:
                                result_date = datetime.strptime(date, "%Y-%m-%d")
                                min_date_obj = datetime.strptime(min_date, "%Y-%m-%d") if min_date else datetime(1900, 1, 1)
                                max_date_obj = datetime.strptime(max_date, "%Y-%m-%d") if max_date else datetime.now()
                                
                                if min_date_obj <= result_date <= max_date_obj:
                                    results.append(result)
                            except ValueError:
                                # Include results with unparseable dates
                                results.append(result)
                    else:
                        results.append(result)
                except Exception as e:
                    print(f"  Error processing medicine result: {str(e)}")
                    continue
            
            print(f"  Found {len(results)} results")
            return results
            
        except Exception as e:
            print(f"  Error in search attempt {attempt + 1}: {str(e)}")
            if attempt < retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"  Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("  All search attempts failed")
                return []

def parse_mhra_html_results(html_content, query, max_results):
    """
    Parse HTML search results from MHRA website
    
    Args:
        html_content (str): HTML content to parse
        query (str): The original search query
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of search results
    """
    print("  Parsing HTML search results")
    results = []
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all medicine items
        medicine_items = soup.select('.search-results .search-result')
        
        for i, item in enumerate(medicine_items):
            if i >= max_results:
                break
                
            try:
                # Extract title and URL
                title_elem = item.select_one('h2 a, .title a')
                if not title_elem:
                    continue
                    
                title = title_elem.get_text().strip()
                url = urljoin(MHRA_BASE_URL, title_elem.get('href', ''))
                
                # Extract date
                date_elem = item.select_one('.date, .authorisation-date')
                date = date_elem.get_text().strip() if date_elem else ""
                
                # Try to convert to YYYY-MM-DD format
                if date:
                    try:
                        # Parse various date formats
                        date_formats = [
                            "%d/%m/%Y",
                            "%Y-%m-%d",
                            "%d %B %Y"
                        ]
                        
                        for fmt in date_formats:
                            try:
                                date_obj = datetime.strptime(date, fmt)
                                date = date_obj.strftime("%Y-%m-%d")
                                break
                            except ValueError:
                                continue
                    except Exception:
                        pass
                
                # Extract snippet
                snippet_elem = item.select_one('.description, .summary')
                snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                
                # Limit snippet length
                if len(snippet) > 300:
                    snippet = snippet[:297] + "..."
                
                # Extract authors/manufacturers
                authors = []
                author_elem = item.select_one('.manufacturer, .marketing-authorisation-holder')
                if author_elem:
                    authors.append(author_elem.get_text().strip())
                
                # Create the result object
                result = {
                    "id": f"mhra-{hash(url) % 10000}",
                    "title": title,
                    "url": url,
                    "source": "MHRA",
                    "date": date,
                    "snippet": snippet,
                    "authors": authors
                }
                
                results.append(result)
                
            except Exception as e:
                print(f"  Error processing HTML item {i}: {str(e)}")
                continue
        
        print(f"  Found {len(results)} results from HTML parsing")
        return results
        
    except Exception as e:
        print(f"  Error parsing HTML: {str(e)}")
        return []

if __name__ == "__main__":
    # Test the API
    results = search_mhra_medicines("paracetamol", max_results=5)
    print(json.dumps(results, indent=2))
