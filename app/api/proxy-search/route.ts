import { NextResponse } from "next/server"
import { JSDOM } from "jsdom"
import type { SearchResult } from "@/types"

// Cache for storing successful search results to reduce repeated scraping
const resultCache: Record<string, { timestamp: number; results: SearchResult[] }> = {}
const CACHE_TTL = 3600000 // 1 hour cache TTL

// List of databases that are known to be problematic for scraping
// We'll use mock data for these instead of attempting to scrape
const PROBLEMATIC_DATABASES = [
  "fda",
  "lakemedelsverket", // Swedish Medical Products Agency
  "medsafe",
  "swissmedic",
  "aemps",
  "pmda",
  "mhra",
  "ema",
  "basg",
  "famhp",
  "ansm",
  "bfarm",
  "hpra",
  "aifa",
  "cbg",
  "infarmed",
  "dmp", // Norwegian Medicines Agency
]

// Database-specific extraction strategies
const extractionStrategies: Record<string, (document: Document, baseUrl: string, query: string) => SearchResult[]> = {
  // Add specialized extractors for each database
}

// Function to extract date from text
function extractDateFromText(text: string): string | null {
  if (!text) return null

  // Try to find a date in format YYYY-MM-DD
  const isoDateMatch = text.match(/\d{4}-\d{2}-\d{2}/)
  if (isoDateMatch) return isoDateMatch[0]

  // Try to find a date in format MM/DD/YYYY or DD/MM/YYYY
  const slashDateMatch = text.match(/\d{1,2}\/\d{1,2}\/\d{4}/)
  if (slashDateMatch) {
    const parts = slashDateMatch[0].split("/")
    if (parts.length === 3) {
      // Assume MM/DD/YYYY format
      return `${parts[2]}-${parts[0].padStart(2, "0")}-${parts[1].padStart(2, "0")}`
    }
  }

  // Try to find a date with month name
  const months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ]

  const monthPatterns = months.map(
    (month) => new RegExp(`(${month}|${month.substring(0, 3)})\\s+\\d{1,2},?\\s+\\d{4}`, "i"),
  )

  for (const pattern of monthPatterns) {
    const match = text.match(pattern)
    if (match) {
      const dateText = match[0]
      const monthMatch = dateText.match(new RegExp(months.map((m) => `(${m}|${m.substring(0, 3)})`).join("|"), "i"))
      if (monthMatch) {
        const monthName = monthMatch[0].toLowerCase()
        let monthIndex = -1

        for (let i = 0; i < months.length; i++) {
          if (months[i].toLowerCase().startsWith(monthName.substring(0, 3))) {
            monthIndex = i
            break
          }
        }

        if (monthIndex !== -1) {
          const dayMatch = dateText.match(/\d{1,2}/)
          const yearMatch = dateText.match(/\d{4}/)

          if (dayMatch && yearMatch) {
            return `${yearMatch[0]}-${(monthIndex + 1).toString().padStart(2, "0")}-${dayMatch[0].padStart(2, "0")}`
          }
        }
      }
    }
  }

  return null
}

// Mock function to simulate search results for problematic databases
function getMockResultsForDatabase(databaseId: string, query: string): SearchResult[] {
  // Implement your mock data generation logic here based on databaseId and query
  // This is just a placeholder
  return [
    {
      id: `${databaseId}-mock-1`,
      title: `Mock Result for ${databaseId}: ${query}`,
      url: "#",
      source: getDatabaseSourceName(databaseId),
      date: new Date().toISOString().split("T")[0],
      snippet: `This is a mock result for the query "${query}" in the ${databaseId} database.`,
      authors: [],
    },
  ]
}

