"""
PubMed API Integration using E-utilities

This module provides functions to search PubMed using the official E-utilities API
instead of web scraping, which is more reliable and complies with NCBI's terms of service.

Documentation: https://www.ncbi.nlm.nih.gov/books/NBK25500/

If the API fails, it can fall back to browser automation with CAPTCHA solving.
"""

import requests
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import quote_plus
import json
import logging
import os
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("pubmed_api")

# Try to import browser automation
try:
    from browser_automation import BrowserAutomationManager
    BROWSER_AUTOMATION_AVAILABLE = True
except ImportError:
    try:
        # Try to import from the current directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir not in sys.path:
            sys.path.append(script_dir)
        from browser_automation import BrowserAutomationManager
        BROWSER_AUTOMATION_AVAILABLE = True
    except ImportError:
        logger.warning("Browser automation is not available. Make sure browser_automation.py is in the same directory.")
        BROWSER_AUTOMATION_AVAILABLE = False

# Base URLs for E-utilities
ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# Add your email here to be a good API citizen
EMAIL = "your.email@example.com"  # Replace with your email
TOOL = "medsearch"

def search_pubmed(query, max_results=10, min_date=None, max_date=None, retries=3, use_browser_fallback=True, captcha_api_key=""):
    """
    Search PubMed using the E-utilities API

    Args:
        query (str): The search query
        max_results (int): Maximum number of results to return
        min_date (str): Minimum date in format YYYY/MM/DD
        max_date (str): Maximum date in format YYYY/MM/DD
        retries (int): Number of retries if the API call fails
        use_browser_fallback (bool): Whether to fall back to browser automation if the API fails
        captcha_api_key (str): API key for CAPTCHA solving service

    Returns:
        list: List of search results
    """
    logger.info(f"Searching PubMed for: {query}")

    # Format dates for the API
    date_range = ""
    if min_date or max_date:
        min_date_str = min_date.replace("-", "/") if min_date else "1900/01/01"
        max_date_str = max_date.replace("-", "/") if max_date else datetime.now().strftime("%Y/%m/%d")
        date_range = f"&mindate={min_date_str}&maxdate={max_date_str}&datetype=pdat"

    # Build the search URL
    search_url = f"{ESEARCH_URL}?db=pubmed&term={quote_plus(query)}&retmax={max_results}&retmode=json{date_range}&tool={TOOL}&email={EMAIL}"

    # Make the search request with retries
    for attempt in range(retries):
        try:
            logger.info(f"  API call attempt {attempt + 1}/{retries}")
            response = requests.get(search_url)
            response.raise_for_status()
            search_results = response.json()

            # Extract the PMIDs
            pmids = search_results.get('esearchresult', {}).get('idlist', [])
            if not pmids:
                logger.info("  No results found")
                return []

            logger.info(f"  Found {len(pmids)} results")

            # Get details for each PMID
            return get_article_details(pmids)

        except Exception as e:
            logger.error(f"  Error in search attempt {attempt + 1}: {str(e)}")
            if attempt < retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.info(f"  Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error("  All API search attempts failed")

                # Try browser automation as a fallback
                if use_browser_fallback and BROWSER_AUTOMATION_AVAILABLE:
                    logger.info("  Falling back to browser automation")
                    return search_pubmed_with_browser(query, max_results, min_date, max_date, captcha_api_key)

                return []

def search_pubmed_with_browser(query, max_results=10, min_date=None, max_date=None, captcha_api_key=""):
    """
    Search PubMed using browser automation with CAPTCHA solving

    Args:
        query (str): The search query
        max_results (int): Maximum number of results to return
        min_date (str): Minimum date in format YYYY-MM-DD
        max_date (str): Maximum date in format YYYY-MM-DD
        captcha_api_key (str): API key for CAPTCHA solving service

    Returns:
        list: List of search results
    """
    logger.info(f"Searching PubMed with browser automation for: {query}")

    # Initialize browser automation
    browser_manager = BrowserAutomationManager(captcha_api_key=captcha_api_key)

    try:
        # Create a browser instance
        browser_id = f"pubmed_{int(time.time())}"
        browser_manager.create_browser(browser_id, headless=True)
        browser = browser_manager.get_browser(browser_id)

        if not browser:
            logger.error("Failed to create browser instance")
            return []

        # Navigate to PubMed
        pubmed_url = "https://pubmed.ncbi.nlm.nih.gov/"
        if not browser.navigate_to(pubmed_url):
            logger.error(f"Failed to navigate to {pubmed_url}")
            return []

        # Build the search URL with date filters
        search_url = f"https://pubmed.ncbi.nlm.nih.gov/?term={quote_plus(query)}"

        # Add date filters if provided
        if min_date or max_date:
            date_filter = "&filter=dates.custom%3A"
            if min_date:
                date_filter += min_date.replace("-", "%2F")
            else:
                date_filter += "1900%2F01%2F01"

            date_filter += "-"

            if max_date:
                date_filter += max_date.replace("-", "%2F")
            else:
                date_filter += datetime.now().strftime("%Y%%2F%m%%2F%d")

            search_url += date_filter

        # Navigate to the search URL
        if not browser.navigate_to(search_url):
            logger.error(f"Failed to navigate to {search_url}")
            return []

        # Check for CAPTCHA
        if "captcha" in browser.get_page_source().lower() or "robot" in browser.get_page_source().lower():
            logger.info("CAPTCHA detected, attempting to solve...")

            # Try to solve the CAPTCHA
            if not browser.solve_captcha():
                logger.error("Failed to solve CAPTCHA")
                return []

            logger.info("CAPTCHA solved successfully")

        # Extract search results
        results = []

        # Get the page source
        html = browser.get_page_source()

        # Parse the HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # Find all result items
        result_items = soup.select(".docsum-content, .results-article")

        logger.info(f"Found {len(result_items)} results on the page")

        for i, item in enumerate(result_items):
            if i >= max_results:
                break

            try:
                # Extract title
                title_elem = item.select_one(".docsum-title, .title")
                title = title_elem.get_text().strip() if title_elem else ""

                # Extract URL
                url = ""
                link_elem = title_elem.find("a") if title_elem else None
                if link_elem and link_elem.get("href"):
                    url = "https://pubmed.ncbi.nlm.nih.gov" + link_elem.get("href")

                # Extract PMID
                pmid = ""
                if url:
                    pmid = url.split("/")[-2] if url.endswith("/") else url.split("/")[-1]

                # Extract date
                date_elem = item.select_one(".docsum-journal-citation date, .pub-date")
                date = date_elem.get_text().strip() if date_elem else ""

                # Try to convert to YYYY-MM-DD format
                if date:
                    try:
                        # Parse various date formats
                        date_formats = [
                            "%Y %b %d",
                            "%Y %b",
                            "%b %Y",
                            "%Y"
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

                # Extract snippet/abstract
                snippet_elem = item.select_one(".full-view-snippet, .abstract")
                snippet = snippet_elem.get_text().strip() if snippet_elem else ""

                if not snippet:
                    # Try to get the citation as snippet
                    citation_elem = item.select_one(".docsum-citation, .citation")
                    snippet = citation_elem.get_text().strip() if citation_elem else ""

                # Extract authors
                authors = []
                authors_elem = item.select_one(".docsum-authors, .authors")
                if authors_elem:
                    author_text = authors_elem.get_text().strip()
                    author_list = author_text.split(",")
                    authors = [author.strip() for author in author_list]

                # Create the result object
                result = {
                    "id": f"pubmed-{pmid}" if pmid else f"pubmed-{i}",
                    "title": title,
                    "url": url,
                    "source": "PubMed",
                    "date": date,
                    "snippet": snippet[:300] + "..." if len(snippet) > 300 else snippet,
                    "authors": authors
                }

                results.append(result)

            except Exception as e:
                logger.error(f"Error processing result {i}: {str(e)}")
                continue

        return results

    except Exception as e:
        logger.error(f"Error in browser automation: {str(e)}")
        return []

    finally:
        # Close the browser
        browser_manager.close_all_browsers()

def get_article_details(pmids, retries=3):
    """
    Get details for a list of PubMed IDs using the ESummary API

    Args:
        pmids (list): List of PubMed IDs
        retries (int): Number of retries if the API call fails

    Returns:
        list: List of article details
    """
    if not pmids:
        return []

    # Join PMIDs with commas for the API
    pmid_list = ",".join(pmids)

    # Build the summary URL
    summary_url = f"{ESUMMARY_URL}?db=pubmed&id={pmid_list}&retmode=json&tool={TOOL}&email={EMAIL}"

    # Make the summary request with retries
    for attempt in range(retries):
        try:
            print(f"  Fetching details for {len(pmids)} articles, attempt {attempt + 1}/{retries}")
            response = requests.get(summary_url)
            response.raise_for_status()
            summary_results = response.json()

            # Extract the article details
            results = []
            for pmid in pmids:
                if pmid in summary_results.get('result', {}):
                    article = summary_results['result'][pmid]

                    # Extract authors
                    authors = []
                    if 'authors' in article:
                        for author in article['authors']:
                            if 'name' in author:
                                authors.append(author['name'])

                    # Extract date
                    date = ""
                    if 'pubdate' in article:
                        date = article['pubdate']
                        # Try to convert to YYYY-MM-DD format
                        try:
                            # Handle various date formats
                            if len(date) >= 4:  # At least has a year
                                year = date[:4]
                                month = "01"
                                day = "01"

                                # Try to extract month and day if available
                                parts = date.split()
                                if len(parts) >= 2:
                                    # Handle formats like "2023 Jan" or "2023 Jan 15"
                                    month_map = {
                                        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
                                        "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
                                        "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
                                    }
                                    if parts[1] in month_map:
                                        month = month_map[parts[1]]

                                        # Try to extract day
                                        if len(parts) >= 3 and parts[2].isdigit():
                                            day = parts[2].zfill(2)

                                date = f"{year}-{month}-{day}"
                        except Exception:
                            # If date parsing fails, keep the original format
                            pass

                    # Get the abstract using EFetch
                    abstract = get_abstract(pmid)

                    # Create the result object
                    result = {
                        "id": f"pubmed-{pmid}",
                        "title": article.get('title', ''),
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        "source": "PubMed",
                        "date": date,
                        "snippet": abstract[:300] + "..." if len(abstract) > 300 else abstract,
                        "authors": authors
                    }

                    results.append(result)

            return results

        except Exception as e:
            print(f"  Error in details attempt {attempt + 1}: {str(e)}")
            if attempt < retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"  Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("  All details attempts failed")
                return []

def get_abstract(pmid, retries=3):
    """
    Get the abstract for a PubMed ID using the EFetch API

    Args:
        pmid (str): PubMed ID
        retries (int): Number of retries if the API call fails

    Returns:
        str: Abstract text
    """
    # Build the fetch URL
    fetch_url = f"{EFETCH_URL}?db=pubmed&id={pmid}&rettype=abstract&retmode=text&tool={TOOL}&email={EMAIL}"

    # Make the fetch request with retries
    for attempt in range(retries):
        try:
            response = requests.get(fetch_url)
            response.raise_for_status()
            return response.text.strip()

        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return "Abstract not available"

if __name__ == "__main__":
    # Test the API
    results = search_pubmed("paracetamol", max_results=5)
    print(json.dumps(results, indent=2))
