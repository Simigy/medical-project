import { NextResponse } from "next/server"
import type { SearchResult } from "@/types"

// Function to extract date from text (reused from proxy-search)
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

// Function to get source name based on URL domain
function getSourceFromUrl(url: string): string {
  try {
    const domain = new URL(url).hostname
    
    if (domain.includes('swissmedic')) return 'Swissmedic'
    if (domain.includes('fda.gov')) return 'FDA'
    if (domain.includes('ema.europa.eu')) return 'EMA'
    if (domain.includes('mhra.gov.uk')) return 'MHRA'
    if (domain.includes('tga.gov.au')) return 'TGA'
    if (domain.includes('medsafe.govt.nz')) return 'Medsafe'
    if (domain.includes('lakemedelsverket.se')) return 'Swedish Medical Products Agency'
    
    // Default to domain name if no specific match
    return domain.replace('www.', '')
  } catch (error) {
    return 'Unknown Source'
  }
}

// Main scraping function
async function scrapeWebsite(url: string, query: string): Promise<SearchResult[]> {
  try {
    console.log(`Scraping ${url} for query: ${query}`)
    
    // Set up fetch with appropriate headers to avoid being blocked
    const userAgents = [
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    ]
    const userAgent = userAgents[Math.floor(Math.random() * userAgents.length)]
    
    const headers: HeadersInit = {
      "User-Agent": userAgent,
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.5",
      "Referer": url,
      "Cache-Control": "no-cache",
      "Pragma": "no-cache",
    }
    
    // Set up timeout
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 15000) // 15 second timeout
    
    // Fetch the page
    const response = await fetch(url, {
      headers,
      signal: controller.signal,
    })
    
    clearTimeout(timeoutId)
    
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`)
    }
    
    const html = await response.text()
    
    // Check for access blocks
    if (
      html.includes("captcha") ||
      html.includes("access denied") ||
      html.includes("blocked") ||
      html.includes("too many requests")
    ) {
      throw new Error("Access blocked by website protection")
    }
    
    // Use a simpler approach to parse HTML without jsdom
    // Check for valid content
    if (!html || html.trim().length === 0) {
      throw new Error("Empty response or invalid HTML")
    }
    
    // Extract results using regex-based parsing
    return extractResultsWithoutJsdom(html, url, query)
  } catch (error) {
    console.error(`Error scraping ${url}:`, error)
    throw error
  }
}

// Extract results using regex-based parsing instead of DOM manipulation
function extractResultsWithoutJsdom(html: string, baseUrl: string, query: string): SearchResult[] {
  const results: SearchResult[] = []
  const maxResults = 10
  const source = getSourceFromUrl(baseUrl)
  const queryLower = query.toLowerCase()
  
  try {
    // Remove script and style tags to clean up the HTML
    const cleanHtml = html
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, '')
    
    // Find sections that contain the query
    const sections = cleanHtml.split(/<\/?(?:div|section|article|main|aside)(?:\s[^>]*)?>/i)
      .filter(section => section.toLowerCase().includes(queryLower))
    
    // Process each section that contains the query
    for (const section of sections) {
      if (results.length >= maxResults) break
      
      try {
        // Skip navigation, footer, header sections
        if (
          /<nav\b/i.test(section) ||
          /<footer\b/i.test(section) ||
          /<header\b/i.test(section) ||
          /class="[^"]*(?:navigation|footer|header)[^"]*"/i.test(section)
        ) {
          continue
        }
        
        // Extract headings
        const headingMatches = section.match(/<h[1-5][^>]*>([\s\S]*?)<\/h[1-5]>/gi) || []
        
        for (const headingMatch of headingMatches) {
          if (results.length >= maxResults) break
          
          // Extract title text
          const titleText = headingMatch.replace(/<[^>]+>/g, '').trim()
          if (!titleText) continue
          
          // Find a link near the heading
          const linkRegex = new RegExp(`<a[^>]*href="([^"#]*)"[^>]*>([\s\S]*?)<\/a>`, 'i')
          const linkMatch = section.match(linkRegex)
          
          if (!linkMatch) continue
          
          const href = linkMatch[1]
          if (!href || href.startsWith('#') || href.startsWith('javascript:')) continue
          
          // Resolve relative URLs
          const url = href.startsWith('http') ? href : new URL(href, baseUrl).href
          
          // Check if this URL is already in our results
          if (results.some(r => r.url === url)) continue
          
          // Extract a snippet - look for paragraphs
          let snippet = ''
          const paragraphMatches = section.match(/<p[^>]*>([\s\S]*?)<\/p>/gi)
          
          if (paragraphMatches && paragraphMatches.length > 0) {
            // Get the first paragraph text
            snippet = paragraphMatches[0].replace(/<[^>]+>/g, '').trim()
          } else {
            // If no paragraphs, use some text from the section
            snippet = section.replace(/<[^>]+>/g, '').trim().substring(0, 200)
            
            // Remove the title from the snippet to avoid duplication
            if (titleText && snippet.includes(titleText)) {
              snippet = snippet.replace(titleText, '').trim()
            }
          }
          
          results.push({
            id: `scrape-${results.length}`,
            title: titleText || 'Untitled',
            url: url,
            source: source,
            date: extractDateFromText(section) || new Date().toISOString().split('T')[0],
            snippet: snippet || `Result related to search term: ${query}`,
            authors: [],
          })
        }
      } catch (sectionError) {
        console.error('Error processing section:', sectionError)
        continue
      }
    }
    
    // If no results found with headings, try to find any links that contain the query
    if (results.length === 0) {
      const linkRegex = new RegExp(`<a[^>]*href="([^"#]*)"[^>]*>([\s\S]*?${queryLower}[\s\S]*?)<\/a>`, 'gi')
      let linkMatch
      
      while ((linkMatch = linkRegex.exec(cleanHtml)) !== null && results.length < maxResults) {
        try {
          const href = linkMatch[1]
          if (!href || href.startsWith('#') || href.startsWith('javascript:')) continue
          
          const linkText = linkMatch[2].replace(/<[^>]+>/g, '').trim()
          if (!linkText) continue
          
          // Resolve relative URLs
          const url = href.startsWith('http') ? href : new URL(href, baseUrl).href
          
          // Check if this URL is already in our results
          if (results.some(r => r.url === url)) continue
          
          results.push({
            id: `scrape-${results.length}`,
            title: linkText || 'Untitled',
            url: url,
            source: source,
            date: new Date().toISOString().split('T')[0],
            snippet: `Result related to search term: ${query}`,
            authors: [],
          })
        } catch (linkError) {
          console.error('Error processing link:', linkError)
          continue
        }
      }
    }
    
    return results
  } catch (error) {
    console.error(`Error in extractResultsWithoutJsdom:`, error)
    return []
  }
}

// API route handler
export async function POST(request: Request) {
  try {
    const { query, url } = await request.json()
    
    // Validate required parameters
    if (!query || !url) {
      return NextResponse.json({ error: "Missing required parameters" }, { status: 400 })
    }
    
    // Validate URL format
    try {
      new URL(url)
    } catch (e) {
      return NextResponse.json({ error: "Invalid URL format" }, { status: 400 })
    }
    
    console.log(`Scrape request for URL: ${url} with query: ${query}`)
    
    // Perform the scraping
    const results = await scrapeWebsite(url, query)
    
    // Return the results
    return NextResponse.json(results)
  } catch (error) {
    console.error("Error in scrape API route:", error)
    return NextResponse.json(
      { error: "An error occurred during scraping", message: (error as Error).message },
      { status: 500 }
    )
  }
}