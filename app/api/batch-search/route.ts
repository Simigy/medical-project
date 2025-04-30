import { NextResponse } from "next/server";
// These imports are only available on the server side
import { spawn, exec } from "child_process";
import { promisify } from "util";
import path from "path";
import fs from "fs";
import type { SearchResult } from "@/types";

const execAsync = promisify(exec);

// Mark this file as server-side only
export const runtime = 'nodejs';

/**
 * API endpoint to run the batch scraper and stream logs back to the client
 */
export async function POST(request: Request) {
  // This is a streaming response
  const encoder = new TextEncoder();
  const customReadable = new ReadableStream({
    async start(controller) {
      try {
        // Parse the request body
        const body = await request.json();
        const {
          query,
          databaseIds,
          limit,
          fromDate,
          toDate,
          useCommercialDatabases,
          useCaptchaSolver,
          useBrowserAutomation
        } = body;

        if (!query) {
          controller.enqueue(encoder.encode("ERROR: Missing required parameter: query\n"));
          controller.close();
          return;
        }

        // Create a temporary file to store results
        const timestamp = Date.now();
        const resultsFile = path.join(process.cwd(), "scraping", `results_${timestamp}.json`);

        // Build the command to run the smart access manager instead of the batch scraper
        const scriptPath = path.join(process.cwd(), "scraping", "smart_access_manager.py");
        const args = [
          "--query", query,
          "--output", resultsFile,
          "--parallel"  // Use parallel processing for faster results
        ];

        // Add optional parameters
        if (limit && !isNaN(parseInt(limit))) {
          args.push("--max-results", limit.toString());
        }

        // Add date range if provided
        // Use 2025 as the default date range
        const futureDate = new Date("2025-12-31");
        const startDate = new Date("2025-01-01");

        const defaultFromDate = startDate.toISOString().split('T')[0]; // Format: YYYY-MM-DD
        const defaultToDate = futureDate.toISOString().split('T')[0]; // Format: YYYY-MM-DD

        args.push("--min-date", fromDate || defaultFromDate);
        args.push("--max-date", toDate || defaultToDate);

        // Add database IDs if provided, or use a limited set of databases
        if (databaseIds && Array.isArray(databaseIds) && databaseIds.length > 0) {
          args.push("--databases", ...databaseIds);
        } else {
          // Use only PubMed since it's the most reliable
          args.push("--databases", "pubmed");
        }

        // Add CAPTCHA API key if available in environment variables
        const captchaApiKey = process.env.CAPTCHA_API_KEY;
        if (captchaApiKey) {
          args.push("--captcha-api-key", captchaApiKey);
        }

        // Add commercial databases option
        if (useCommercialDatabases) {
          args.push("--include-commercial");
        }

        // Add CAPTCHA solver option
        if (useCaptchaSolver === false) {
          args.push("--no-captcha-solver");
        }

        // Add browser automation option
        if (useBrowserAutomation === false) {
          args.push("--no-browser-automation");
        }

        // Check if requirements are installed
        const requirementsFile = path.join(process.cwd(), "scraping", "requirements.txt");
        if (fs.existsSync(requirementsFile)) {
          controller.enqueue(encoder.encode(`Checking Python dependencies...\n`));
          try {
            // Try to install requirements
            const { stdout, stderr } = await execAsync(`pip install -r ${requirementsFile}`);
            if (stderr) {
              controller.enqueue(encoder.encode(`Warning installing dependencies: ${stderr}\n`));
            } else {
              controller.enqueue(encoder.encode(`Dependencies installed successfully\n`));
            }
          } catch (error) {
            controller.enqueue(encoder.encode(`Warning: Failed to install dependencies: ${error.message}\n`));
            controller.enqueue(encoder.encode(`Continuing anyway, but scraping might fail\n`));
          }
        }

        controller.enqueue(encoder.encode(`Starting batch search for query: "${query}"\n`));
        controller.enqueue(encoder.encode(`Command: python ${scriptPath} ${args.join(" ")}\n`));

        // Spawn the process to run the actual Python script
        const pythonProcess = spawn("python", [scriptPath, ...args]);

        // Handle stdout
        pythonProcess.stdout.on("data", (data) => {
          controller.enqueue(encoder.encode(data.toString()));
        });

        // Handle stderr
        pythonProcess.stderr.on("data", (data) => {
          controller.enqueue(encoder.encode(`ERROR: ${data.toString()}`));
        });

        // Handle process completion
        await new Promise<void>((resolve, reject) => {
          pythonProcess.on("close", (code) => {
            if (code === 0) {
              controller.enqueue(encoder.encode(`Batch search completed successfully\n`));
              resolve();
            } else {
              controller.enqueue(encoder.encode(`ERROR: Batch search failed with code ${code}\n`));
              reject(new Error(`Process exited with code ${code}`));
            }
          });

          pythonProcess.on("error", (err) => {
            controller.enqueue(encoder.encode(`ERROR: ${err.message}\n`));
            reject(err);
          });
        }).catch((error) => {
          console.error("Process error:", error);
          // We don't rethrow here because we want to continue to try to read the results
        });

        // Check if the results file exists
        if (!fs.existsSync(resultsFile)) {
          controller.enqueue(encoder.encode("ERROR: Batch scraper did not produce results\n"));
          controller.close();
          return;
        }

        // Read the results file
        controller.enqueue(encoder.encode(`Reading results from ${resultsFile}\n`));
        const resultsData = fs.readFileSync(resultsFile, "utf-8");
        let results: SearchResult[] = [];

        try {
          results = JSON.parse(resultsData);

          // Filter results by date if date range is provided
          if (fromDate || toDate) {
            const fromDateObj = fromDate ? new Date(fromDate) : new Date(0); // If no fromDate, use epoch
            const toDateObj = toDate ? new Date(toDate) : new Date(8640000000000000); // If no toDate, use max date

            results = results.filter(result => {
              if (!result.date) return true; // Keep results without dates
              const resultDate = new Date(result.date);
              return resultDate >= fromDateObj && resultDate <= toDateObj;
            });

            controller.enqueue(encoder.encode(`Filtered to ${results.length} results within date range\n`));
          }

          controller.enqueue(encoder.encode(`Successfully parsed ${results.length} results\n`));
        } catch (error) {
          controller.enqueue(encoder.encode(`ERROR: Failed to parse batch scraper results: ${error}\n`));
          controller.close();
          return;
        }

        // Clean up the temporary file
        fs.unlinkSync(resultsFile);
        controller.enqueue(encoder.encode(`Cleaned up temporary file\n`));

        // Send the final results
        controller.enqueue(encoder.encode(`RESULTS:${JSON.stringify(results)}\n`));
        controller.enqueue(encoder.encode("DONE\n"));
        controller.close();
      } catch (error) {
        console.error("Error in batch search API:", error);
        controller.enqueue(encoder.encode(`ERROR: An unexpected error occurred: ${error}\n`));
        controller.close();
      }
    }
  });

  return new Response(customReadable, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
    },
  });
}

export async function GET() {
  return NextResponse.json(
    { error: "This endpoint only accepts POST requests" },
    { status: 405 }
  );
}
