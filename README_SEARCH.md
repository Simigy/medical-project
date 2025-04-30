# Medical Database Search

This document provides instructions on how to use the improved search functionality to fetch data from multiple medical databases.

## Setup

1. **Install Dependencies**

   Run the following command to install all the necessary dependencies:

   ```bash
   python install_selenium.py
   ```

   This will install:
   - Selenium and WebDriver Manager for browser automation
   - CAPTCHA solving libraries
   - Other required dependencies

2. **Set Up CAPTCHA Solver (Optional)**

   If you want to access websites that use CAPTCHAs, you'll need to set up a CAPTCHA solving service:

   ```bash
   python setup_captcha.py --api-key YOUR_API_KEY --service 2captcha
   ```

   Supported services:
   - 2captcha (recommended)
   - anticaptcha
   - capsolver
   - local (uses Tesseract OCR, less reliable)

   You can get an API key from:
   - [2Captcha](https://2captcha.com/)
   - [Anti-Captcha](https://anti-captcha.com/)
   - [CapSolver](https://capsolver.com/)

## Running a Search

### Using the Web Interface

1. Start the Next.js development server:

   ```bash
   npm run dev
   ```

2. Open your browser and navigate to http://localhost:3000

3. Use the search form to search for medications across multiple databases.

### Using the Command Line

You can also run searches directly from the command line:

```bash
python run_search.py --query "methotrexate" --databases pubmed fda-drugs ema-medicines nejm amjmed
```

Options:
- `--query`: The search query (required)
- `--databases`: List of database IDs to search (default: pubmed, fda-drugs, ema-medicines, nejm, amjmed)
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

Options:
- `--query`: The search query (default: methotrexate)
- `--database`: Specific database ID to test (if not provided, tests all databases)
- `--limit`: Maximum number of databases to test (0 = no limit)
- `--output`: Output file for test results (JSON)

## Supported Databases

The system supports over 140 databases, including:

- **PubMed**: Medical research articles
- **FDA Drugs**: US Food and Drug Administration drug database
- **EMA Medicines**: European Medicines Agency database
- **TGA**: Australian Therapeutic Goods Administration
- **MHRA**: UK Medicines and Healthcare products Regulatory Agency
- **Health Canada**: Canadian drug database
- **PMDA**: Japanese Pharmaceuticals and Medical Devices Agency
- **Medical Journals**: NEJM, JAMA, The Lancet, etc.

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

### Performance Issues

If searches are taking too long:

1. Reduce the number of databases:
   ```bash
   python run_search.py --query "methotrexate" --databases pubmed nejm
   ```

2. Reduce the maximum number of results:
   ```bash
   python run_search.py --query "methotrexate" --max-results 5
   ```

3. Disable parallel searches if they're causing issues:
   ```bash
   python run_search.py --query "methotrexate" --no-parallel
   ```
