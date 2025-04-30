"""
FDA API Integration using OpenFDA

This module provides functions to search the FDA's drug database using the official OpenFDA API
instead of web scraping, which is more reliable and complies with FDA's terms of service.

Documentation: https://open.fda.gov/apis/
"""

import requests
import time
from datetime import datetime
from urllib.parse import quote_plus
import json

# Base URL for OpenFDA API
OPENFDA_URL = "https://api.fda.gov/drug"

# No API key is required for basic usage, but for higher rate limits you can get one
# API_KEY = "your_api_key_here"  # Uncomment and add your key for higher rate limits

def search_fda_drugs(query, max_results=10, min_date=None, max_date=None, retries=3):
    """
    Search FDA drug database using the OpenFDA API
    
    Args:
        query (str): The search query
        max_results (int): Maximum number of results to return
        min_date (str): Minimum date in format YYYY-MM-DD
        max_date (str): Maximum date in format YYYY-MM-DD
        retries (int): Number of retries if the API call fails
        
    Returns:
        list: List of search results
    """
    print(f"Searching FDA drug database for: {query}")
    
    # Format the search query for the API
    # Search in various fields for better results
    search_query = f"(generic_name:{quote_plus(query)}+OR+brand_name:{quote_plus(query)}+OR+substance_name:{quote_plus(query)})"
    
    # Add date range if provided
    if min_date or max_date:
        min_date_str = min_date if min_date else "1900-01-01"
        max_date_str = max_date if max_date else datetime.now().strftime("%Y-%m-%d")
        search_query += f"+AND+effective_time:[{min_date_str.replace('-', '')} TO {max_date_str.replace('-', '')}]"
    
    # Build the search URL
    search_url = f"{OPENFDA_URL}/label.json?search={search_query}&limit={max_results}"
    
    # Add API key if available
    # if 'API_KEY' in globals() and API_KEY:
    #     search_url += f"&api_key={API_KEY}"
    
    # Make the search request with retries
    for attempt in range(retries):
        try:
            print(f"  API call attempt {attempt + 1}/{retries}")
            response = requests.get(search_url)
            response.raise_for_status()
            search_results = response.json()
            
            # Check if we have results
            if 'results' not in search_results or not search_results['results']:
                print("  No results found")
                return []
            
            results = []
            for drug in search_results['results']:
                # Extract drug information
                try:
                    # Get basic information
                    openfda = drug.get('openfda', {})
                    
                    # Get the brand name
                    brand_names = openfda.get('brand_name', [])
                    brand_name = brand_names[0] if brand_names else ""
                    
                    # Get the generic name
                    generic_names = openfda.get('generic_name', [])
                    generic_name = generic_names[0] if generic_names else ""
                    
                    # Get the manufacturer
                    manufacturers = openfda.get('manufacturer_name', [])
                    manufacturer = manufacturers[0] if manufacturers else ""
                    
                    # Construct a title
                    title = brand_name if brand_name else generic_name
                    if not title:
                        title = "Unnamed Drug"
                    
                    # Get the application number for the URL
                    application_numbers = openfda.get('application_number', [])
                    application_number = application_numbers[0] if application_numbers else ""
                    
                    # Construct a URL
                    url = f"https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process"
                    if application_number:
                        url += f"&ApplNo={application_number}"
                    
                    # Get the effective date
                    effective_time = drug.get('effective_time', "")
                    date = ""
                    if effective_time and len(effective_time) == 8:
                        # Convert YYYYMMDD to YYYY-MM-DD
                        date = f"{effective_time[:4]}-{effective_time[4:6]}-{effective_time[6:8]}"
                    
                    # Get the description/snippet
                    description = ""
                    if 'description' in drug:
                        description = drug['description'][0] if isinstance(drug['description'], list) else drug['description']
                    elif 'indications_and_usage' in drug:
                        description = drug['indications_and_usage'][0] if isinstance(drug['indications_and_usage'], list) else drug['indications_and_usage']
                    
                    # Create the result object
                    result = {
                        "id": f"fda-{application_number}" if application_number else f"fda-{hash(title) % 10000}",
                        "title": title,
                        "url": url,
                        "source": "FDA - Drugs",
                        "date": date,
                        "snippet": description[:300] + "..." if len(description) > 300 else description,
                        "authors": [manufacturer] if manufacturer else []
                    }
                    
                    results.append(result)
                except Exception as e:
                    print(f"  Error processing drug result: {str(e)}")
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

if __name__ == "__main__":
    # Test the API
    results = search_fda_drugs("paracetamol", max_results=5)
    print(json.dumps(results, indent=2))
