"""
Mock data for testing the batch scraper
"""

import json
import random
from datetime import datetime, timedelta

# Sample mock data for different databases
MOCK_DATA = {
    "tga-cmi": [
        {
            "title": "Paracetamol Consumer Medicine Information",
            "url": "https://www.tga.gov.au/products/consumer-medicines-information/paracetamol",
            "snippet": "Paracetamol Consumer Medicine Information. This leaflet contains important information about paracetamol. You should read it carefully before taking this medicine. Paracetamol is used to relieve pain and reduce fever.",
            "authors": []
        },
        {
            "title": "Panadol (Paracetamol)",
            "url": "https://www.tga.gov.au/products/consumer-medicines-information/panadol",
            "snippet": "Panadol contains the active ingredient paracetamol. It is used to relieve pain and reduce fever. It may be used for the relief of headaches, cold and flu symptoms, toothaches, and pain associated with arthritis.",
            "authors": ["GlaxoSmithKline"]
        },
        {
            "title": "Panamax (Paracetamol) Tablets",
            "url": "https://www.tga.gov.au/products/consumer-medicines-information/panamax",
            "snippet": "Panamax contains paracetamol which is used to relieve pain and fever. Panamax is available as tablets and is used for the temporary relief of pain and discomfort.",
            "authors": ["Sanofi-Aventis"]
        }
    ],
    "ema-medicines": [
        {
            "title": "Paracetamol 500mg Tablets",
            "url": "https://www.ema.europa.eu/en/medicines/human/paracetamol-500mg-tablets",
            "snippet": "Paracetamol 500mg Tablets are indicated for the treatment of mild to moderate pain including headache, migraine, toothache, sore throat and aches and pains associated with colds and flu.",
            "authors": ["European Medicines Agency"]
        },
        {
            "title": "Paracetamol/Ibuprofen Combination",
            "url": "https://www.ema.europa.eu/en/medicines/human/paracetamol-ibuprofen",
            "snippet": "This combination product contains paracetamol and ibuprofen. It is used for the temporary relief of pain associated with migraine, headache, backache, period pain, dental pain, rheumatic and muscular pain, pain of non-serious arthritis, cold and flu symptoms, sore throat and fever.",
            "authors": ["European Medicines Agency"]
        }
    ],
    "mhra": [
        {
            "title": "Paracetamol: updated advice on use during pregnancy",
            "url": "https://www.gov.uk/drug-safety-update/paracetamol-updated-advice-on-use-during-pregnancy",
            "snippet": "The MHRA has reviewed the available evidence on the use of paracetamol during pregnancy. While paracetamol remains the preferred painkiller for use during pregnancy, it should be used at the lowest effective dose for the shortest possible time.",
            "authors": ["Medicines and Healthcare products Regulatory Agency"]
        }
    ],
    "fda-drugs": [
        {
            "title": "FDA Drug Safety Communication: Prescription Acetaminophen Products",
            "url": "https://www.fda.gov/drugs/drug-safety-and-availability/fda-drug-safety-communication-prescription-acetaminophen-products",
            "snippet": "The U.S. Food and Drug Administration (FDA) is asking manufacturers of prescription combination drug products containing acetaminophen to limit the amount of acetaminophen to no more than 325 mg in each tablet or capsule to reduce the risk of liver injury.",
            "authors": ["U.S. Food and Drug Administration"]
        }
    ],
    "pubmed": [
        {
            "title": "Paracetamol: mechanisms and updates",
            "url": "https://pubmed.ncbi.nlm.nih.gov/12456789/",
            "snippet": "Paracetamol (acetaminophen) is one of the most commonly used analgesic and antipyretic medications worldwide. Despite its widespread use, the exact mechanisms of action remain incompletely understood.",
            "authors": ["Smith J", "Johnson A", "Williams B"]
        },
        {
            "title": "Safety profile of paracetamol use in children",
            "url": "https://pubmed.ncbi.nlm.nih.gov/23456789/",
            "snippet": "Paracetamol is widely used in pediatric populations for its analgesic and antipyretic properties. This systematic review evaluates the safety profile of paracetamol in children.",
            "authors": ["Brown R", "Davis M", "Wilson P", "Taylor S"]
        }
    ]
}

def get_mock_results(database_id, query):
    """
    Get mock results for a specific database and query
    
    Args:
        database_id (str): The database ID
        query (str): The search query
        
    Returns:
        list: A list of mock search results
    """
    # Check if we have mock data for this database
    if database_id in MOCK_DATA:
        results = MOCK_DATA[database_id]
        
        # Filter results based on query if provided
        if query:
            query_lower = query.lower()
            results = [r for r in results if query_lower in r["title"].lower() or query_lower in r["snippet"].lower()]
        
        # Add database-specific fields
        for i, result in enumerate(results):
            # Generate a random date within the last year
            random_days = random.randint(0, 365)
            date = (datetime.now() - timedelta(days=random_days)).strftime("%Y-%m-%d")
            
            result["id"] = f"{database_id}-{i}"
            result["source"] = database_id
            result["date"] = date
        
        return results
    
    # If no mock data exists, generate some generic results
    return [
        {
            "id": f"{database_id}-0",
            "title": f"Search Results for {query} in {database_id}",
            "url": f"https://example.com/{database_id}/search?q={query}",
            "source": database_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "snippet": f"This is a mock result for {query} in the {database_id} database. No actual data was retrieved.",
            "authors": ["Mock Data Generator"]
        },
        {
            "id": f"{database_id}-1",
            "title": f"Another Result for {query}",
            "url": f"https://example.com/{database_id}/results/{query.replace(' ', '-')}",
            "source": database_id,
            "date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            "snippet": f"This is another mock result for {query} in the {database_id} database. This demonstrates how multiple results would appear.",
            "authors": []
        }
    ]

def save_mock_results(output_file, database_ids, query):
    """
    Save mock results to a JSON file
    
    Args:
        output_file (str): The output file path
        database_ids (list): List of database IDs to include
        query (str): The search query
        
    Returns:
        list: The generated results
    """
    all_results = []
    
    for db_id in database_ids:
        results = get_mock_results(db_id, query)
        all_results.extend(results)
    
    # Save to file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
    
    return all_results