// Function to get the source name of the database
function getDatabaseSourceName(databaseId: string): string {
  switch (databaseId) {
    case "fda":
      return "FDA"
    case "lakemedelsverket":
    case "sweden-medicines":
    case "sweden-safety":
    case "sweden-news":
    case "sweden-main":
    case "sweden-main-alt":
      return "Swedish Medical Products Agency"
    case "medsafe":
    case "medsafe-search":
    case "medsafe-db":
      return "Medsafe"
    case "swissmedic":
      return "Swissmedic"
    case "aemps":
    case "spain-medicines":
      return "AEMPS"
    case "pmda":
      return "PMDA"
    case "mhra":
    case "mhra-main":
    case "mhra-dsu":
    case "mhra-alerts":
      return "MHRA"
    case "ema":
      return "EMA"
    case "basg":
      return "BASG"
    case "famhp":
      return "FAMHP"
    case "ansm":
      return "ANSM"
    case "bfarm":
      return "BfArM"
    case "hpra":
      return "HPRA"
    case "aifa":
      return "AIFA"
    case "cbg":
      return "CBG"
    case "infarmed":
      return "Infarmed"
    case "dmp":
      return "Norwegian Medicines Agency"
    case "tga-cmi":
    case "tga-product-info":
    case "tga-safety":
    case "tga-safety-updates":
    case "tga-main":
      return "TGA"
    case "pubmed":
      return "PubMed"
    default:
      return databaseId // Or a more generic name if you prefer
  }
}

// This is a server-side proxy to handle searches for databases without APIs
// or to avoid CORS issues with direct browser requests
export async function POST(request: Request) {
  try {
    const { databaseId, url, query, advanced = false } = await request.json()

    if (!databaseId || !url || !query) {
      return NextResponse.json({ error: "Missing required parameters" }, { status: 400 })
    }

    console.log(`Proxy search request for ${databaseId} (${url}) with query: ${query}, advanced: ${advanced}`)

    // Check cache first
    const cacheKey = `${databaseId}:${query}`
    const cachedResult = resultCache[cacheKey]
    if (cachedResult && Date.now() - cachedResult.timestamp < CACHE_TTL) {
      console.log(`Returning cached results for ${databaseId}`)
      return NextResponse.json(cachedResult.results)
    }

    // For problematic databases, use mock data instead of attempting to scrape
    if (PROBLEMATIC_DATABASES.some((db) => databaseId.includes(db))) {
      console.log(`Using mock data for ${databaseId} search: ${query} (known problematic database)`)
      const mockResults = getMockResultsForDatabase(databaseId, query)
      return NextResponse.json(mockResults)
    }

    try {
      // Different scraping strategies based on the database
      const results = await scrapeDatabase(databaseId, url, query, advanced)

      // If no results were found, use mock data as fallback
      // Cache successful results
      if (results.length > 0) {
        resultCache[cacheKey] = {
          timestamp: Date.now(),
          results,
        }
      }

      return NextResponse.json(results)
    } catch (error) {
      console.error(`Error scraping database ${databaseId}:`, error)

      // Return an error result instead of throwing
      const errorResult: SearchResult[] = [
        {
          id: `${databaseId}-error`,
          title: `Could not retrieve results from ${getDatabaseSourceName(databaseId)}`,
          url: url,
          source: getDatabaseSourceName(databaseId),
          date: new Date().toISOString().split("T")[0],
          snippet: "This database could not be accessed. Please try again later or visit the database directly.",
          authors: [],
          isError: true,
        },
      ]

      return NextResponse.json(errorResult)
    }
  } catch (error) {
    console.error("Error in proxy search:", error)
    return NextResponse.json({ error: "Failed to process search request" }, { status: 500 })
  }
}

async function scrapeDatabase(
  databaseId: string,
  baseUrl: string,
  query: string,
  advanced: boolean,
): Promise<SearchResult[]> {
  try {
    // Construct the search URL based on the database
    const searchUrl = constructSearchUrl(databaseId, baseUrl, query)
    console.log(`Attempting to fetch: ${searchUrl}`)

    // Fetch the page with a timeout
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), advanced ? 30000 : 15000) // Longer timeout for advanced mode

    try {
      // Use different user agents to avoid detection
      const userAgents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
      ]

      const userAgent = userAgents[Math.floor(Math.random() * userAgents.length)]

      const headers: HeadersInit = {
        "User-Agent": userAgent,
        Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        Referer: baseUrl,
        "Cache-Control": "no-cache",
        Pragma: "no-cache",
      }

      // Add cookies for sites that require them
      if (databaseId.includes("lakemedelsverket") || databaseId.includes("sweden")) {
        headers["Cookie"] = "cookieconsent_status=allow; JSESSIONID=random"
      }

      const response = await fetch(searchUrl, {
        headers,
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        console.error(`Failed to fetch ${searchUrl}: ${response.status}`)
        throw new Error(`HTTP error ${response.status}`)
      }

      const html = await response.text()

      // Check if we got a captcha or access denied page
      if (
        html.includes("captcha") ||
        html.includes("access denied") ||
        html.includes("blocked") ||
        html.includes("too many requests")
      ) {
        throw new Error("Access blocked by website protection")
      }

      // Parse the HTML using JSDOM
      const dom = new JSDOM(html)
      const document = dom.window.document

      // Check if we got a proper page with content
      if (!document.body || document.body.textContent?.trim().length === 0) {
        throw new Error("Empty response or invalid HTML")
      }

      // Use database-specific extraction if available, otherwise use generic
      // Extract results based on the database structure
      return extractResults(databaseId, document, baseUrl, query, advanced)
    } catch (fetchError) {
      clearTimeout(timeoutId)
      console.error(`Fetch error for ${searchUrl}:`, fetchError)
      throw fetchError
    }
  } catch (error) {
    console.error(`Error in scrapeDatabase for ${databaseId}:`, error)
    throw error
  }
}

