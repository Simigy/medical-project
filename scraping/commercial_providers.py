"""
Commercial Data Providers for Medical Information

This module provides access to commercial pharmaceutical data providers
that offer more reliable and comprehensive data through official APIs.

Supported providers:
1. DrugBank - Comprehensive drug information
2. RxNav - Drug interaction and terminology information
3. ChEMBL - Chemical compounds and bioactivity data
"""

import requests
import time
import json
import logging
import os
import sys
from datetime import datetime
from urllib.parse import quote_plus, urljoin

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("commercial_providers")

# Try to import configuration
try:
    from config import get_api_key, get_rate_limit, get_database_config
except ImportError:
    try:
        # Try to import from the current directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir not in sys.path:
            sys.path.append(script_dir)
        from config import get_api_key, get_rate_limit, get_database_config
    except ImportError:
        logger.error("Could not import configuration. Make sure config.py is in the same directory.")
        sys.exit(1)

class DrugBankAPI:
    """
    DrugBank API client
    
    DrugBank provides comprehensive drug information including:
    - Drug names and identifiers
    - Chemical structures
    - Mechanisms of action
    - Indications
    - Side effects
    - Drug interactions
    - Pharmacokinetics
    
    API Documentation: https://docs.drugbank.com/v1/
    """
    
    def __init__(self, api_key=None):
        """
        Initialize the DrugBank API client
        
        Args:
            api_key (str): DrugBank API key
        """
        self.api_key = api_key or get_api_key("drugbank")
        if not self.api_key:
            logger.warning("No DrugBank API key provided. API calls will fail.")
        
        self.base_url = "https://api.drugbank.com/v1/"
        self.rate_limit = get_rate_limit("drugbank")
        self.last_request_time = 0
    
    def search_drugs(self, query, max_results=10, retries=3):
        """
        Search for drugs in DrugBank
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            retries (int): Number of retries if the API call fails
            
        Returns:
            list: List of search results
        """
        logger.info(f"Searching DrugBank for: {query}")
        
        if not self.api_key:
            logger.error("DrugBank API key is required")
            return []
        
        # Build the search URL
        search_url = f"{self.base_url}drugs/search"
        
        # Set up the headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Set up the payload
        payload = {
            "query": query,
            "limit": max_results
        }
        
        # Make the search request with retries
        for attempt in range(retries):
            try:
                # Respect rate limits
                self._respect_rate_limit()
                
                logger.info(f"  API call attempt {attempt + 1}/{retries}")
                response = requests.post(search_url, headers=headers, json=payload)
                response.raise_for_status()
                search_results = response.json()
                
                # Extract the results
                if "results" not in search_results:
                    logger.info("  No results found")
                    return []
                
                drugs = search_results["results"]
                logger.info(f"  Found {len(drugs)} results")
                
                # Format the results
                results = []
                for drug in drugs:
                    try:
                        # Get drug details
                        drug_id = drug.get("id", "")
                        if drug_id:
                            drug_details = self.get_drug_details(drug_id)
                        else:
                            drug_details = {}
                        
                        # Create the result object
                        result = {
                            "id": f"drugbank-{drug.get('id', '')}",
                            "title": drug.get("name", ""),
                            "url": f"https://go.drugbank.com/drugs/{drug.get('id', '')}",
                            "source": "DrugBank",
                            "date": drug_details.get("updated", ""),
                            "snippet": drug_details.get("description", "")[:300] + "..." if len(drug_details.get("description", "")) > 300 else drug_details.get("description", ""),
                            "authors": [],
                            "additional_data": {
                                "cas_number": drug_details.get("cas_number", ""),
                                "atc_codes": drug_details.get("atc_codes", []),
                                "groups": drug_details.get("groups", []),
                                "categories": drug_details.get("categories", []),
                                "synonyms": drug_details.get("synonyms", [])
                            }
                        }
                        
                        results.append(result)
                    except Exception as e:
                        logger.error(f"  Error processing drug result: {str(e)}")
                        continue
                
                return results
                
            except Exception as e:
                logger.error(f"  Error in search attempt {attempt + 1}: {str(e)}")
                if attempt < retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"  Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("  All search attempts failed")
                    return []
    
    def get_drug_details(self, drug_id, retries=3):
        """
        Get details for a specific drug
        
        Args:
            drug_id (str): DrugBank drug ID
            retries (int): Number of retries if the API call fails
            
        Returns:
            dict: Drug details
        """
        logger.info(f"Getting details for drug: {drug_id}")
        
        if not self.api_key:
            logger.error("DrugBank API key is required")
            return {}
        
        # Build the URL
        url = f"{self.base_url}drugs/{drug_id}"
        
        # Set up the headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
        
        # Make the request with retries
        for attempt in range(retries):
            try:
                # Respect rate limits
                self._respect_rate_limit()
                
                logger.info(f"  API call attempt {attempt + 1}/{retries}")
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
                
            except Exception as e:
                logger.error(f"  Error in details attempt {attempt + 1}: {str(e)}")
                if attempt < retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"  Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("  All details attempts failed")
                    return {}
    
    def _respect_rate_limit(self):
        """
        Respect the rate limit by adding a delay if necessary
        """
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        # Calculate the minimum time between requests
        min_interval = 60.0 / self.rate_limit
        
        # If we need to wait, do so
        if elapsed < min_interval:
            wait_time = min_interval - elapsed
            time.sleep(wait_time)
        
        # Update the last request time
        self.last_request_time = time.time()

