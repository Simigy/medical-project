"""
List available databases
"""

def main():
    """
    Main entry point
    """
    print("Available Databases:")
    print("-------------------")
    
    # Public databases
    print("\nPublic Databases:")
    print("  - pubmed: PubMed")
    print("    URL: https://pubmed.ncbi.nlm.nih.gov/")
    print("    Access Methods: api, browser, selenium")
    
    print("  - fda-drugs: FDA Drugs")
    print("    URL: https://www.accessdata.fda.gov/scripts/cder/daf/")
    print("    Access Methods: api, browser")
    
    print("  - ema-medicines: EMA Medicines")
    print("    URL: https://www.ema.europa.eu/en/medicines/")
    print("    Access Methods: api, browser, selenium")
    
    print("  - mhra: MHRA")
    print("    URL: https://products.mhra.gov.uk/")
    print("    Access Methods: api, browser, selenium")
    
    print("  - tga-cmi: TGA - Consumer Medicines Information")
    print("    URL: https://www.tga.gov.au/products/consumer-medicines-information/search")
    print("    Access Methods: browser, selenium")
    
    # Commercial databases
    print("\nCommercial Databases:")
    print("  - drugbank: DrugBank")
    print("    URL: https://go.drugbank.com/")
    print("    Access Methods: api")
    
    print("  - rxnav: RxNav")
    print("    URL: https://mor.nlm.nih.gov/RxNav/")
    print("    Access Methods: api")
    
    print("  - chembl: ChEMBL")
    print("    URL: https://www.ebi.ac.uk/chembl/")
    print("    Access Methods: api")

if __name__ == "__main__":
    main()
