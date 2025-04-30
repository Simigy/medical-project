#!/bin/bash

echo "MedSearch Batch Scraper"
echo "====================="

QUERY=""
LIMIT=0
OUTPUT="scraping_results.json"
PARALLEL=1
DATABASE_IDS=""
VERBOSE=""
USE_PROXIES=""
SOLVE_CAPTCHAS=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --query)
      QUERY="$2"
      shift 2
      ;;
    --limit)
      LIMIT="$2"
      shift 2
      ;;
    --output)
      OUTPUT="$2"
      shift 2
      ;;
    --parallel)
      PARALLEL="$2"
      shift 2
      ;;
    --database-ids)
      DATABASE_IDS="$2"
      shift 2
      ;;
    --verbose)
      VERBOSE="--verbose"
      shift
      ;;
    --use-proxies)
      USE_PROXIES="--use-proxies"
      shift
      ;;
    --solve-captchas)
      SOLVE_CAPTCHAS="--solve-captchas"
      shift
      ;;
    --help)
      echo "Usage: run_batch_scraper.sh [options]"
      echo ""
      echo "Options:"
      echo "  --query QUERY         Search query (required)"
      echo "  --limit LIMIT         Limit the number of databases to scrape (0 = all)"
      echo "  --output OUTPUT       Output file path (default: scraping_results.json)"
      echo "  --parallel PARALLEL   Number of parallel scraping processes (default: 1)"
      echo "  --database-ids IDS    Specific database IDs to scrape (space-separated list)"
      echo "  --verbose             Enable verbose output"
      echo "  --use-proxies         Use proxy rotation"
      echo "  --solve-captchas      Use CAPTCHA solver"
      echo "  --help                Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Run with --help for usage information"
      exit 1
      ;;
  esac
done

# Check if query is provided
if [ -z "$QUERY" ]; then
  echo "Error: Query is required"
  echo "Run with --help for usage information"
  exit 1
fi

echo "Query: $QUERY"
if [ $LIMIT -gt 0 ]; then
  echo "Limit: $LIMIT databases"
fi
echo "Output: $OUTPUT"
echo "Parallel processes: $PARALLEL"
if [ ! -z "$DATABASE_IDS" ]; then
  echo "Database IDs: $DATABASE_IDS"
fi
if [ ! -z "$USE_PROXIES" ]; then
  echo "Using proxy rotation"
fi
if [ ! -z "$SOLVE_CAPTCHAS" ]; then
  echo "Using CAPTCHA solver"
fi

echo ""
echo "Starting scraper..."
echo ""

# Build the command
COMMAND="python $(dirname \"$0\")/batch_scraper.py --query \"$QUERY\" --output \"$OUTPUT\" --parallel $PARALLEL $VERBOSE"

if [ $LIMIT -gt 0 ]; then
  COMMAND="$COMMAND --limit $LIMIT"
fi
if [ ! -z "$DATABASE_IDS" ]; then
  COMMAND="$COMMAND --database-ids $DATABASE_IDS"
fi
if [ ! -z "$USE_PROXIES" ]; then
  COMMAND="$COMMAND $USE_PROXIES"
fi
if [ ! -z "$SOLVE_CAPTCHAS" ]; then
  COMMAND="$COMMAND $SOLVE_CAPTCHAS"
fi

# Change to the script directory
cd "$(dirname "$0")"

# Run the command
eval $COMMAND

echo ""
if [ $? -eq 0 ]; then
  echo "Scraping completed successfully!"
  echo "Results saved to: $OUTPUT"
  echo ""
  echo "To view the results, open results_viewer.html in a web browser."
else
  echo "Scraping failed with error code $?"
fi

read -p "Press Enter to continue..."
