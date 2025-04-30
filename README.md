# MedSearch

A comprehensive medical database search tool that allows users to search for medications across multiple medical databases.

## Features

- Search across 140+ medical databases including PubMed, FDA, EMA, and medical journals
- Real-time search results with streaming updates
- Advanced filtering options by date range
- Support for multiple active ingredients
- Browser automation with human-like behavior to avoid detection
- CAPTCHA solving capabilities
- Clean, modern user interface

## Getting Started

### Prerequisites

- Node.js (v16+)
- Python (v3.8+)
- npm or yarn

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/medsearch.git
   cd medsearch
   ```

2. Install JavaScript dependencies:
   ```bash
   npm install
   ```

3. Install Python dependencies:
   ```bash
   pip install -r scraping/requirements.txt
   ```

4. Install Selenium and related packages:
   ```bash
   pip install selenium webdriver-manager undetected-chromedriver 2captcha-python
   ```

### Running the Application

1. Start the development server:
   ```bash
   npm run dev
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:3000
   ```

## Using the Search Tool

1. Enter one or more active ingredients in the search form
2. Select the databases you want to search
3. Set a date range if needed
4. Click "Search" to start the search process
5. View real-time updates as results are found
6. Browse through the search results

## Command Line Usage

You can also run searches directly from the command line:

```bash
python run_search.py --query "methotrexate" --databases pubmed fda-drugs ema-medicines nejm amjmed
```

Options:
- `--query`: The search query (required)
- `--databases`: List of database IDs to search
- `--output`: Output file for search results (JSON)
- `--max-results`: Maximum number of results per database (default: 10)
- `--min-date`: Minimum date (YYYY-MM-DD)
- `--max-date`: Maximum date (YYYY-MM-DD)
- `--no-captcha`: Disable CAPTCHA solver
- `--no-browser`: Disable browser automation
- `--no-parallel`: Disable parallel searches

## Testing Database Connections

You can test the connections to various databases:

```bash
python test_databases.py --query "methotrexate" --limit 10
```

## CAPTCHA Solving

To use CAPTCHA solving services, set up your API key:

```bash
python setup_captcha.py --api-key YOUR_API_KEY --service 2captcha
```

Supported services:
- 2captcha (recommended)
- anticaptcha
- capsolver
- local (uses Tesseract OCR, less reliable)

## Project Structure

- `/app` - Next.js application files
- `/components` - React components
- `/public` - Static assets
- `/scraping` - Python scraping modules
  - `smart_access_manager.py` - Main search orchestration
  - `browser_automation.py` - Browser automation with human-like behavior
  - `captcha_solver.py` - CAPTCHA solving capabilities
  - Database-specific modules for each data source

## Troubleshooting

### Browser Automation Issues

If you encounter issues with browser automation:

1. Make sure Selenium is installed:
   ```bash
   pip install selenium webdriver-manager
   ```

2. Try running with the `--no-browser` option to disable browser automation:
   ```bash
   python run_search.py --query "methotrexate" --no-browser
   ```

### CAPTCHA Issues

If you encounter issues with CAPTCHA solving:

1. Make sure you have set up a CAPTCHA solving service:
   ```bash
   python setup_captcha.py --api-key YOUR_API_KEY --service 2captcha
   ```

2. Try running with the `--no-captcha` option to disable CAPTCHA solving:
   ```bash
   python run_search.py --query "methotrexate" --no-captcha
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all the medical databases that provide access to their data
- The Next.js team for their excellent framework
- The Selenium team for their browser automation tools