class RxNavAPI:
    """
    RxNav API client
    
    RxNav provides access to drug information from the National Library of Medicine:
    - RxNorm (drug names and codes)
    - RxClass (drug classes)
    - Interaction API (drug-drug interactions)
    - NDFRT (drug properties)
    
    API Documentation: https://lhncbc.nlm.nih.gov/RxNav/APIs/
    """
    
    def __init__(self, api_key=None):
        """
        Initialize the RxNav API client
        
        Args:
            api_key (str): RxNav API key (not required but recommended)
        """
        self.api_key = api_key or get_api_key("rxnav")
        self.base_url = "https://rxnav.nlm.nih.gov/REST/"
        self.rate_limit = get_rate_limit("rxnav")
        self.last_request_time = 0
    
    def search_drugs(self, query, max_results=10, retries=3):
        """
        Search for drugs in RxNav
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            retries (int): Number of retries if the API call fails
            
        Returns:
            list: List of search results
        """
        logger.info(f"Searching RxNav for: {query}")
        
        # Build the search URL
        search_url = f"{self.base_url}drugs"
        
        # Set up the parameters
        params = {
            "name": query
        }
        
        # Add API key if available
        if self.api_key:
            params["apiKey"] = self.api_key
        
        # Make the search request with retries
        for attempt in range(retries):
            try:
                # Respect rate limits
                self._respect_rate_limit()
                
                logger.info(f"  API call attempt {attempt + 1}/{retries}")
                response = requests.get(search_url, params=params)
                response.raise_for_status()
                
                # Parse the XML response
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                
                # Extract the drug concepts
                concepts = root.findall(".//conceptGroup/conceptProperties")
                
                logger.info(f"  Found {len(concepts)} results")
                
                # Format the results
                results = []
                for i, concept in enumerate(concepts):
                    if i >= max_results:
                        break
                    
                    try:
                        # Extract concept information
                        rxcui = concept.find("rxcui").text if concept.find("rxcui") is not None else ""
                        name = concept.find("name").text if concept.find("name") is not None else ""
                        synonym = concept.find("synonym").text if concept.find("synonym") is not None else ""
                        
                        # Get drug interactions
                        interactions = self.get_drug_interactions(rxcui)
                        
                        # Create the result object
                        result = {
                            "id": f"rxnav-{rxcui}",
                            "title": name,
                            "url": f"https://mor.nlm.nih.gov/RxNav/search?searchBy=RXCUI&searchTerm={rxcui}",
                            "source": "RxNav",
                            "date": "",  # RxNav doesn't provide dates
                            "snippet": f"RxCUI: {rxcui}. {synonym}" if synonym else f"RxCUI: {rxcui}",
                            "authors": [],
                            "additional_data": {
                                "rxcui": rxcui,
                                "interactions": interactions
                            }
                        }
                        
                        results.append(result)
                    except Exception as e:
                        logger.error(f"  Error processing drug result: {str(e)}")
                        continue
                
                return results
                
            except Exception as e:
                logger.error(f"  Error in search attempt {attempt + 1}: {str(e)}")
                if attempt < retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"  Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("  All search attempts failed")
                    return []
    
    def get_drug_interactions(self, rxcui, retries=3):
        """
        Get drug interactions for a specific RxCUI
        
        Args:
            rxcui (str): RxNorm Concept Unique Identifier
            retries (int): Number of retries if the API call fails
            
        Returns:
            list: List of drug interactions
        """
        logger.info(f"Getting interactions for drug: {rxcui}")
        
        # Build the URL
        url = f"{self.base_url}interaction/interaction.json"
        
        # Set up the parameters
        params = {
            "rxcui": rxcui
        }
        
        # Add API key if available
        if self.api_key:
            params["apiKey"] = self.api_key
        
        # Make the request with retries
        for attempt in range(retries):
            try:
                # Respect rate limits
                self._respect_rate_limit()
                
                logger.info(f"  API call attempt {attempt + 1}/{retries}")
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                # Parse the JSON response
                data = response.json()
                
                # Extract the interactions
                interactions = []
                
                if "interactionTypeGroup" in data:
                    for group in data["interactionTypeGroup"]:
                        if "interactionType" in group:
                            for interaction_type in group["interactionType"]:
                                if "interactionPair" in interaction_type:
                                    for pair in interaction_type["interactionPair"]:
                                        if "description" in pair:
                                            interactions.append(pair["description"])
                
                return interactions
                
            except Exception as e:
                logger.error(f"  Error in interactions attempt {attempt + 1}: {str(e)}")
                if attempt < retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"  Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("  All interactions attempts failed")
                    return []
    
    def _respect_rate_limit(self):
        """
        Respect the rate limit by adding a delay if necessary
        """
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        # Calculate the minimum time between requests
        min_interval = 60.0 / self.rate_limit
        
        # If we need to wait, do so
        if elapsed < min_interval:
            wait_time = min_interval - elapsed
            time.sleep(wait_time)
        
        # Update the last request time
        self.last_request_time = time.time()

