# MedSearch Batch Scraper

This tool allows you to fetch data from multiple medical databases at once. It uses the advanced scraping utilities from the MedSearch project.

## Prerequisites

Before using this tool, make sure you have the following installed:

- Python 3.7 or higher
- BeautifulSoup4 (`pip install beautifulsoup4`)
- Selenium (if you want to scrape JavaScript-heavy websites)
- Chrome WebDriver (if using Selenium)

## Usage

### Basic Usage

To scrape all databases with a specific query:

```bash
python scraping/batch_scraper.py --query "paracetamol"
```

This will:
1. Load the list of databases from `data/default-databases.ts`
2. Scrape each database for the query "paracetamol"
3. Save the results to `scraping_results.json`

### Advanced Usage

You can customize the scraping process with various options:

```bash
python scraping/batch_scraper.py --query "paracetamol" --limit 10 --output "results/paracetamol_results.json" --verbose --parallel 3
```

#### Available Options

- `--query`: The search query (required)
- `--output`: Output file path (default: `scraping_results.json`)
- `--limit`: Limit the number of databases to scrape (0 = all)
- `--max-retries`: Maximum number of retries per database (default: 3)
- `--timeout`: Timeout in seconds per database (default: 60)
- `--use-proxies`: Use proxy rotation
- `--solve-captchas`: Use CAPTCHA solver
- `--parallel`: Number of parallel scraping processes (use with caution)
- `--verbose`: Enable verbose output
- `--database-ids`: Specific database IDs to scrape (space-separated list)

### Examples

#### Scrape Specific Databases

```bash
python scraping/batch_scraper.py --query "aspirin" --database-ids fda-drugs ema-medicines mhra
```

#### Scrape with Proxies and CAPTCHA Solving

```bash
python scraping/batch_scraper.py --query "ibuprofen" --use-proxies --solve-captchas
```

#### Parallel Scraping (Faster but More Resource-Intensive)

```bash
python scraping/batch_scraper.py --query "metformin" --parallel 5
```

## Viewing Results

You can view the results using the included HTML viewer:

1. Open `scraping/results_viewer.html` in a web browser
2. If your results file is not named `scraping_results.json` or is not in the same directory, add a `file` parameter to the URL:
   ```
   file:///path/to/scraping/results_viewer.html?file=path/to/your/results.json
   ```

The viewer allows you to:
- Filter results by text
- Filter by source (database)
- Paginate through results
- View statistics about the results

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   
   If you see import errors, install the required packages:
   ```bash
   pip install beautifulsoup4 selenium requests
   ```

2. **Selenium Issues**
   
   If you're having issues with Selenium:
   - Make sure Chrome WebDriver is installed and in your PATH
   - Check that the WebDriver version matches your Chrome version

3. **Rate Limiting**
   
   If you're getting blocked by websites:
   - Reduce the number of parallel processes
   - Use the `--use-proxies` option
   - Increase the time between requests by modifying the rate limits in `scraping/config.py`

4. **CAPTCHA Issues**
   
   To solve CAPTCHAs automatically:
   - Get an API key from a CAPTCHA solving service like 2Captcha
   - Add your API key to `scraping/config.py`
   - Use the `--solve-captchas` option

## Customization

You can customize the scraping behavior for specific databases by modifying:

- `scraping/config.py`: Database-specific configurations
- The `create_search_url` function in `batch_scraper.py`: URL patterns for different databases

## Legal Considerations

Please be aware of and respect:
- Terms of service for each database
- Rate limiting policies
- Copyright and data usage restrictions

Always use this tool responsibly and ethically.