function constructSearchUrl(databaseId: string, baseUrl: string, query: string): string {
  // Encode the query for URL
  const encodedQuery = encodeURIComponent(query)

  // Database-specific URL construction
  switch (databaseId) {
    case "tga-cmi":
    case "tga-product-info":
    case "tga-safety":
    case "tga-safety-updates":
    case "tga-main":
      return `${baseUrl}/search?query=${encodedQuery}`

    case "mhra-main":
    case "mhra-dsu":
    case "mhra-alerts":
      return `${baseUrl}/search/site?keys=${encodedQuery}`

    case "aemps-main":
    case "spain-medicines":
      return `${baseUrl}/cima/publico/home.html?name=${encodedQuery}`

    case "medsafe-search":
    case "medsafe-db":
      return `${baseUrl}/Medicines/infoSearch.asp?searchfor=${encodedQuery}`

    case "fda-drugs":
      // FDA has a complex search system, this is a simplified approach
      return `${baseUrl}/scripts/cder/daf/index.cfm?event=BasicSearch.process&BasicSearchString=${encodedQuery}`

    case "pubmed":
      return `https://pubmed.ncbi.nlm.nih.gov/?term=${encodedQuery}`

    case "lakemedelsverket":
    case "sweden-medicines":
    case "sweden-safety":
    case "sweden-news":
    case "sweden-main":
    case "sweden-main-alt":
      // Swedish Medical Products Agency - multiple possible search endpoints
      return `${baseUrl}/sv/sok?q=${encodedQuery}`

    // Add more cases for other databases
    default:
      // Generic search URL pattern - try to guess based on the domain
      const urlObj = new URL(baseUrl)
      const domain = urlObj.hostname.replace("www.", "")

      if (domain.includes("gov")) {
        return `${baseUrl}/search?q=${encodedQuery}`
      } else if (domain.includes("lakemedelsverket")) {
        return `${baseUrl}/sv/sok?q=${encodedQuery}`
      } else {
        return `${baseUrl}/search?q=${encodedQuery}`
      }
  }
}

