"use client"

import { useState, useEffect } from "react"
import { ExternalLink, Download, Bookmark, Filter, AlertCircle, AlertTriangle, RefreshCw } from "lucide-react"
import type { SearchResult } from "@/types"

interface SearchResultsProps {
  results: SearchResult[]
  totalResults: number
  isLoading: boolean
  searchProgress?: Record<string, number>
  onRetryDatabase?: (databaseId: string) => void
}

export default function SearchResults({
  results,
  totalResults,
  isLoading,
  searchProgress = {},
  onRetryDatabase,
}: SearchResultsProps) {
  const [sortBy, setSortBy] = useState<"date" | "relevance">("date")
  const [filterSource, setFilterSource] = useState<string | null>(null)
  const [savedResults, setSavedResults] = useState<SearchResult[]>([])

  // Load saved results from localStorage on component mount
  useEffect(() => {
    const saved = localStorage.getItem("savedResults")
    if (saved) {
      try {
        setSavedResults(JSON.parse(saved))
      } catch (e) {
        console.error("Failed to parse saved results:", e)
      }
    }
  }, [])

  // Save results to localStorage when they change
  const saveResult = (result: SearchResult) => {
    const newSavedResults = [...savedResults, result]
    setSavedResults(newSavedResults)
    localStorage.setItem("savedResults", JSON.stringify(newSavedResults))
  }

  const removeResult = (resultId: string) => {
    const newSavedResults = savedResults.filter((r) => r.id !== resultId)
    setSavedResults(newSavedResults)
    localStorage.setItem("savedResults", JSON.stringify(newSavedResults))
  }

  // Get unique sources for filtering
  const sources = Array.from(new Set(results.map((result) => result.source)))

  // Apply sorting and filtering
  const filteredResults = [...results]
    .filter((result) => (filterSource ? result.source === filterSource : true))
    .sort((a, b) => {
      if (sortBy === "date") {
        return new Date(b.date).getTime() - new Date(a.date).getTime()
      }
      // For relevance sorting, use the relevanceScore if available
      return (b.relevanceScore || 0) - (a.relevanceScore || 0)
    })

  // Count results by source
  const resultsBySource = results.reduce(
    (acc, result) => {
      acc[result.source] = (acc[result.source] || 0) + 1
      return acc
    },
    {} as Record<string, number>,
  )

  // Count error results
  const errorResults = results.filter((result) => result.isError)
  const hasErrors = errorResults.length > 0

  if (isLoading && results.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 mt-6">
        <div className="flex flex-col items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-gray-600 mb-4">Searching medical databases...</p>

          {/* Progress indicator */}
          {Object.keys(searchProgress).length > 0 && (
            <div className="w-full max-w-md">
              <p className="text-sm text-gray-500 mb-2">Search progress by database:</p>
              <div className="space-y-2">
                {Object.entries(searchProgress).map(([database, count]) => (
                  <div key={database} className="flex items-center">
                    <span className="text-xs text-gray-600 w-32 truncate">{database}:</span>
                    <span className="text-xs font-medium text-blue-600 ml-2">{count} results</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  if (results.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 mt-6">
        <div className="text-center py-8">
          <AlertCircle className="h-16 w-16 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-700 mb-1">No results found</h3>
          <p className="text-gray-500">Try different search terms or databases.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mt-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-4">
        <div>
          <h2 className="text-xl font-semibold text-gray-800">Search Results</h2>
          <p className="text-gray-600">
            Found {totalResults} results {isLoading && "(still searching...)"}
          </p>
        </div>

        <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4 mt-3 md:mt-0">
          <div className="flex items-center">
            <label htmlFor="sortBy" className="mr-2 text-sm text-gray-600">
              Sort:
            </label>
            <select
              id="sortBy"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as "date" | "relevance")}
              className="border border-gray-300 rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="date">Newest First</option>
              <option value="relevance">Relevance</option>
            </select>
          </div>

          <div className="flex items-center">
            <Filter size={16} className="mr-1 text-gray-600" />
            <label htmlFor="filterSource" className="mr-2 text-sm text-gray-600">
              Source:
            </label>
            <select
              id="filterSource"
              value={filterSource || ""}
              onChange={(e) => setFilterSource(e.target.value || null)}
              className="border border-gray-300 rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">All Sources</option>
              {sources.map((source) => (
                <option key={source} value={source}>
                  {source} ({resultsBySource[source] || 0})
                </option>
              ))}
            </select>
          </div>

          <button
            className="flex items-center text-sm text-blue-600 hover:text-blue-800"
            onClick={() => {
              // Export all results as CSV
              const csvContent = [
                ["Title", "Source", "Date", "URL"].join(","),
                ...filteredResults.map((result) =>
                  [`"${result.title.replace(/"/g, '""')}"`, result.source, result.date, result.url].join(","),
                ),
              ].join("\n")

              const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
              const url = URL.createObjectURL(blob)
              const link = document.createElement("a")
              link.setAttribute("href", url)
              link.setAttribute("download", "search_results.csv")
              document.body.appendChild(link)
              link.click()
              document.body.removeChild(link)
            }}
          >
            <Download size={16} className="mr-1" />
            Export
          </button>
        </div>
      </div>

      {/* Error notification */}
      {hasErrors && (
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
          <p className="text-sm text-yellow-700 flex items-center">
            <AlertTriangle size={16} className="mr-2" />
            Some databases could not be accessed. You can try again or visit them directly.
          </p>
        </div>
      )}

      {/* Source distribution chart */}
      {sources.length > 1 && (
        <div className="mb-6 p-4 border border-gray-200 rounded-lg">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Results by Source</h3>
          <div className="flex items-end h-24">
            {Object.entries(resultsBySource).map(([source, count], index) => {
              const percentage = Math.round((count / totalResults) * 100)
              const hue = (index * 25) % 360 // Generate different colors
              return (
                <div
                  key={source}
                  className="flex flex-col items-center mr-2"
                  style={{ width: `${Math.max(5, percentage)}%` }}
                >
                  <div
                    className="w-full rounded-t"
                    style={{
                      backgroundColor: `hsl(${hue}, 70%, 60%)`,
                      height: `${Math.max(20, percentage)}%`,
                    }}
                  ></div>
                  <div className="text-xs text-gray-600 mt-1 truncate w-full text-center">{source}</div>
                  <div className="text-xs font-medium">{count}</div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {isLoading && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-sm text-blue-700 flex items-center">
            <svg
              className="animate-spin -ml-1 mr-2 h-4 w-4 text-blue-700"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            Still searching additional databases. Results will update as they arrive.
          </p>
        </div>
      )}

      <div className="space-y-4">
        {filteredResults.map((result) => {
          const isSaved = savedResults.some((r) => r.id === result.id)
          const isError = result.isError

          return (
            <div
              key={result.id}
              className={`border ${isError ? "border-yellow-200 bg-yellow-50" : "border-gray-200"} rounded-lg p-4 hover:shadow-md transition-shadow duration-200`}
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-medium text-gray-800 hover:text-blue-600">
                    {isError ? (
                      <span className="flex items-center text-yellow-700">
                        <AlertTriangle size={16} className="mr-1" />
                        {result.title}
                      </span>
                    ) : (
                      <a href={result.url} target="_blank" rel="noopener noreferrer" className="flex items-center">
                        {result.title}
                        <ExternalLink size={16} className="ml-1" />
                      </a>
                    )}
                  </h3>

                  <div className="flex items-center mt-1 text-sm">
                    <span
                      className={`${isError ? "bg-yellow-100 text-yellow-800" : "bg-blue-100 text-blue-800"} px-2 py-0.5 rounded-full font-medium`}
                    >
                      {result.source}
                    </span>
                    <span className="mx-2 text-gray-400">•</span>
                    <span className="text-gray-600">{result.date}</span>
                    {result.relevanceScore && (
                      <>
                        <span className="mx-2 text-gray-400">•</span>
                        <span className="text-gray-600">Relevance: {result.relevanceScore.toFixed(2)}</span>
                      </>
                    )}
                  </div>
                </div>

                {isError && onRetryDatabase ? (
                  <button
                    className="text-yellow-600 hover:text-yellow-800 transition-colors p-1"
                    title="Retry this database"
                    onClick={() => {
                      // Extract database ID from the result ID
                      const databaseId = result.id.split("-")[0]
                      onRetryDatabase(databaseId)
                    }}
                  >
                    <RefreshCw size={18} />
                  </button>
                ) : (
                  <button
                    className={`text-gray-400 hover:text-blue-600 transition-colors p-1 ${isSaved ? "text-blue-600" : ""}`}
                    title={isSaved ? "Remove from favorites" : "Save to favorites"}
                    onClick={() => (isSaved ? removeResult(result.id) : saveResult(result))}
                  >
                    <Bookmark size={18} fill={isSaved ? "currentColor" : "none"} />
                  </button>
                )}
              </div>

              <p className="mt-2 text-gray-600 text-sm line-clamp-2">{result.snippet}</p>

              {result.authors && result.authors.length > 0 && (
                <div className="mt-2 text-xs text-gray-500">
                  <span className="font-medium">Authors:</span> {result.authors.join(", ")}
                </div>
              )}

              {isError && (
                <div className="mt-2">
                  <a
                    href={result.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:text-blue-800 flex items-center"
                  >
                    Visit database directly
                    <ExternalLink size={14} className="ml-1" />
                  </a>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
