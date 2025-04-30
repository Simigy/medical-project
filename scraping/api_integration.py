"""
API Integration for Medical Databases

This module integrates all the individual database APIs into a single interface
for batch searching across multiple medical databases.

It includes support for:
1. Official APIs where available
2. Browser automation with human-like behavior
3. CAPTCHA solving capabilities
4. Fallback mechanisms for robust data retrieval
"""

import importlib
import concurrent.futures
import time
import json
import os
import sys
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("api_integration")

# Try to import the individual API modules
api_modules = {}

try:
    from . import pubmed_api
    api_modules["pubmed"] = pubmed_api
except ImportError:
    try:
        import pubmed_api
        api_modules["pubmed"] = pubmed_api
    except ImportError:
        print("Warning: PubMed API module not found")

try:
    from . import fda_api
    api_modules["fda-drugs"] = fda_api
except ImportError:
    try:
        import fda_api
        api_modules["fda-drugs"] = fda_api
    except ImportError:
        print("Warning: FDA API module not found")

try:
    from . import ema_api
    api_modules["ema-medicines"] = ema_api
except ImportError:
    try:
        import ema_api
        api_modules["ema-medicines"] = ema_api
    except ImportError:
        print("Warning: EMA API module not found")

try:
    from . import mhra_api
    api_modules["mhra"] = mhra_api
except ImportError:
    try:
        import mhra_api
        api_modules["mhra"] = mhra_api
    except ImportError:
        print("Warning: MHRA API module not found")

try:
    from . import tga_api
    api_modules["tga-cmi"] = tga_api
    api_modules["tga"] = tga_api
except ImportError:
    try:
        import tga_api
        api_modules["tga-cmi"] = tga_api
        api_modules["tga"] = tga_api
    except ImportError:
        print("Warning: TGA API module not found")

def search_database(db_id, query, max_results=10, min_date=None, max_date=None, captcha_api_key=""):
    """
    Search a specific database using its API or advanced scraping techniques

    Args:
        db_id (str): Database ID
        query (str): Search query
        max_results (int): Maximum number of results to return
        min_date (str): Minimum date in format YYYY-MM-DD
        max_date (str): Maximum date in format YYYY-MM-DD
        captcha_api_key (str): API key for CAPTCHA solving service

    Returns:
        list: List of search results
    """
    logger.info(f"Searching {db_id} for: {query}")

    # Check if we have an API module for this database
    if db_id in api_modules:
        module = api_modules[db_id]

        # Call the appropriate search function based on the database
        if db_id == "pubmed":
            # Use PubMed API with browser automation fallback
            return module.search_pubmed(
                query,
                max_results,
                min_date,
                max_date,
                use_browser_fallback=True,
                captcha_api_key=captcha_api_key
            )
        elif db_id == "fda-drugs":
            return module.search_fda_drugs(query, max_results, min_date, max_date)
        elif db_id == "ema-medicines":
            return module.search_ema_medicines(query, max_results, min_date, max_date)
        elif db_id == "mhra":
            return module.search_mhra_medicines(query, max_results, min_date, max_date)
        elif db_id in ["tga-cmi", "tga"]:
            # Use TGA API with browser automation and CAPTCHA solving
            return module.search_tga_medicines(
                query,
                max_results,
                min_date,
                max_date,
                retries=3,
                captcha_api_key=captcha_api_key
            )
    else:
        logger.warning(f"  No API module available for {db_id}")
        return []

def batch_search(query, database_ids, max_results=10, min_date=None, max_date=None,
              parallel=False, max_workers=4, captcha_api_key=""):
    """
    Search multiple databases in parallel or sequentially

    Args:
        query (str): Search query
        database_ids (list): List of database IDs to search
        max_results (int): Maximum number of results per database
        min_date (str): Minimum date in format YYYY-MM-DD
        max_date (str): Maximum date in format YYYY-MM-DD
        parallel (bool): Whether to search databases in parallel
        max_workers (int): Maximum number of parallel workers
        captcha_api_key (str): API key for CAPTCHA solving service

    Returns:
        list: Combined list of search results from all databases
    """
    all_results = []

    if parallel and len(database_ids) > 1:
        logger.info(f"Searching {len(database_ids)} databases in parallel with {max_workers} workers...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_db = {
                executor.submit(
                    search_database,
                    db_id,
                    query,
                    max_results,
                    min_date,
                    max_date,
                    captcha_api_key
                ): db_id
                for db_id in database_ids
            }

            for future in concurrent.futures.as_completed(future_to_db):
                db_id = future_to_db[future]
                try:
                    results = future.result()
                    all_results.extend(results)
                    logger.info(f"  Completed search for {db_id}, found {len(results)} results")
                except Exception as e:
                    logger.error(f"  Error searching {db_id}: {str(e)}")
    else:
        logger.info(f"Searching {len(database_ids)} databases sequentially...")
        for db_id in database_ids:
            try:
                results = search_database(
                    db_id,
                    query,
                    max_results,
                    min_date,
                    max_date,
                    captcha_api_key
                )
                all_results.extend(results)
                logger.info(f"  Completed search for {db_id}, found {len(results)} results")
            except Exception as e:
                logger.error(f"  Error searching {db_id}: {str(e)}")

    logger.info(f"Total results found: {len(all_results)}")
    return all_results

def save_results_to_file(results, output_file):
    """
    Save search results to a JSON file

    Args:
        results (list): List of search results
        output_file (str): Output file path

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)

        # Save the results
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        print(f"Results saved to {output_file}")
        return True
    except Exception as e:
        print(f"Error saving results: {str(e)}")
        return False

if __name__ == "__main__":
    # Example usage
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Search medical databases using APIs and advanced scraping")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--databases", nargs="+", default=["pubmed", "fda-drugs", "ema-medicines", "mhra", "tga-cmi"],
                        help="List of database IDs to search")
    parser.add_argument("--max-results", type=int, default=10, help="Maximum number of results per database")
    parser.add_argument("--min-date", help="Minimum date in format YYYY-MM-DD")
    parser.add_argument("--max-date", help="Maximum date in format YYYY-MM-DD")
    parser.add_argument("--parallel", action="store_true", help="Search databases in parallel")
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum number of parallel workers")
    parser.add_argument("--captcha-api-key", default="", help="API key for CAPTCHA solving service")
    parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()

    # Set default dates if not provided
    if not args.min_date:
        today = datetime.now()
        args.min_date = (today.replace(year=today.year - 1)).strftime("%Y-%m-%d")

    if not args.max_date:
        args.max_date = datetime.now().strftime("%Y-%m-%d")

    # Set default output file if not provided
    if not args.output:
        args.output = f"results_{int(time.time())}.json"

    # Search databases
    results = batch_search(
        args.query,
        args.databases,
        args.max_results,
        args.min_date,
        args.max_date,
        args.parallel,
        args.max_workers,
        args.captcha_api_key
    )

    # Save results to file
    save_results_to_file(results, args.output)