class ChEMBLAPI:
    """
    ChEMBL API client
    
    ChEMBL provides access to bioactivity data for small molecules:
    - Chemical structures
    - Bioactivity data
    - Drug targets
    - ADMET properties
    
    API Documentation: https://chembl.gitbook.io/chembl-interface-documentation/web-services
    """
    
    def __init__(self, api_key=None):
        """
        Initialize the ChEMBL API client
        
        Args:
            api_key (str): ChEMBL API key (not required)
        """
        self.api_key = api_key or get_api_key("chembl")
        self.base_url = "https://www.ebi.ac.uk/chembl/api/data/"
        self.rate_limit = get_rate_limit("chembl")
        self.last_request_time = 0
    
    def search_compounds(self, query, max_results=10, retries=3):
        """
        Search for compounds in ChEMBL
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            retries (int): Number of retries if the API call fails
            
        Returns:
            list: List of search results
        """
        logger.info(f"Searching ChEMBL for: {query}")
        
        # Build the search URL
        search_url = f"{self.base_url}molecule/search"
        
        # Set up the parameters
        params = {
            "q": query,
            "limit": max_results,
            "format": "json"
        }
        
        # Make the search request with retries
        for attempt in range(retries):
            try:
                # Respect rate limits
                self._respect_rate_limit()
                
                logger.info(f"  API call attempt {attempt + 1}/{retries}")
                response = requests.get(search_url, params=params)
                response.raise_for_status()
                search_results = response.json()
                
                # Extract the molecules
                if "molecules" not in search_results:
                    logger.info("  No results found")
                    return []
                
                molecules = search_results["molecules"]
                logger.info(f"  Found {len(molecules)} results")
                
                # Format the results
                results = []
                for molecule in molecules:
                    try:
                        # Extract molecule information
                        chembl_id = molecule.get("molecule_chembl_id", "")
                        
                        # Get compound details
                        if chembl_id:
                            compound_details = self.get_compound_details(chembl_id)
                        else:
                            compound_details = {}
                        
                        # Create the result object
                        result = {
                            "id": f"chembl-{chembl_id}",
                            "title": molecule.get("pref_name", "") or f"ChEMBL: {chembl_id}",
                            "url": f"https://www.ebi.ac.uk/chembl/compound_report_card/{chembl_id}/",
                            "source": "ChEMBL",
                            "date": "",  # ChEMBL doesn't provide dates
                            "snippet": compound_details.get("description", "")[:300] + "..." if len(compound_details.get("description", "")) > 300 else compound_details.get("description", ""),
                            "authors": [],
                            "additional_data": {
                                "chembl_id": chembl_id,
                                "molecular_formula": molecule.get("molecule_properties", {}).get("full_molformula", ""),
                                "molecular_weight": molecule.get("molecule_properties", {}).get("full_mwt", ""),
                                "smiles": molecule.get("molecule_structures", {}).get("canonical_smiles", ""),
                                "inchi_key": molecule.get("molecule_structures", {}).get("standard_inchi_key", ""),
                                "targets": compound_details.get("targets", [])
                            }
                        }
                        
                        results.append(result)
                    except Exception as e:
                        logger.error(f"  Error processing compound result: {str(e)}")
                        continue
                
                return results
                
            except Exception as e:
                logger.error(f"  Error in search attempt {attempt + 1}: {str(e)}")
                if attempt < retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"  Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("  All search attempts failed")
                    return []
    
    def get_compound_details(self, chembl_id, retries=3):
        """
        Get details for a specific compound
        
        Args:
            chembl_id (str): ChEMBL compound ID
            retries (int): Number of retries if the API call fails
            
        Returns:
            dict: Compound details
        """
        logger.info(f"Getting details for compound: {chembl_id}")
        
        # Build the URL
        url = f"{self.base_url}molecule/{chembl_id}"
        
        # Set up the parameters
        params = {
            "format": "json"
        }
        
        # Make the request with retries
        for attempt in range(retries):
            try:
                # Respect rate limits
                self._respect_rate_limit()
                
                logger.info(f"  API call attempt {attempt + 1}/{retries}")
                response = requests.get(url, params=params)
                response.raise_for_status()
                molecule = response.json()
                
                # Get the compound's targets
                targets = self.get_compound_targets(chembl_id)
                
                # Create a description from the available data
                description = ""
                if "pref_name" in molecule and molecule["pref_name"]:
                    description += f"Name: {molecule['pref_name']}. "
                
                if "molecule_properties" in molecule:
                    props = molecule["molecule_properties"]
                    if "full_molformula" in props:
                        description += f"Formula: {props['full_molformula']}. "
                    if "full_mwt" in props:
                        description += f"Molecular Weight: {props['full_mwt']}. "
                    if "alogp" in props:
                        description += f"ALogP: {props['alogp']}. "
                
                if targets:
                    description += f"Targets: {', '.join([t.get('name', '') for t in targets[:3]])}."
                
                return {
                    "description": description,
                    "targets": targets
                }
                
            except Exception as e:
                logger.error(f"  Error in details attempt {attempt + 1}: {str(e)}")
                if attempt < retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"  Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("  All details attempts failed")
                    return {}
    
    def get_compound_targets(self, chembl_id, retries=3):
        """
        Get targets for a specific compound
        
        Args:
            chembl_id (str): ChEMBL compound ID
            retries (int): Number of retries if the API call fails
            
        Returns:
            list: List of targets
        """
        logger.info(f"Getting targets for compound: {chembl_id}")
        
        # Build the URL
        url = f"{self.base_url}mechanism"
        
        # Set up the parameters
        params = {
            "molecule_chembl_id": chembl_id,
            "format": "json"
        }
        
        # Make the request with retries
        for attempt in range(retries):
            try:
                # Respect rate limits
                self._respect_rate_limit()
                
                logger.info(f"  API call attempt {attempt + 1}/{retries}")
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Extract the targets
                if "mechanisms" not in data:
                    return []
                
                targets = []
                for mechanism in data["mechanisms"]:
                    target = {
                        "id": mechanism.get("target_chembl_id", ""),
                        "name": mechanism.get("target_name", ""),
                        "action": mechanism.get("action_type", ""),
                        "mechanism": mechanism.get("mechanism_of_action", "")
                    }
                    targets.append(target)
                
                return targets
                
            except Exception as e:
                logger.error(f"  Error in targets attempt {attempt + 1}: {str(e)}")
                if attempt < retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"  Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("  All targets attempts failed")
                    return []
    
    def _respect_rate_limit(self):
        """
        Respect the rate limit by adding a delay if necessary
        """
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        # Calculate the minimum time between requests
        min_interval = 60.0 / self.rate_limit
        
        # If we need to wait, do so
        if elapsed < min_interval:
            wait_time = min_interval - elapsed
            time.sleep(wait_time)
        
        # Update the last request time
        self.last_request_time = time.time()

