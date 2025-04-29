import { apiConfigurations, proxyEndpoint } from "./api-config"
import type { SearchParams, SearchResult } from "@/types"
import { requiresAdvancedScraping, getDatabaseScrapingConfig } from "@/lib/scraping"

// Rate limiting implementation
const rateLimits: Record<string, { lastCall: number; callsThisMinute: number }> = {}

// Track database availability for adaptive retries
const databaseAvailability: Record<
  string,
  {
    available: boolean
    lastCheck: number
    consecutiveFailures: number
    apiPreferred: boolean
  }
> = {}

const checkRateLimit = (databaseId: string): boolean => {
  const config = apiConfigurations[databaseId]
  if (!config || !config.rateLimitPerMinute) return true

  const now = Date.now()
  const limit = rateLimits[databaseId] || { lastCall: 0, callsThisMinute: 0 }

  // Reset counter if it's been more than a minute
  if (now - limit.lastCall > 60000) {
    limit.callsThisMinute = 0
  }

  // Check if we're over the limit
  if (limit.callsThisMinute >= config.rateLimitPerMinute) {
    return false
  }

  // Update the limit
  rateLimits[databaseId] = {
    lastCall: now,
    callsThisMinute: limit.callsThisMinute + 1,
  }

  return true
}

// Check if a database has official API support
function hasOfficialApi(databaseId: string): boolean {
  return !!apiConfigurations[databaseId]
}

// Update database availability status
function updateDatabaseStatus(databaseId: string, success: boolean): void {
  const status = databaseAvailability[databaseId] || {
    available: true,
    lastCheck: 0,
    consecutiveFailures: 0,
    apiPreferred: hasOfficialApi(databaseId),
  }

  const now = Date.now()

  if (success) {
    status.available = true
    status.consecutiveFailures = 0
  } else {
    status.consecutiveFailures += 1
    // Mark as unavailable after 3 consecutive failures
    if (status.consecutiveFailures >= 3) {
      status.available = false
    }
  }

  status.lastCheck = now
  databaseAvailability[databaseId] = status
}

// Get the best method to search a database based on past performance
function getBestSearchMethod(databaseId: string): "api" | "proxy" | "advanced-proxy" {
  const status = databaseAvailability[databaseId]

  if (!status) {
    return hasOfficialApi(databaseId) ? "api" : "proxy"
  }

  if (status.apiPreferred && hasOfficialApi(databaseId)) {
    return "api"
  }

  // If regular proxy has been failing, try advanced proxy
  if (status.consecutiveFailures >= 2) {
    return "advanced-proxy"
  }

  return "proxy"
}

// Search a single database with direct API
export async function searchDatabaseApi(
  databaseId: string,
  query: string,
  options: { signal?: AbortSignal } = {},
): Promise<SearchResult[]> {
  const config = apiConfigurations[databaseId]
  if (!config) {
    throw new Error(`No API configuration found for database: ${databaseId}`)
  }

  // Check rate limit
  if (!checkRateLimit(databaseId)) {
    throw new Error(`Rate limit exceeded for database: ${databaseId}`)
  }

  try {
    // Build the URL with query parameters
    const url = new URL(`${config.baseUrl}${config.searchEndpoint}`)

    // Different APIs expect different parameter names
    if (databaseId === "fda-drugs") {
      url.searchParams.append(
        "search",
        `openfda.generic_name:"${query}" OR openfda.brand_name:"${query}" OR openfda.substance_name:"${query}"`,
      )
      url.searchParams.append("limit", "10")
    } else if (databaseId === "pubmed") {
      url.searchParams.append("db", "pubmed")
      url.searchParams.append("term", query)
      url.searchParams.append("retmode", "json")
      url.searchParams.append("retmax", "10")
    } else if (databaseId === "ema-medicines") {
      url.searchParams.append("name", query)
      url.searchParams.append("active_substance", query)
      url.searchParams.append("page", "1")
      url.searchParams.append("size", "10")
    } else if (databaseId === "who-iris") {
      url.searchParams.append("query", query)
      url.searchParams.append("limit", "10")
    } else if (databaseId === "canada-drug-db") {
      url.searchParams.append("brand_name", query)
      url.searchParams.append("limit", "10")
    } else {
      url.searchParams.append("q", query)
    }

    // Set up headers
    const headers: HeadersInit = {
      Accept:
        config.responseType === "json"
          ? "application/json"
          : config.responseType === "xml"
            ? "application/xml"
            : "text/html",
      ...config.headers,
    }

    // Add API key if required
    if (config.requiresAuth && config.authType === "apiKey" && config.apiKey) {
      if (databaseId === "fda-drugs") {
        url.searchParams.append("api_key", config.apiKey)
      } else {
        headers["X-API-Key"] = config.apiKey
      }
    }

    console.log(`Making API request to ${url.toString()}`)

    // Make the request
    const response = await fetch(url.toString(), {
      method: config.searchMethod,
      headers,
      signal: options.signal,
    })

    if (!response.ok) {
      updateDatabaseStatus(databaseId, false)
      throw new Error(`API request failed with status ${response.status}`)
    }

    let data
    if (config.responseType === "json") {
      data = await response.json()
    } else if (config.responseType === "xml") {
      // In a real app, you'd use a proper XML parser here
      const text = await response.text()
      // This is a simplified mock parser
      data = { ids: text.match(/\d{8}/g) || [] }
    } else {
      // For HTML responses, we'd need server-side parsing
      throw new Error("HTML parsing requires server-side processing")
    }

    // Parse the response using the database-specific parser
    const results = config.parser(data, query)

    // Update database status as successful
    updateDatabaseStatus(databaseId, true)

    return results
  } catch (error) {
    console.error(`Error searching database ${databaseId}:`, error)
    updateDatabaseStatus(databaseId, false)

    // Try proxy as fallback for API failures
    console.log(`Attempting proxy fallback for ${databaseId}`)
    try {
      const databaseUrl = config.baseUrl
      return await searchDatabaseViaProxy(databaseId, databaseUrl, query, options, true)
    } catch (proxyError) {
      console.error(`Proxy fallback also failed for ${databaseId}:`, proxyError)

      // Return an error result instead of throwing
      return [
        {
          id: `${databaseId}-error`,
          title: `Could not retrieve results from ${databaseId.toUpperCase()}`,
          url: config.baseUrl,
          source: databaseId.toUpperCase(),
          date: new Date().toISOString().split("T")[0],
          snippet: "This database could not be accessed. Please try again later or visit the database directly.",
          authors: [],
          isError: true,
        },
      ]
    }
  }
}

