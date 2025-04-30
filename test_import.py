import os
import sys

# Add the current directory to the path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

# Add the scraping directory to the path
scraping_dir = os.path.join(script_dir, "scraping")
if scraping_dir not in sys.path:
    sys.path.append(scraping_dir)

print(f"Script directory: {script_dir}")
print(f"Scraping directory: {scraping_dir}")
print(f"Current path: {sys.path}")

# Try to import our modules
try:
    import scraping.config
    print("Successfully imported config")
except ImportError as e:
    print(f"Failed to import config: {e}")

try:
    import scraping.interface
    print("Successfully imported interface")
except ImportError as e:
    print(f"Failed to import interface: {e}")

try:
    import scraping.smart_access_manager
    print("Successfully imported smart_access_manager")
except ImportError as e:
    print(f"Failed to import smart_access_manager: {e}")