function extractResults(
  databaseId: string,
  document: Document,
  baseUrl: string,
  query: string,
  advanced: boolean,
): SearchResult[] {
  const results: SearchResult[] = []
  const maxResults = 10 // Limit the number of results to avoid processing too much data

  try {
    // Database-specific extraction logic
    switch (databaseId) {
      case "tga-cmi":
      case "tga-product-info":
      case "tga-safety":
      case "tga-safety-updates":
      case "tga-main": {
        // Example extraction for TGA website
        const resultElements = document.querySelectorAll(".search-result, .result-item, .search-item")

        if (resultElements.length === 0) {
          // Fallback to generic extraction
          return extractGenericResults(document, baseUrl, databaseId, query, maxResults, advanced)
        }

        resultElements.forEach((el, index) => {
          if (index >= maxResults) return

          const titleEl = el.querySelector(".search-result-title, .title, h3, h2")
          const snippetEl = el.querySelector(".search-result-snippet, .snippet, .description, p")
          const dateEl = el.querySelector(".search-result-date, .date, time")

          if (titleEl) {
            const linkEl = titleEl.querySelector("a") || titleEl.closest("a")
            const url = linkEl ? new URL(linkEl.getAttribute("href") || "", baseUrl).href : baseUrl

            results.push({
              id: `${databaseId}-${index}`,
              title: titleEl.textContent?.trim() || "Untitled",
              url: url,
              source: getDatabaseSourceName(databaseId),
              date: dateEl?.textContent?.trim() || new Date().toISOString().split("T")[0],
              snippet: snippetEl?.textContent?.trim() || "No description available",
              authors: [],
            })
          }
        })
        break
      }

      case "mhra-main":
      case "mhra-dsu":
      case "mhra-alerts": {
        // Example extraction for MHRA website
        const resultElements = document.querySelectorAll(".search-result, .results-list li, article")

        if (resultElements.length === 0) {
          // Fallback to generic extraction
          return extractGenericResults(document, baseUrl, databaseId, query, maxResults, advanced)
        }

        resultElements.forEach((el, index) => {
          if (index >= maxResults) return

          const titleEl = el.querySelector("h3, h2, .title")
          const snippetEl = el.querySelector(".search-result-excerpt, .excerpt, .summary, p")
          const dateEl = el.querySelector(".date, time, .published")

          if (titleEl) {
            const linkEl = titleEl.querySelector("a") || titleEl.closest("a")
            const url = linkEl ? new URL(linkEl.getAttribute("href") || "", baseUrl).href : baseUrl

            results.push({
              id: `${databaseId}-${index}`,
              title: titleEl.textContent?.trim() || "Untitled",
              url: url,
              source: getDatabaseSourceName(databaseId),
              date: dateEl?.textContent?.trim() || new Date().toISOString().split("T")[0],
              snippet: snippetEl?.textContent?.trim() || "No description available",
              authors: [],
            })
          }
        })
        break
      }

      case "medsafe-search":
      case "medsafe-db": {
        // Specific extraction for Medsafe
        const tables = document.querySelectorAll("table")
        let resultTable = null

        // Find the table that likely contains search results
        for (const table of tables) {
          if (table.querySelector("th") && table.textContent?.includes("Medicine")) {
            resultTable = table
            break
          }
        }

        if (resultTable) {
          const rows = resultTable.querySelectorAll("tr")

          // Skip header row
          for (let i = 1; i < rows.length && i <= maxResults; i++) {
            const row = rows[i]
            const cells = row.querySelectorAll("td")

            if (cells.length >= 2) {
              const nameCell = cells[0]
              const linkEl = nameCell.querySelector("a")

              if (linkEl) {
                const title = linkEl.textContent?.trim() || "Untitled Medicine"
                const relativeUrl = linkEl.getAttribute("href") || ""
                const url = new URL(relativeUrl, baseUrl).href

                results.push({
                  id: `${databaseId}-${i}`,
                  title: title,
                  url: url,
                  source: "Medsafe",
                  date: new Date().toISOString().split("T")[0], // Date might not be available
                  snippet: cells.length > 1 ? cells[1].textContent?.trim() || "" : "Medicine information",
                  authors: [],
                })
              }
            }
          }
        }

        // If no results found with specific extraction, try generic
        if (results.length === 0) {
          return extractGenericResults(document, baseUrl, databaseId, query, maxResults, advanced)
        }
        break
      }

      case "lakemedelsverket":
      case "sweden-medicines":
      case "sweden-safety":
      case "sweden-news":
      case "sweden-main":
      case "sweden-main-alt": {
        // Swedish Medical Products Agency - try multiple selector patterns
        const resultSelectors = [
          // Main search results
          ".search-result-item",
          ".search-result",
          ".result-item",
          // Product listings
          ".product-item",
          ".medicine-item",
          // News items
          ".news-item",
          "article",
          // Table rows
          "table tr",
          // Generic containers
          ".content-item",
          ".list-item",
        ]

        // Try each selector until we find results
        for (const selector of resultSelectors) {
          const elements = document.querySelectorAll(selector)
          if (elements.length > 0) {
            console.log(`Found ${elements.length} results with selector ${selector} for ${databaseId}`)

            elements.forEach((el, index) => {
              if (index >= maxResults) return

              // Try multiple title selectors
              const titleSelectors = ["h2", "h3", "h4", ".title", ".name", "a", "strong"]
              let titleEl = null
              for (const titleSelector of titleSelectors) {
                titleEl = el.querySelector(titleSelector)
                if (titleEl && titleEl.textContent?.trim()) break
              }

              if (!titleEl) return

              // Try to find a link
              const linkEl = titleEl.tagName === "A" ? titleEl : titleEl.querySelector("a") || el.querySelector("a")

              if (!linkEl) return

              const href = linkEl.getAttribute("href")
              if (!href) return

              // Construct absolute URL
              const url = href.startsWith("http") ? href : new URL(href, baseUrl).href

              // Try to find a snippet
              const snippetSelectors = ["p", ".description", ".summary", ".info", ".content"]
              let snippetEl = null
              for (const snippetSelector of snippetSelectors) {
                snippetEl = el.querySelector(snippetSelector)
                if (snippetEl && snippetEl.textContent?.trim()) break
              }

              // Try to find a date
              const dateSelectors = [".date", "time", ".published", "[datetime]"]
              let dateEl = null
              for (const dateSelector of dateSelectors) {
                dateEl = el.querySelector(dateSelector)
                if (dateEl && (dateEl.textContent?.trim() || dateEl.getAttribute("datetime"))) break
              }

              const date = dateEl
                ? dateEl.getAttribute("datetime") ||
                  extractDateFromText(dateEl.textContent || "") ||
                  new Date().toISOString().split("T")[0]
                : new Date().toISOString().split("T")[0]

              results.push({
                id: `${databaseId}-${index}`,
                title: titleEl.textContent?.trim() || "Untitled",
                url: url,
                source: "Swedish MPA",
                date: date,
                snippet: snippetEl?.textContent?.trim() || "No description available",
                authors: [],
              })
            })

            // If we found results, stop trying other selectors
            if (results.length > 0) break
          }
        }

        // If no results found with specific selectors, try generic extraction
        if (results.length === 0) {
          return extractGenericResults(document, baseUrl, databaseId, query, maxResults, advanced)
        }

        break
      }

      case "pubmed": {
        // Extract PubMed results
        const resultElements = document.querySelectorAll(".docsum-content, .results-article")

        resultElements.forEach((el, index) => {
          if (index >= maxResults) return

          const titleEl = el.querySelector(".docsum-title, .title")
          const authorsEl = el.querySelector(".docsum-authors, .authors")
          const journalEl = el.querySelector(".docsum-journal-citation, .citation")

          if (titleEl) {
            const linkEl = titleEl.querySelector("a") || titleEl.closest("a")
            const url = linkEl
              ? new URL(linkEl.getAttribute("href") || "", "https://pubmed.ncbi.nlm.nih.gov/").href
              : `https://pubmed.ncbi.nlm.nih.gov/?term=${encodeURIComponent(query)}`

            const authors =
              authorsEl?.textContent
                ?.trim()
                .split(",")
                .map((a) => a.trim()) || []

            results.push({
              id: `pubmed-${index}`,
              title: titleEl.textContent?.trim() || "Untitled Publication",
              url: url,
              source: "PubMed",
              date: extractDateFromText(journalEl?.textContent || "") || new Date().toISOString().split("T")[0],
              snippet: journalEl?.textContent?.trim() || "Medical publication",
              authors: authors,
            })
          }
        })

        if (results.length === 0) {
          return extractGenericResults(document, baseUrl, databaseId, query, maxResults, advanced)
        }
        break
      }

      case "fda-drugs": {
        // FDA has a complex structure, try multiple selectors
        const resultElements = document.querySelectorAll(".result-item, .search-result, tr.data-row, .product-details")

        if (resultElements.length === 0) {
          // Try to find tables that might contain results
          const tables = document.querySelectorAll("table")
          for (const table of tables) {
            const rows = table.querySelectorAll("tr")
            if (rows.length > 1) {
              // Has at least a header and a data row
              for (let i = 1; i < rows.length && i <= maxResults; i++) {
                const row = rows[i]
                const cells = row.querySelectorAll("td")

                if (cells.length >= 2) {
                  const nameCell = cells[0]
                  const linkEl = nameCell.querySelector("a")

                  const title = nameCell.textContent?.trim() || "Untitled Drug"
                  const url = linkEl
                    ? new URL(linkEl.getAttribute("href") || "", baseUrl).href
                    : `${baseUrl}/scripts/cder/daf/index.cfm?event=overview.process&ApplNo=UNKNOWN`

                  results.push({
                    id: `fda-${i}`,
                    title: title,
                    url: url,
                    source: "FDA",
                    date: new Date().toISOString().split("T")[0],
                    snippet: cells.length > 1 ? cells[1].textContent?.trim() || "" : "Drug information",
                    authors: [],
                  })
                }
              }
            }
          }
        } else {
          resultElements.forEach((el, index) => {
            if (index >= maxResults) return

            const titleEl = el.querySelector("h3, h2, .title, .product-name, td:first-child")
            const snippetEl = el.querySelector(".description, .summary, p, td:nth-child(2)")

            if (titleEl) {
              const linkEl = titleEl.querySelector("a") || titleEl.closest("a")
              const url = linkEl
                ? new URL(linkEl.getAttribute("href") || "", baseUrl).href
                : `${baseUrl}/scripts/cder/daf/index.cfm?event=overview.process&ApplNo=UNKNOWN`

              results.push({
                id: `fda-${index}`,
                title: titleEl.textContent?.trim() || "Untitled Drug",
                url: url,
                source: "FDA",
                date: new Date().toISOString().split("T")[0],
                snippet: snippetEl?.textContent?.trim() || "Drug information",
                authors: [],
              })
            }
          })
        }

        // If no results found with specific extraction, try generic
        if (results.length === 0) {
          return extractGenericResults(document, baseUrl, databaseId, query, maxResults, advanced)
        }
        break
      }

      // Add more cases for other databases

      default:
        // Generic extraction logic for unknown database structures
        return extractGenericResults(document, baseUrl, databaseId, query, maxResults, advanced)
    }
  } catch (error) {
    console.error(`Error extracting results from ${databaseId}:`, error)
    // Return empty results instead of throwing
    return []
  }

  return results
}

