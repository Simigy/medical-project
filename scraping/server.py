#!/usr/bin/env python
"""
Simple HTTP Server for MedSearch Results Viewer

This script starts a local HTTP server to serve the results viewer interface.
"""

import http.server
import socketserver
import os
import json
import argparse
from urllib.parse import urlparse, parse_qs

# Sample data to use if no results file exists
SAMPLE_DATA = [
  {
    "id": "tga-cmi-0",
    "title": "Paracetamol Consumer Medicine Information",
    "url": "https://www.tga.gov.au/products/consumer-medicines-information/paracetamol",
    "source": "TGA - Consumer Medicines Information",
    "date": "2023-05-15",
    "snippet": "Paracetamol Consumer Medicine Information. This leaflet contains important information about paracetamol. You should read it carefully before taking this medicine. Paracetamol is used to relieve pain and reduce fever.",
    "authors": []
  },
  {
    "id": "tga-cmi-1",
    "title": "Panadol (Paracetamol)",
    "url": "https://www.tga.gov.au/products/consumer-medicines-information/panadol",
    "source": "TGA - Consumer Medicines Information",
    "date": "2023-04-20",
    "snippet": "Panadol contains the active ingredient paracetamol. It is used to relieve pain and reduce fever. It may be used for the relief of headaches, cold and flu symptoms, toothaches, and pain associated with arthritis.",
    "authors": ["GlaxoSmithKline"]
  },
  {
    "id": "ema-medicines-0",
    "title": "Paracetamol 500mg Tablets",
    "url": "https://www.ema.europa.eu/en/medicines/human/paracetamol-500mg-tablets",
    "source": "EMA - Medicines",
    "date": "2023-06-10",
    "snippet": "Paracetamol 500mg Tablets are indicated for the treatment of mild to moderate pain including headache, migraine, toothache, sore throat and aches and pains associated with colds and flu. They are also used for the symptomatic relief of pain due to rheumatism, arthritis and muscular aches.",
    "authors": ["European Medicines Agency"]
  },
  {
    "id": "mhra-0",
    "title": "Paracetamol: updated advice on use during pregnancy",
    "url": "https://www.gov.uk/drug-safety-update/paracetamol-updated-advice-on-use-during-pregnancy",
    "source": "MHRA",
    "date": "2023-02-15",
    "snippet": "The MHRA has reviewed the available evidence on the use of paracetamol during pregnancy. While paracetamol remains the preferred painkiller for use during pregnancy, it should be used at the lowest effective dose for the shortest possible time.",
    "authors": ["Medicines and Healthcare products Regulatory Agency"]
  },
  {
    "id": "fda-drugs-0",
    "title": "FDA Drug Safety Communication: Prescription Acetaminophen Products",
    "url": "https://www.fda.gov/drugs/drug-safety-and-availability/fda-drug-safety-communication-prescription-acetaminophen-products",
    "source": "FDA - Drugs",
    "date": "2023-03-05",
    "snippet": "The U.S. Food and Drug Administration (FDA) is asking manufacturers of prescription combination drug products containing acetaminophen to limit the amount of acetaminophen to no more than 325 mg in each tablet or capsule to reduce the risk of liver injury.",
    "authors": ["U.S. Food and Drug Administration"]
  }
]

class MedSearchHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler for MedSearch"""
    
    def do_GET(self):
        """Handle GET requests"""
        # Parse the URL
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Handle requests for scraping_results.json
        if path == '/scraping_results.json':
            # Check if the file exists
            if os.path.exists('scraping_results.json'):
                # Serve the actual file
                return super().do_GET()
            else:
                # Serve sample data
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(SAMPLE_DATA).encode())
                return
        
        # For all other requests, use the default handler
        return super().do_GET()

def run_server(port=8000):
    """Run the HTTP server"""
    # Change to the directory containing this script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Create the server
    handler = MedSearchHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)
    
    print(f"Server running at http://localhost:{port}/")
    print(f"View the results at http://localhost:{port}/results_viewer.html")
    print("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a local HTTP server for MedSearch Results Viewer")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on (default: 8000)")
    args = parser.parse_args()
    
    run_server(args.port)
