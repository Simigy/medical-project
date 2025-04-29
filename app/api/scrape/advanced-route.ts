import { NextResponse } from "next/server";
import type { SearchResult } from "@/types";
import { scrapeWithAdvancedTechniques, getDatabaseScrapingConfig, requiresAdvancedScraping } from "@/lib/scraping";

/**
 * Advanced scraping endpoint that uses the new scraping utilities
 * to handle restricted databases with techniques like proxy rotation,
 * CAPTCHA solving, authentication, rate limiting, and retries.
 */
export async function POST(request: Request) {
  try {
    // Parse the request body
    const body = await request.json();
    const { query, databaseId, url } = body;

    if (!query || !databaseId || !url) {
      return NextResponse.json(
        { error: "Missing required parameters: query, databaseId, and url are required" },
        { status: 400 }
      );
    }

    // Check if this database requires advanced scraping techniques
    if (!requiresAdvancedScraping(databaseId)) {
      return NextResponse.json(
        { error: "This database does not require advanced scraping techniques" },
        { status: 400 }
      );
    }

    // Get database-specific scraping configuration
    const scrapingConfig = getDatabaseScrapingConfig(databaseId);

    // Perform the advanced scraping
    console.log(`Performing advanced scraping for ${databaseId} with query: ${query}`);
    const results = await scrapeWithAdvancedTechniques(url, query, scrapingConfig);

    // Check if we got any results
    if (!results || results.length === 0) {
      console.log(`No results found for ${databaseId} with query: ${query}`);
      return NextResponse.json({ results: [] });
    }

    // Enhance the results with database-specific information
    const enhancedResults = results.map(result => ({
      ...result,
      source: databaseId,
      // Add any additional database-specific enhancements here
    }));

    console.log(`Found ${enhancedResults.length} results for ${databaseId} with query: ${query}`);
    return NextResponse.json({ results: enhancedResults });
  } catch (error) {
    console.error("Error in advanced scraping:", error);
    return NextResponse.json(
      { error: "Failed to perform advanced scraping" },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json(
    { error: "This endpoint only accepts POST requests" },
    { status: 405 }
  );
}