#!/usr/bin/env python
"""
Simple test script to verify Python is working
"""

import os
import sys

print("Python version:", sys.version)
print("Current directory:", os.getcwd())
print("Files in current directory:", os.listdir("."))

# Try to import BeautifulSoup
try:
    from bs4 import BeautifulSoup
    print("BeautifulSoup is installed")
except ImportError:
    print("BeautifulSoup is not installed")

# Try to import Selenium
try:
    from selenium import webdriver
    print("Selenium is installed")
except ImportError:
    print("Selenium is not installed")

# Try to import requests
try:
    import requests
    print("Requests is installed")
except ImportError:
    print("Requests is not installed")

print("Test completed successfully!")