// Search a database that requires server-side proxy
export async function searchDatabaseViaProxy(
  databaseId: string,
  databaseUrl: string,
  query: string,
  options: { signal?: AbortSignal } = {},
  isAdvanced = false,
): Promise<SearchResult[]> {
  try {
    console.log(`Searching ${databaseId} via ${isAdvanced ? "advanced " : ""}proxy: ${databaseUrl}`)

    // Check if this database requires advanced scraping techniques
    if (isAdvanced || requiresAdvancedScraping(databaseId)) {
      // Get database-specific scraping configuration
      const scrapingConfig = getDatabaseScrapingConfig(databaseId)
      
      const response = await fetch(proxyEndpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          databaseId,
          url: databaseUrl,
          query,
          advanced: true, // Tell the proxy to use advanced techniques
          config: scrapingConfig, // Pass any database-specific configuration
        }),
        signal: options.signal,
      })

      if (!response.ok) {
        updateDatabaseStatus(databaseId, false)
        console.error(`Advanced proxy request failed with status ${response.status} for ${databaseId}`)
        throw new Error(`Advanced proxy request failed with status ${response.status}`)
      }

      const results = await response.json()
      updateDatabaseStatus(databaseId, true)
      return Array.isArray(results) ? results : []
    } else {
      const response = await fetch(proxyEndpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          databaseId,
          url: databaseUrl,
          query,
          advanced: isAdvanced, // Tell the proxy to use advanced techniques
        }),
        signal: options.signal,
      })

      if (!response.ok) {
        updateDatabaseStatus(databaseId, false)
        console.error(`Proxy request failed with status ${response.status} for ${databaseId}`)

        // If regular proxy failed, try advanced proxy
        if (!isAdvanced) {
          console.log(`Attempting advanced proxy for ${databaseId}`)
          return await searchDatabaseViaProxy(databaseId, databaseUrl, query, options, true)
        }

        throw new Error(`Proxy request failed with status ${response.status}`)
      }

      const results = await response.json()

      // Check if the response is an error object
      if (results && results.error) {
        updateDatabaseStatus(databaseId, false)
        console.error(`Proxy returned error for ${databaseId}: ${results.error}`)

        // If regular proxy returned error, try advanced proxy
        if (!isAdvanced) {
          console.log(`Attempting advanced proxy after error for ${databaseId}`)
          return await searchDatabaseViaProxy(databaseId, databaseUrl, query, options, true)
        }

        throw new Error(results.error)
      }

      // If we got an empty array, try advanced proxy
      if (Array.isArray(results) && results.length === 0 && !isAdvanced) {
        console.log(`No results found for ${databaseId}, trying advanced proxy`)
        return await searchDatabaseViaProxy(databaseId, databaseUrl, query, options, true)
      }

      // Update database status as successful
      updateDatabaseStatus(databaseId, true)

      return Array.isArray(results) ? results : []
    }
  } catch (error) {
    console.error(`Error searching database ${databaseId} via proxy:`, error)
    updateDatabaseStatus(databaseId, false)

    // Return an error result instead of throwing
    return [
      {
        id: `${databaseId}-error`,
        title: `Could not retrieve results from ${databaseId.toUpperCase()}`,
        url: databaseUrl,
        source: databaseId.toUpperCase(),
        date: new Date().toISOString().split("T")[0],
        snippet: "This database could not be accessed. Please try again later or visit the database directly.",
        authors: [],
        isError: true,
      },
    ]
  }
}

