@echo off
echo MedSearch Batch Scraper
echo =====================

set QUERY=
set LIMIT=0
set OUTPUT=scraping_results.json
set PARALLEL=1
set DATABASE_IDS=

:parse_args
if "%~1"=="" goto run
if /i "%~1"=="--query" (
    set QUERY=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--limit" (
    set LIMIT=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--output" (
    set OUTPUT=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--parallel" (
    set PARALLEL=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--database-ids" (
    set DATABASE_IDS=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--help" (
    echo Usage: run_batch_scraper.bat [options]
    echo.
    echo Options:
    echo   --query QUERY         Search query (required)
    echo   --limit LIMIT         Limit the number of databases to scrape (0 = all)
    echo   --output OUTPUT       Output file path (default: scraping_results.json)
    echo   --parallel PARALLEL   Number of parallel scraping processes (default: 1)
    echo   --database-ids IDS    Specific database IDs to scrape (space-separated list)
    echo   --help                Show this help message
    exit /b 0
)

shift
goto parse_args

:run
if "%QUERY%"=="" (
    echo Error: Query is required
    echo Run with --help for usage information
    exit /b 1
)

echo Query: %QUERY%
if %LIMIT% GTR 0 echo Limit: %LIMIT% databases
echo Output: %OUTPUT%
echo Parallel processes: %PARALLEL%
if not "%DATABASE_IDS%"=="" echo Database IDs: %DATABASE_IDS%

echo.
echo Starting scraper...
echo.

set COMMAND=python %~dp0batch_scraper.py --query "%QUERY%" --output "%OUTPUT%" --parallel %PARALLEL% --verbose

if %LIMIT% GTR 0 set COMMAND=%COMMAND% --limit %LIMIT%
if not "%DATABASE_IDS%"=="" set COMMAND=%COMMAND% --database-ids %DATABASE_IDS%

cd %~dp0
%COMMAND%

echo.
if %ERRORLEVEL% EQU 0 (
    echo Scraping completed successfully!
    echo Results saved to: %OUTPUT%
    echo.
    echo To view the results, open results_viewer.html in a web browser.
) else (
    echo Scraping failed with error code %ERRORLEVEL%
)

pause
