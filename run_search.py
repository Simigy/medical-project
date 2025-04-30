"""
Run a search with all the improvements
"""

import os
import sys
import json
import argparse
import logging
import time
import subprocess
from typing import List, Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("run_search")

def run_search(query: str, databases: List[str], output_file: str, 
               max_results: int = 10, min_date: str = None, max_date: str = None,
               use_captcha: bool = True, use_browser: bool = True, parallel: bool = True) -> str:
    """
    Run a search with all the improvements
    
    Args:
        query (str): Query to search for
        databases (List[str]): List of database IDs to search
        output_file (str): Output file for search results (JSON)
        max_results (int): Maximum number of results per database
        min_date (str): Minimum date (YYYY-MM-DD)
        max_date (str): Maximum date (YYYY-MM-DD)
        use_captcha (bool): Whether to use CAPTCHA solver
        use_browser (bool): Whether to use browser automation
        parallel (bool): Whether to run searches in parallel
        
    Returns:
        str: Path to the output file
    """
    # Build the command
    cmd = [
        "python",
        os.path.join("scraping", "smart_access_manager.py"),
        "--query", query,
        "--output", output_file,
        "--max-results", str(max_results)
    ]
    
    # Add databases
    cmd.append("--databases")
    cmd.extend(databases)
    
    # Add date range
    if min_date:
        cmd.extend(["--min-date", min_date])
    if max_date:
        cmd.extend(["--max-date", max_date])
    
    # Add options
    if parallel:
        cmd.append("--parallel")
    if not use_captcha:
        cmd.append("--no-captcha-solver")
    if not use_browser:
        cmd.append("--no-browser-automation")
    
    # Run the command
    logger.info(f"Running command: {' '.join(cmd)}")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Print output in real-time
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    
    # Get the return code
    return_code = process.wait()
    
    # Check if the search was successful
    if return_code != 0:
        logger.error(f"Search failed with return code {return_code}")
        stderr = process.stderr.read()
        logger.error(f"Error: {stderr}")
        return None
    
    # Check if the output file exists
    if not os.path.exists(output_file):
        logger.error(f"Output file {output_file} not found")
        return None
    
    # Return the output file path
    return output_file

def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(description="Run a search with all the improvements")
    parser.add_argument("--query", required=True, help="Query to search for")
    parser.add_argument("--databases", nargs="+", default=["pubmed", "fda-drugs", "ema-medicines", "nejm", "amjmed"],
                        help="List of database IDs to search")
    parser.add_argument("--output", help="Output file for search results (JSON)")
    parser.add_argument("--max-results", type=int, default=10, help="Maximum number of results per database")
    parser.add_argument("--min-date", help="Minimum date (YYYY-MM-DD)")
    parser.add_argument("--max-date", help="Maximum date (YYYY-MM-DD)")
    parser.add_argument("--no-captcha", action="store_true", help="Disable CAPTCHA solver")
    parser.add_argument("--no-browser", action="store_true", help="Disable browser automation")
    parser.add_argument("--no-parallel", action="store_true", help="Disable parallel searches")
    args = parser.parse_args()
    
    # Generate output file name if not provided
    if not args.output:
        timestamp = int(time.time() * 1000)
        args.output = f"search_results_{timestamp}.json"
    
    # Run the search
    output_file = run_search(
        query=args.query,
        databases=args.databases,
        output_file=args.output,
        max_results=args.max_results,
        min_date=args.min_date,
        max_date=args.max_date,
        use_captcha=not args.no_captcha,
        use_browser=not args.no_browser,
        parallel=not args.no_parallel
    )
    
    # Check if the search was successful
    if not output_file:
        logger.error("Search failed")
        return
    
    # Load and display the results
    try:
        with open(output_file, "r") as f:
            results = json.load(f)
        
        # Group results by database
        results_by_db = {}
        for result in results:
            db_id = result.get("database", "unknown")
            if db_id not in results_by_db:
                results_by_db[db_id] = []
            results_by_db[db_id].append(result)
        
        # Print statistics
        print(f"\nSearch Results:")
        print(f"Total results: {len(results)}")
        for db_id, db_results in results_by_db.items():
            print(f"  {db_id}: {len(db_results)} results")
        
        print(f"\nResults saved to {output_file}")
    except Exception as e:
        logger.error(f"Error loading results: {e}")

if __name__ == "__main__":
    main()
