"""
Example search script
"""

import json
from datetime import datetime

def main():
    """
    Main entry point
    """
    print("MedSearch - Example Search")
    print("-------------------------")
    
    # Search parameters
    query = "paracetamol"
    databases = ["pubmed", "fda-drugs", "ema-medicines", "mhra", "tga-cmi"]
    max_results = 5
    
    print(f"Searching for: {query}")
    print(f"Databases: {', '.join(databases)}")
    print(f"Max Results: {max_results}")
    
    # Create mock results
    results = []
    for db in databases:
        for i in range(3):  # Just 3 mock results per database
            results.append({
                "id": f"{db}-{i}",
                "title": f"Mock Result {i} for {db}",
                "url": f"https://example.com/{db}/{i}",
                "source": db.upper(),
                "date": "2023-01-01",
                "snippet": f"This is a mock result for {query} in {db}.",
                "authors": ["Author 1", "Author 2"]
            })
    
    # Print results summary
    print(f"\nFound {len(results)} results:")
    
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
    
    # Save results to file
    output_file = f"results_{int(datetime.now().timestamp())}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
