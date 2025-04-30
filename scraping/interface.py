"""
Medical Database Search Interface

This module provides a command-line interface for searching medical databases
using various methods, including APIs, browser automation, and CAPTCHA solving.
"""

import os
import sys
import time
import json
import argparse
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("interface")

# Try to import smart access manager
try:
    from smart_access_manager import (
        batch_search, search_database, save_results_to_file, get_available_databases
    )
    SMART_ACCESS_AVAILABLE = True
except ImportError:
    try:
        # Try to import from the current directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir not in sys.path:
            sys.path.append(script_dir)
        from smart_access_manager import (
            batch_search, search_database, save_results_to_file, get_available_databases
        )
        SMART_ACCESS_AVAILABLE = True
    except ImportError:
        logger.error("Could not import smart access manager. Make sure smart_access_manager.py is in the same directory.")
        SMART_ACCESS_AVAILABLE = False

# Try to import configuration
try:
    from config import (
        get_database_config, get_access_methods, get_api_key,
        get_rate_limit, get_browser_config, get_captcha_config
    )
    CONFIG_AVAILABLE = True
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
        CONFIG_AVAILABLE = True
    except ImportError:
        logger.error("Could not import configuration. Make sure config.py is in the same directory.")
        CONFIG_AVAILABLE = False

def search_command(args):
    """
    Handle the search command
    
    Args:
        args: Command-line arguments
    """
    if not SMART_ACCESS_AVAILABLE:
        logger.error("Smart access manager is not available")
        return
    
    # Set default databases if not provided
    if not args.databases:
        args.databases = ["pubmed", "fda-drugs", "ema-medicines", "mhra", "tga-cmi"]
        
        # Add commercial databases if requested
        if args.include_commercial:
            args.databases.extend(["drugbank", "rxnav", "chembl"])
    
    # Set default output file if not provided
    if not args.output:
        args.output = f"results_{int(time.time())}.json"
    
    # Search databases
    logger.info(f"Searching for: {args.query}")
    logger.info(f"Databases: {', '.join(args.databases)}")
    
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
    
    # Print summary
    print(f"\nSearch Results Summary:")
    print(f"  Query: {args.query}")
    print(f"  Total results: {len(results)}")
    
    # Group results by source
    results_by_source = {}
    for result in results:
        source = result.get("source", "Unknown")
        if source not in results_by_source:
            results_by_source[source] = []
        results_by_source[source].append(result)
    
    # Print results by source
    for source, source_results in results_by_source.items():
        print(f"  {source}: {len(source_results)} results")
    
    print(f"\nResults saved to: {args.output}")

def list_databases_command(args):
    """
    Handle the list-databases command
    
    Args:
        args: Command-line arguments
    """
    if not SMART_ACCESS_AVAILABLE:
        logger.error("Smart access manager is not available")
        return
    
    databases = get_available_databases()
    
    print("\nAvailable Databases:")
    for db_id in databases:
        # Get database configuration
        if CONFIG_AVAILABLE:
            db_config = get_database_config(db_id)
            db_name = db_config.get("name", db_id)
            db_url = db_config.get("url", "")
            
            # Get access methods
            methods = get_access_methods(db_id)
            methods_str = ", ".join(methods)
            
            print(f"  - {db_id}: {db_name}")
            print(f"    URL: {db_url}")
            print(f"    Access Methods: {methods_str}")
        else:
            print(f"  - {db_id}")

def configure_command(args):
    """
    Handle the configure command
    
    Args:
        args: Command-line arguments
    """
    if not CONFIG_AVAILABLE:
        logger.error("Configuration module is not available")
        return
    
    # Load current configuration
    try:
        from config import load_config, save_config
        config = load_config()
    except (ImportError, AttributeError):
        logger.error("Could not load configuration")
        return
    
    # Update API keys
    if args.pubmed_api_key is not None:
        config["api_keys"]["pubmed"] = args.pubmed_api_key
    
    if args.fda_api_key is not None:
        config["api_keys"]["fda"] = args.fda_api_key
    
    if args.captcha_api_key is not None:
        config["api_keys"]["captcha"]["2captcha"] = args.captcha_api_key
    
    if args.drugbank_api_key is not None:
        config["api_keys"]["commercial"]["drugbank"] = args.drugbank_api_key
    
    if args.rxnav_api_key is not None:
        config["api_keys"]["commercial"]["rxnav"] = args.rxnav_api_key
    
    if args.chembl_api_key is not None:
        config["api_keys"]["commercial"]["chembl"] = args.chembl_api_key
    
    # Update browser configuration
    if args.headless is not None:
        config["browser"]["headless"] = args.headless
    
    # Save configuration
    try:
        save_config(config)
        print("Configuration updated successfully")
    except Exception as e:
        logger.error(f"Error saving configuration: {str(e)}")

def main():
    """
    Main entry point
    """
    # Create the main parser
    parser = argparse.ArgumentParser(description="Medical Database Search Interface")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search medical databases")
    search_parser.add_argument("--query", required=True, help="Search query")
    search_parser.add_argument("--databases", nargs="+", help="List of database IDs to search")
    search_parser.add_argument("--max-results", type=int, default=10, help="Maximum number of results per database")
    search_parser.add_argument("--min-date", help="Minimum date in format YYYY-MM-DD")
    search_parser.add_argument("--max-date", help="Maximum date in format YYYY-MM-DD")
    search_parser.add_argument("--parallel", action="store_true", help="Search databases in parallel")
    search_parser.add_argument("--max-workers", type=int, default=4, help="Maximum number of parallel workers")
    search_parser.add_argument("--captcha-api-key", default="", help="API key for CAPTCHA solving service")
    search_parser.add_argument("--output", help="Output file path")
    search_parser.add_argument("--include-commercial", action="store_true", help="Include commercial databases")
    
    # List databases command
    list_parser = subparsers.add_parser("list-databases", help="List all available databases")
    
    # Configure command
    config_parser = subparsers.add_parser("configure", help="Configure the application")
    config_parser.add_argument("--pubmed-api-key", help="PubMed API key")
    config_parser.add_argument("--fda-api-key", help="FDA API key")
    config_parser.add_argument("--captcha-api-key", help="CAPTCHA solving service API key")
    config_parser.add_argument("--drugbank-api-key", help="DrugBank API key")
    config_parser.add_argument("--rxnav-api-key", help="RxNav API key")
    config_parser.add_argument("--chembl-api-key", help="ChEMBL API key")
    config_parser.add_argument("--headless", type=bool, help="Run browser in headless mode")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle commands
    if args.command == "search":
        search_command(args)
    elif args.command == "list-databases":
        list_databases_command(args)
    elif args.command == "configure":
        configure_command(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
