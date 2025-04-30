"""
Test database connections
"""

import os
import sys
import json
import argparse
import logging
import time
from typing import List, Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_databases")

def test_database(database_id: str, query: str = "methotrexate") -> Dict[str, Any]:
    """
    Test a database connection
    
    Args:
        database_id (str): Database ID to test
        query (str): Query to search for
        
    Returns:
        Dict[str, Any]: Test results
    """
    logger.info(f"Testing database: {database_id}")
    
    # Import the smart access manager
    try:
        from scraping.smart_access_manager import SmartAccessManager
        manager = SmartAccessManager()
    except ImportError:
        logger.error("Failed to import SmartAccessManager")
        return {
            "database_id": database_id,
            "status": "error",
            "error": "Failed to import SmartAccessManager",
            "results": []
        }
    
    # Test the database
    try:
        # Start the timer
        start_time = time.time()
        
        # Search the database
        results = manager.search_database(database_id, query, max_results=5)
        
        # Calculate the elapsed time
        elapsed_time = time.time() - start_time
        
        # Return the results
        return {
            "database_id": database_id,
            "status": "success" if results else "no_results",
            "results_count": len(results),
            "elapsed_time": elapsed_time,
            "results": results
        }
    except Exception as e:
        logger.error(f"Error testing database {database_id}: {e}")
        return {
            "database_id": database_id,
            "status": "error",
            "error": str(e),
            "results": []
        }

def test_all_databases(query: str = "methotrexate", limit: int = 0) -> List[Dict[str, Any]]:
    """
    Test all databases
    
    Args:
        query (str): Query to search for
        limit (int): Maximum number of databases to test (0 = no limit)
        
    Returns:
        List[Dict[str, Any]]: Test results
    """
    # Import the database list
    try:
        from scraping.config import DATABASE_IDS
        databases = DATABASE_IDS
    except ImportError:
        try:
            # Try to get the database list from the smart access manager
            from scraping.smart_access_manager import SmartAccessManager
            manager = SmartAccessManager()
            databases = manager.get_database_ids()
        except ImportError:
            logger.error("Failed to import database list")
            return []
    
    # Limit the number of databases to test
    if limit > 0 and limit < len(databases):
        databases = databases[:limit]
    
    # Test each database
    results = []
    for database_id in databases:
        result = test_database(database_id, query)
        results.append(result)
        
        # Print the result
        if result["status"] == "success":
            logger.info(f"Database {database_id}: {result['results_count']} results in {result['elapsed_time']:.2f} seconds")
        elif result["status"] == "no_results":
            logger.info(f"Database {database_id}: No results")
        else:
            logger.error(f"Database {database_id}: Error - {result.get('error', 'Unknown error')}")
    
    return results

def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(description="Test database connections")
    parser.add_argument("--query", default="methotrexate", help="Query to search for")
    parser.add_argument("--database", help="Specific database ID to test")
    parser.add_argument("--limit", type=int, default=0, help="Maximum number of databases to test (0 = no limit)")
    parser.add_argument("--output", help="Output file for test results (JSON)")
    args = parser.parse_args()
    
    # Test databases
    if args.database:
        # Test a specific database
        results = [test_database(args.database, args.query)]
    else:
        # Test all databases
        results = test_all_databases(args.query, args.limit)
    
    # Calculate statistics
    total = len(results)
    success = sum(1 for r in results if r["status"] == "success")
    no_results = sum(1 for r in results if r["status"] == "no_results")
    errors = sum(1 for r in results if r["status"] == "error")
    
    # Print statistics
    print(f"\nTest Results:")
    print(f"Total databases tested: {total}")
    print(f"Successful: {success} ({success/total*100:.1f}%)")
    print(f"No results: {no_results} ({no_results/total*100:.1f}%)")
    print(f"Errors: {errors} ({errors/total*100:.1f}%)")
    
    # Save results to file if requested
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {args.output}")

if __name__ == "__main__":
    main()
