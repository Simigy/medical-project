"""
Smart Data Access Manager

This module provides a smart manager that chooses the best method to access
each medical database based on availability, reliability, and configuration.

It integrates:
1. Official APIs
2. Browser automation with human-like behavior
3. CAPTCHA solving
4. Commercial data providers
5. Traditional web scraping
"""

import time
import logging
import os
import sys
import json
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("smart_access_manager")

# Try to import configuration
try:
    from config import (
        get_database_config, get_access_methods, get_api_key,
        get_rate_limit, get_browser_config, get_captcha_config
    )
except ImportError:
    try:
        # Try to import from the current directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir not in sys.path:
            sys.path.append(script_dir)
        from config import (
            get_database_config, get_access_methods, get_api_key,
            get_rate_limit, get_browser_config, get_captcha_config
        )
    except ImportError:
        logger.error("Could not import configuration. Make sure config.py is in the same directory.")
        sys.exit(1)

# Try to import API modules
API_MODULES = {}

# PubMed API
try:
    from pubmed_api import search_pubmed, search_pubmed_with_browser
    API_MODULES["pubmed"] = {
        "api": search_pubmed,
        "browser": search_pubmed_with_browser
    }
except ImportError:
    logger.warning("PubMed API module not found")

# FDA API
try:
    from fda_api import search_fda_drugs
    API_MODULES["fda-drugs"] = {
        "api": search_fda_drugs
    }
except ImportError:
    logger.warning("FDA API module not found")

# EMA API
try:
    from ema_api import search_ema_medicines
    API_MODULES["ema-medicines"] = {
        "api": search_ema_medicines
    }
except ImportError:
    logger.warning("EMA API module not found")

# MHRA API
try:
    from mhra_api import search_mhra_medicines
    API_MODULES["mhra"] = {
        "api": search_mhra_medicines
    }
except ImportError:
    logger.warning("MHRA API module not found")

# TGA API
try:
    from tga_api import search_tga_medicines, search_tga_with_selenium, search_tga_with_browser_automation
    API_MODULES["tga-cmi"] = {
        "browser": search_tga_medicines,
        "selenium": search_tga_with_selenium,
        "browser_automation": search_tga_with_browser_automation
    }
    API_MODULES["tga"] = API_MODULES["tga-cmi"]
except ImportError:
    logger.warning("TGA API module not found")

# Commercial data providers
try:
    from commercial_providers import search_drugbank, search_rxnav, search_chembl
    API_MODULES["drugbank"] = {
        "api": search_drugbank
    }
    API_MODULES["rxnav"] = {
        "api": search_rxnav
    }
    API_MODULES["chembl"] = {
        "api": search_chembl
    }
except ImportError:
    logger.warning("Commercial data providers module not found")

# Try to import browser automation
try:
    from browser_automation import BrowserAutomationManager
    BROWSER_AUTOMATION_AVAILABLE = True
except ImportError:
    logger.warning("Browser automation module not found")
    BROWSER_AUTOMATION_AVAILABLE = False

# Try to import CAPTCHA solver
try:
    from captcha_solver import CaptchaSolver
    CAPTCHA_SOLVER_AVAILABLE = True
except ImportError:
    logger.warning("CAPTCHA solver module not found")
    CAPTCHA_SOLVER_AVAILABLE = False