def search_drugbank(query, max_results=10):
    """
    Search DrugBank for drug information
    
    Args:
        query (str): Search query
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of search results
    """
    api = DrugBankAPI()
    return api.search_drugs(query, max_results)

def search_rxnav(query, max_results=10):
    """
    Search RxNav for drug information
    
    Args:
        query (str): Search query
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of search results
    """
    api = RxNavAPI()
    return api.search_drugs(query, max_results)

def search_chembl(query, max_results=10):
    """
    Search ChEMBL for compound information
    
    Args:
        query (str): Search query
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of search results
    """
    api = ChEMBLAPI()
    return api.search_compounds(query, max_results)

# Example usage
if __name__ == "__main__":
    # Test DrugBank API
    print("Testing DrugBank API...")
    drugbank_results = search_drugbank("paracetamol", 3)
    print(f"Found {len(drugbank_results)} results from DrugBank")
    
    # Test RxNav API
    print("\nTesting RxNav API...")
    rxnav_results = search_rxnav("paracetamol", 3)
    print(f"Found {len(rxnav_results)} results from RxNav")
    
    # Test ChEMBL API
    print("\nTesting ChEMBL API...")
    chembl_results = search_chembl("paracetamol", 3)
    print(f"Found {len(chembl_results)} results from ChEMBL")