// Helper function to get database URL from ID
function getDatabaseUrlForId(databaseId: string, query: string): string {
  // Map database IDs to their search URLs
  const databaseUrls: Record<string, string> = {
    "swissmedic": `https://www.swissmedic.ch/swissmedic/en/home/humanarzneimittel/marktueberwachung/health-professional-communication--hpc-/search.html?query=${encodeURIComponent(query)}`,
    "ema-medicines": `https://www.ema.europa.eu/en/medicines/search?search_api_views_fulltext=${encodeURIComponent(query)}`,
    "mhra": `https://products.mhra.gov.uk/?query=${encodeURIComponent(query)}&page=1`,
    "tga": `https://www.tga.gov.au/search?query=${encodeURIComponent(query)}`,
    "medsafe": `https://www.medsafe.govt.nz/searchResults.asp?q=${encodeURIComponent(query)}`,
    "lakemedelsverket": `https://www.lakemedelsverket.se/en/search?q=${encodeURIComponent(query)}`,
    // Add more databases as needed
  }

  return databaseUrls[databaseId] || `https://www.google.com/search?q=${encodeURIComponent(query)}+site:${databaseId}`
}

// Main search function that coordinates searches across multiple databases
export async function searchDatabases(
  params: SearchParams,
  options: {
    signal?: AbortSignal
    onProgress?: (results: SearchResult[], databaseId: string) => void
  } = {},
): Promise<SearchResult[]> {
  const { activeIngredients, databaseUrls } = params
  const query = activeIngredients.join(" OR ")

  // Map URLs back to database IDs
  const databaseIds = databaseUrls
    .map((url) => {
      const entry = Object.entries(apiConfigurations).find(([_, config]) => config.baseUrl === url)
      return entry ? entry[0] : null
    })
    .filter(Boolean) as string[]

  // For databases with direct API access
  const apiSearchPromises = databaseIds.map(async (databaseId) => {
    if (apiConfigurations[databaseId]) {
      try {
        const results = await searchDatabaseApi(databaseId, query, { signal: options.signal })
        if (options.onProgress) {
          options.onProgress(results, databaseId)
        }
        return results
      } catch (error) {
        console.error(`Error searching ${databaseId}:`, error)

        // Return an error result instead of empty array
        const errorResult: SearchResult[] = [
          {
            id: `${databaseId}-error`,
            title: `Could not retrieve results from ${databaseId.toUpperCase()}`,
            url: apiConfigurations[databaseId].baseUrl,
            source: databaseId.toUpperCase(),
            date: new Date().toISOString().split("T")[0],
            snippet: "This database could not be accessed. Please try again later or visit the database directly.",
            authors: [],
            isError: true,
          },
        ]

        if (options.onProgress) {
          options.onProgress(errorResult, databaseId)
        }

        return errorResult
      }
    }
    return []
  })

  // For databases without API access (using proxy)
  const proxySearchPromises = databaseUrls
    .filter((url) => !databaseIds.some((id) => apiConfigurations[id]?.baseUrl === url))
    .map(async (url) => {
      // Extract database ID from URL
      const urlObj = new URL(url)
      const databaseId = urlObj.hostname.replace(/^www\./, "").split(".")[0]

      try {
        // Determine best search method based on past performance
        const method = getBestSearchMethod(databaseId)

        let results: SearchResult[] = []

        if (method === "advanced-proxy") {
          results = await searchDatabaseViaProxy(databaseId, url, query, { signal: options.signal }, true)
        } else {
          results = await searchDatabaseViaProxy(databaseId, url, query, { signal: options.signal })
        }

        if (options.onProgress) {
          options.onProgress(results, databaseId)
        }
        return results
      } catch (error) {
        console.error(`Error searching ${url} via proxy:`, error)

        // Return an error result instead of empty array
        const errorResult: SearchResult[] = [
          {
            id: `${databaseId}-error`,
            title: `Could not retrieve results from ${databaseId.toUpperCase()}`,
            url: url,
            source: databaseId.toUpperCase(),
            date: new Date().toISOString().split("T")[0],
            snippet: "This database could not be accessed. Please try again later or visit the database directly.",
            authors: [],
            isError: true,
          },
        ]

        if (options.onProgress) {
          options.onProgress(errorResult, databaseId)
        }

        return errorResult
      }
    })

  // Combine all search promises
  const allPromises = [...apiSearchPromises, ...proxySearchPromises]

  // Wait for all searches to complete
  const resultsArrays = await Promise.all(allPromises)

  // Flatten and return all results
  return resultsArrays.flat()
}