class SmartAccessManager:
    """
    Smart manager for accessing medical databases

    This class intelligently chooses the best method to access each database
    based on availability, reliability, and configuration.
    """

    def __init__(self, captcha_api_key: str = "", use_captcha_solver: bool = True,
                use_browser_automation: bool = True):
        """
        Initialize the smart access manager

        Args:
            captcha_api_key (str): API key for CAPTCHA solving service
            use_captcha_solver (bool): Whether to use CAPTCHA solver
            use_browser_automation (bool): Whether to use browser automation
        """
        self.captcha_api_key = captcha_api_key
        self.use_captcha_solver = use_captcha_solver
        self.use_browser_automation = use_browser_automation

        # Initialize browser automation manager if available and enabled
        self.browser_manager = None
        if BROWSER_AUTOMATION_AVAILABLE and self.use_browser_automation:
            self.browser_manager = BrowserAutomationManager(captcha_api_key=captcha_api_key)

        # Initialize CAPTCHA solver if available and enabled
        self.captcha_solver = None
        if CAPTCHA_SOLVER_AVAILABLE and self.use_captcha_solver:
            captcha_config = get_captcha_config()
            self.captcha_solver = CaptchaSolver(
                api_key=captcha_api_key or captcha_config.get("api_key", ""),
                service=captcha_config.get("service", "2captcha")
            )

        # Track success rates for different methods
        self.success_rates = self._load_success_rates()

    def search_database(self, db_id: str, query: str, max_results: int = 10,
                       min_date: Optional[str] = None, max_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search a database using the best available method

        Args:
            db_id (str): Database ID
            query (str): Search query
            max_results (int): Maximum number of results to return
            min_date (Optional[str]): Minimum date in format YYYY-MM-DD
            max_date (Optional[str]): Maximum date in format YYYY-MM-DD

        Returns:
            List[Dict[str, Any]]: List of search results
        """
        logger.info(f"Searching {db_id} for: {query}")

        # Get available access methods for this database
        methods = get_access_methods(db_id)

        # Sort methods by success rate
        sorted_methods = self._sort_methods_by_success_rate(db_id, methods)

        # Try each method in order until one succeeds
        results = []
        for method in sorted_methods:
            logger.info(f"  Trying {method} method for {db_id}")

            try:
                # Get the appropriate function for this method
                if db_id in API_MODULES and method in API_MODULES[db_id]:
                    func = API_MODULES[db_id][method]

                    # Call the function with appropriate parameters
                    if method == "api":
                        results = func(query, max_results, min_date, max_date)
                    elif method in ["browser", "selenium"]:
                        results = func(query, max_results, min_date, max_date, self.captcha_api_key)
                    elif method == "browser_automation":
                        results = func(query, max_results, min_date, max_date, self.captcha_api_key)

                    # If we got results, update success rate and return
                    if results:
                        self._update_success_rate(db_id, method, True)
                        logger.info(f"  {method} method succeeded for {db_id}, found {len(results)} results")
                        # Sort results by relevance score
                        sorted_results = self._sort_results(results)
                        return sorted_results
                    else:
                        self._update_success_rate(db_id, method, False)
                        logger.info(f"  {method} method returned no results for {db_id}")
                else:
                    logger.warning(f"  No {method} method available for {db_id}")

            except Exception as e:
                self._update_success_rate(db_id, method, False)
                logger.error(f"  Error using {method} method for {db_id}: {str(e)}")

        # If all methods failed, return empty list
        logger.error(f"  All methods failed for {db_id}")
        return []

    def batch_search(self, query: str, database_ids: List[str], max_results: int = 10,
                    min_date: Optional[str] = None, max_date: Optional[str] = None,
                    parallel: bool = False, max_workers: int = 4) -> List[Dict[str, Any]]:
        """
        Search multiple databases

        Args:
            query (str): Search query
            database_ids (List[str]): List of database IDs to search
            max_results (int): Maximum number of results per database
            min_date (Optional[str]): Minimum date in format YYYY-MM-DD
            max_date (Optional[str]): Maximum date in format YYYY-MM-DD
            parallel (bool): Whether to search databases in parallel
            max_workers (int): Maximum number of parallel workers

        Returns:
            List[Dict[str, Any]]: Combined list of search results
        """
        all_results = []

        if parallel and len(database_ids) > 1:
            import concurrent.futures

            logger.info(f"Searching {len(database_ids)} databases in parallel with {max_workers} workers...")
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_db = {
                    executor.submit(
                        self.search_database,
                        db_id,
                        query,
                        max_results,
                        min_date,
                        max_date
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
                    results = self.search_database(db_id, query, max_results, min_date, max_date)
                    all_results.extend(results)
                    logger.info(f"  Completed search for {db_id}, found {len(results)} results")
                except Exception as e:
                    logger.error(f"  Error searching {db_id}: {str(e)}")

        logger.info(f"Total results found: {len(all_results)}")

        # Sort results by relevance score
        sorted_results = self._sort_results(all_results)

        return sorted_results

    def close(self):
        """
        Close all resources
        """
        # Close browser automation manager
        if self.browser_manager:
            self.browser_manager.close_all_browsers()

        # Save success rates
        self._save_success_rates()

    def _sort_methods_by_success_rate(self, db_id: str, methods: List[str]) -> List[str]:
        """
        Sort access methods by success rate

        Args:
            db_id (str): Database ID
            methods (List[str]): List of access methods

        Returns:
            List[str]: Sorted list of access methods
        """
        # Get success rates for this database
        db_rates = self.success_rates.get(db_id, {})

        # Sort methods by success rate (higher first)
        # Use the 'rate' value from the stats dictionary, or default to 0.5
        return sorted(methods, key=lambda m: db_rates.get(m, {}).get('rate', 0.5) if isinstance(db_rates.get(m), dict) else 0.5, reverse=True)

    def _update_success_rate(self, db_id: str, method: str, success: bool):
        """
        Update success rate for a method

        Args:
            db_id (str): Database ID
            method (str): Access method
            success (bool): Whether the method succeeded
        """
        # Initialize database if not exists
        if db_id not in self.success_rates:
            self.success_rates[db_id] = {}

        # Initialize method if not exists
        if method not in self.success_rates[db_id]:
            self.success_rates[db_id][method] = {
                "success": 0,
                "total": 0,
                "rate": 0.5  # Start with neutral rate
            }

        # Update counts
        stats = self.success_rates[db_id][method]
        if success:
            stats["success"] += 1
        stats["total"] += 1

        # Update rate
        stats["rate"] = stats["success"] / stats["total"]

    def _load_success_rates(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """
        Load success rates from file

        Returns:
            Dict[str, Dict[str, Dict[str, float]]]: Success rates
        """
        try:
            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "success_rates.json")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading success rates: {str(e)}")

        return {}

    def _save_success_rates(self):
        """
        Save success rates to file
        """
        try:
            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "success_rates.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.success_rates, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving success rates: {str(e)}")

    def _sort_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort results by relevance score

        Args:
            results (List[Dict[str, Any]]): List of search results

        Returns:
            List[Dict[str, Any]]: Sorted list of search results
        """
        # Ensure all results have a numeric relevanceScore
        for result in results:
            if "relevanceScore" not in result or not isinstance(result["relevanceScore"], (int, float)):
                result["relevanceScore"] = 0.5

        return sorted(results, key=lambda r: r.get("relevanceScore", 0), reverse=True)

def search_database(db_id: str, query: str, max_results: int = 10,
                   min_date: Optional[str] = None, max_date: Optional[str] = None,
                   captcha_api_key: str = "", use_captcha_solver: bool = True,
                   use_browser_automation: bool = True) -> List[Dict[str, Any]]:
    """
    Search a database using the smart access manager

    Args:
        db_id (str): Database ID
        query (str): Search query
        max_results (int): Maximum number of results to return
        min_date (Optional[str]): Minimum date in format YYYY-MM-DD
        max_date (Optional[str]): Maximum date in format YYYY-MM-DD
        captcha_api_key (str): API key for CAPTCHA solving service
        use_captcha_solver (bool): Whether to use CAPTCHA solver
        use_browser_automation (bool): Whether to use browser automation

    Returns:
        List[Dict[str, Any]]: List of search results
    """
    manager = SmartAccessManager(
        captcha_api_key=captcha_api_key,
        use_captcha_solver=use_captcha_solver,
        use_browser_automation=use_browser_automation
    )
    try:
        return manager.search_database(db_id, query, max_results, min_date, max_date)
    finally:
        manager.close()

def batch_search(query: str, database_ids: List[str], max_results: int = 10,
                min_date: Optional[str] = None, max_date: Optional[str] = None,
                parallel: bool = False, max_workers: int = 4,
                captcha_api_key: str = "", use_captcha_solver: bool = True,
                use_browser_automation: bool = True) -> List[Dict[str, Any]]:
    """
    Search multiple databases using the smart access manager

    Args:
        query (str): Search query
        database_ids (List[str]): List of database IDs to search
        max_results (int): Maximum number of results per database
        min_date (Optional[str]): Minimum date in format YYYY-MM-DD
        max_date (Optional[str]): Maximum date in format YYYY-MM-DD
        parallel (bool): Whether to search databases in parallel
        max_workers (int): Maximum number of parallel workers
        captcha_api_key (str): API key for CAPTCHA solving service
        use_captcha_solver (bool): Whether to use CAPTCHA solver
        use_browser_automation (bool): Whether to use browser automation

    Returns:
        List[Dict[str, Any]]: Combined list of search results
    """
    manager = SmartAccessManager(
        captcha_api_key=captcha_api_key,
        use_captcha_solver=use_captcha_solver,
        use_browser_automation=use_browser_automation
    )
    try:
        return manager.batch_search(
            query, database_ids, max_results, min_date, max_date, parallel, max_workers
        )
    finally:
        manager.close()

def save_results_to_file(results: List[Dict[str, Any]], output_file: str) -> bool:
    """
    Save search results to a JSON file

    Args:
        results (List[Dict[str, Any]]): List of search results
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

        logger.info(f"Results saved to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving results: {str(e)}")
        return False

def get_available_databases() -> List[str]:
    """
    Get a list of all available databases

    Returns:
        List[str]: List of database IDs
    """
    # Combine databases from API modules and configuration
    databases = set(API_MODULES.keys())

    # Add databases from configuration
    try:
        from config import DATABASE_CONFIGS
        databases.update(DATABASE_CONFIGS.keys())
    except (ImportError, AttributeError):
        pass

    return sorted(list(databases))

# Example usage
if __name__ == "__main__":
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Search medical databases using smart access manager")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--databases", nargs="+", help="List of database IDs to search")
    parser.add_argument("--max-results", type=int, default=10, help="Maximum number of results per database")
    parser.add_argument("--min-date", help="Minimum date in format YYYY-MM-DD")
    parser.add_argument("--max-date", help="Maximum date in format YYYY-MM-DD")
    parser.add_argument("--parallel", action="store_true", help="Search databases in parallel")
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum number of parallel workers")
    parser.add_argument("--captcha-api-key", default="", help="API key for CAPTCHA solving service")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--list-databases", action="store_true", help="List all available databases")
    parser.add_argument("--include-commercial", action="store_true", help="Include commercial databases")
    parser.add_argument("--no-captcha-solver", action="store_true", help="Disable CAPTCHA solver")
    parser.add_argument("--no-browser-automation", action="store_true", help="Disable browser automation")

    args = parser.parse_args()

    # List databases if requested
    if args.list_databases:
        databases = get_available_databases()
        print("Available databases:")
        for db in databases:
            print(f"  - {db}")
        sys.exit(0)

    # Set default databases if not provided
    if not args.databases:
        # Start with public databases
        args.databases = ["pubmed", "fda-drugs", "ema-medicines", "mhra", "tga-cmi"]

        # Add commercial databases if requested
        if args.include_commercial:
            args.databases.extend(["drugbank", "rxnav", "chembl"])

    # Set default output file if not provided
    if not args.output:
        args.output = f"results_{int(time.time())}.json"

    # Create a configuration dictionary for the search
    search_config = {
        "use_captcha_solver": not args.no_captcha_solver,
        "use_browser_automation": not args.no_browser_automation
    }

    # Log the search configuration
    logger.info(f"Search configuration:")
    logger.info(f"  Query: {args.query}")
    logger.info(f"  Databases: {', '.join(args.databases)}")
    logger.info(f"  Max Results: {args.max_results}")
    logger.info(f"  Date Range: {args.min_date or 'None'} to {args.max_date or 'None'}")
    logger.info(f"  Parallel: {args.parallel}")
    logger.info(f"  CAPTCHA Solver: {'Disabled' if args.no_captcha_solver else 'Enabled'}")
    logger.info(f"  Browser Automation: {'Disabled' if args.no_browser_automation else 'Enabled'}")

    # Search databases
    results = batch_search(
        args.query,
        args.databases,
        args.max_results,
        args.min_date,
        args.max_date,
        args.parallel,
        args.max_workers,
        args.captcha_api_key,
        not args.no_captcha_solver,
        not args.no_browser_automation
    )

    # Save results to file
    save_results_to_file(results, args.output)