// Generic extraction function as a fallback
function extractGenericResults(
  document: Document,
  baseUrl: string,
  databaseId: string,
  query: string,
  maxResults: number,
  advanced: boolean,
): SearchResult[] {
  const results: SearchResult[] = []

  try {
    // In advanced mode, try more aggressive extraction techniques
    if (advanced) {
      // 1. Try to find any element that contains the query text
      const allElements = document.querySelectorAll("*")
      const queryLower = query.toLowerCase()
      const relevantElements = Array.from(allElements).filter(
        (el) => {
          try {
            return el.textContent?.toLowerCase().includes(queryLower) &&
              !["script", "style", "meta", "link", "head"].includes(el.tagName.toLowerCase())
          } catch (e) {
            return false
          }
        }
      )

      for (const el of relevantElements) {
        if (results.length >= maxResults) break

        try {
          // Skip elements that are likely part of navigation, footer, etc.
          if (
            el.closest("nav") ||
            el.closest("footer") ||
            el.closest("header") ||
            el.getAttribute("role") === "navigation" ||
            el.classList.contains("navigation") ||
            el.classList.contains("footer") ||
            el.classList.contains("header")
          ) {
            continue
          }

          // Find the closest container that might be a result item
          const container = el.closest("article") || el.closest("div.item") || el.closest("li") || el.closest("tr") || el

          // Try to find a title and link
          const titleEl =
            container.querySelector("h1, h2, h3, h4, h5, .title, .heading") || container.querySelector("a") || container

          if (!titleEl) continue

          const linkEl = titleEl.tagName === "A" ? titleEl : titleEl.querySelector("a") || container.querySelector("a")

          if (!linkEl) continue

          const href = linkEl.getAttribute("href")
          if (!href || href.startsWith("#") || href.startsWith("javascript:")) continue

          // Check if this URL is already in our results
          const url = href.startsWith("http") ? href : new URL(href, baseUrl).href
          if (results.some((r) => r.url === url)) continue

          // Get text content for snippet
          let snippet = ""
          const paragraphs = container.querySelectorAll("p")
          if (paragraphs.length > 0) {
            for (const p of paragraphs) {
              if (p.textContent?.trim()) {
                snippet = p.textContent.trim()
                break
              }
            }
          } else {
            // If no paragraphs, use the container's text
            snippet = container.textContent?.trim() || ""
            // Remove the title text from the snippet to avoid duplication
            const titleText = titleEl.textContent?.trim() || ""
            if (titleText && snippet.includes(titleText)) {
              snippet = snippet.replace(titleText, "").trim()
            }
          }

          results.push({
            id: `${databaseId}-advanced-${results.length}`,
            title: titleEl.textContent?.trim() || "Untitled",
            url: url,
            source: getDatabaseSourceName(databaseId),
            date: extractDateFromText(container.textContent || "") || new Date().toISOString().split("T")[0],
            snippet: snippet || `Result related to search term: ${query}`,
            authors: [],
          })
        } catch (elementError) {
          console.error("Error processing element:", elementError)
          continue
        }
      }
    }

    // If advanced extraction didn't yield results, try standard methods
    if (results.length === 0) {
      // 1. Look for headings with links
      const headings = document.querySelectorAll("h1, h2, h3, h4, h5")
      for (const heading of headings) {
        if (results.length >= maxResults) break

        try {
          const linkEl = heading.querySelector("a") || heading.closest("a")
          if (linkEl && !linkEl.getAttribute("href")?.startsWith("#")) {
            const url = new URL(linkEl.getAttribute("href") || "", baseUrl).href

            // Get some surrounding text for the snippet
            let snippet = ""
            const nextEl = heading.nextElementSibling
            if (nextEl && nextEl.tagName.toLowerCase() === "p") {
              snippet = nextEl.textContent?.trim() || ""
            }

            results.push({
              id: `${databaseId}-${results.length}`,
              title: heading.textContent?.trim() || "Untitled",
              url: url,
              source: getDatabaseSourceName(databaseId),
              date: new Date().toISOString().split("T")[0],
              snippet: snippet || `Result related to search term: ${query}`,
              authors: [],
            })
          }
        } catch (headingError) {
          console.error("Error processing heading:", headingError)
          continue
        }
      }

      // 2. Look for common result containers
      if (results.length < maxResults) {
        const resultContainers = document.querySelectorAll(
          ".search-result, .result, .search-item, .item, article, .card, .list-item",
        )

        for (const container of resultContainers) {
          if (results.length >= maxResults) break

          try {
            // Skip if this container is likely a wrapper for other results
            if (container.querySelectorAll(".search-result, .result, .search-item, .item").length > 0) {
              continue
            }

            const titleEl = container.querySelector("h1, h2, h3, h4, h5, .title, .heading")
            if (!titleEl) continue

            const linkEl = titleEl.querySelector("a") || titleEl.closest("a") || container.querySelector("a")
            if (!linkEl || linkEl.getAttribute("href")?.startsWith("#")) continue

            const url = new URL(linkEl.getAttribute("href") || "", baseUrl).href

            // Try to find a snippet
            let snippet = ""
            const snippetEl = container.querySelector("p, .description, .excerpt, .summary, .snippet")
            if (snippetEl) {
              snippet = snippetEl.textContent?.trim() || ""
            }

            // Try to find a date
            let date = new Date().toISOString().split("T")[0]
            const dateEl = container.querySelector(".date, time, .published, [datetime]")
            if (dateEl) {
              const dateAttr = dateEl.getAttribute("datetime")
              if (dateAttr) {
                date = dateAttr.split("T")[0]
              } else {
                date = extractDateFromText(dateEl.textContent || "") || date
              }
            }

            results.push({
              id: `${databaseId}-${results.length}`,
              title: titleEl.textContent?.trim() || "Untitled",
              url: url,
              source: getDatabaseSourceName(databaseId),
              date: date,
              snippet: snippet || `Result related to search term: ${query}`,
              authors: [],
            })
          } catch (containerError) {
            console.error("Error processing container:", containerError)
            continue
          }
        }
      }

      // 3. Last resort: just find links with text that might be relevant
      if (results.length < maxResults) {
        const links = document.querySelectorAll("a")

        for (const link of links) {
          if (results.length >= maxResults) break

          try {
            const href = link.getAttribute("href")
            if (!href || href.startsWith("#") || href.startsWith("javascript:")) continue

            const text = link.textContent?.trim()
            if (!text || text.length < 10) continue

            // Skip navigation links, which often have short text
            if (link.closest("nav, header, footer")) continue

            // Skip if this link is already part of a result we found
            let alreadyIncluded = false
            for (const result of results) {
              if (result.url === new URL(href, baseUrl).href) {
                alreadyIncluded = true
                break
              }
            }
            
            if (alreadyIncluded) continue
            
            results.push({
              id: `${databaseId}-link-${results.length}`,
              title: text,
              url: new URL(href, baseUrl).href,
              source: getDatabaseSourceName(databaseId),
              date: new Date().toISOString().split('T')[0],
              snippet: `Link found on page: ${text}`,
              authors: [],
            })
          } catch (linkError) {
            console.error("Error processing link:", linkError)
            continue
          }
        }
      }
    }
    
    return results
  } catch (error) {
    console.error(`Error in extractGenericResults for ${databaseId}:`, error)
    return []
  }
}
