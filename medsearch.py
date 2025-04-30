#!/usr/bin/env python3
"""
MedSearch - Medical Database Search Tool

This tool allows searching across multiple medical databases using various methods:
1. Official APIs
2. Browser automation with human-like behavior
3. CAPTCHA solving
4. Commercial data providers
5. Traditional web scraping

It intelligently chooses the best method for each database based on availability,
reliability, and configuration.
"""

import os
import sys
import argparse
import logging
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("medsearch")

# Add the scraping directory to the path
script_dir = os.path.dirname(os.path.abspath(__file__))
scraping_dir = os.path.join(script_dir, "scraping")
if scraping_dir not in sys.path:
    sys.path.append(scraping_dir)

# Try to import the interface
try:
    from scraping.interface import main as interface_main
    INTERFACE_AVAILABLE = True
except ImportError:
    logger.error("Could not import interface. Make sure scraping/interface.py is in the correct location.")
    INTERFACE_AVAILABLE = False

def main():
    """
    Main entry point
    """
    if INTERFACE_AVAILABLE:
        # Run the interface
        interface_main()
    else:
        print("Error: Interface not available. Please check the installation.")
        sys.exit(1)

if __name__ == "__main__":
    main()
