"use client"

import { useState, useCallback, useEffect } from "react"
import SearchForm from "@/components/search/search-form"
import SearchResults from "@/components/search/search-results"
import type { SearchParams, SearchResult } from "@/types"
import { searchDatabases } from "@/lib/api/api-service"

export default function HomePage() {
  const [results, setResults] = useState<SearchResult[]>([])
  const [totalResults, setTotalResults] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [searchProgress, setSearchProgress] = useState<Record<string, number>>({})
  const [abortController, setAbortController] = useState<AbortController | null>(null)
  const [lastSearchParams, setLastSearchParams] = useState<SearchParams | null>(null)

  // Clean up the abort controller on unmount
  useEffect(() => {
    return () => {
      if (abortController) {
        abortController.abort()
      }
    }
  }, [abortController])

  const handleSearch = async (params: SearchParams) => {
    // Cancel any ongoing search
    if (abortController) {
      abortController.abort()
    }

    // Create a new abort controller for this search
    const newController = new AbortController()
    setAbortController(newController)

    setIsLoading(true)
    setResults([])
    setTotalResults(0)
    setSearchProgress({})
    setLastSearchParams(params)

    // Check if this is a batch search
    if (params.additionalFilters?.isBatchSearch && params.additionalFilters?.batchSearchResults) {
      // Handle batch search results
      const batchResults = params.additionalFilters.batchSearchResults as SearchResult[]

      // Process the batch results
      setResults(batchResults)
      setTotalResults(batchResults.length)
      setIsLoading(false)
      setAbortController(null)

      // Update progress for display
      const batchProgress: Record<string, number> = {}
      const sourceGroups = batchResults.reduce((acc, result) => {
        const source = result.source || "Unknown"
        acc[source] = (acc[source] || 0) + 1
        return acc
      }, {} as Record<string, number>)

      Object.entries(sourceGroups).forEach(([source, count]) => {
        batchProgress[source] = count
      })

      setSearchProgress(batchProgress)
      return
    }

    try {
      // Start the search
      const allResults = await searchDatabases(params, {
        signal: newController.signal,
        onProgress: (partialResults, databaseId) => {
          // Update results as they come in
          setResults((prevResults) => {
            // Filter out any existing results from this database
            const filteredResults = prevResults.filter((r) => !r.id.startsWith(`${databaseId}-`))
            const newResults = [...filteredResults, ...partialResults]
            setTotalResults(newResults.length)
            return newResults
          })

          // Update progress
          setSearchProgress((prev) => ({
            ...prev,
            [databaseId]: partialResults.length,
          }))
        },
      })

      // Ensure we have the final count
      setTotalResults(allResults.length)
    } catch (error) {
      console.error("Error during search:", error)
    } finally {
      // Ensure loading state is reset even if there's an error
      setIsLoading(false)
      setAbortController(null)
    }
  }

  const handleCancelSearch = () => {
    if (abortController) {
      abortController.abort()
      setIsLoading(false)
      setAbortController(null)
    }
  }

  const handleRetryDatabase = useCallback(
    (databaseId: string) => {
      if (!lastSearchParams) return

      // Create a new search params object with just this database
      const databaseUrl = lastSearchParams.databaseUrls.find((url) => {
        const urlObj = new URL(url)
        return urlObj.hostname.replace("www.", "").split(".")[0] === databaseId
      })

      if (!databaseUrl) return

      const retryParams: SearchParams = {
        ...lastSearchParams,
        databaseUrls: [databaseUrl],
      }

      // Remove existing results for this database
      setResults((prevResults) => prevResults.filter((r) => !r.id.startsWith(`${databaseId}-`)))

      // Start the search for just this database
      searchDatabases(retryParams, {
        onProgress: (partialResults, dbId) => {
          // Update results
          setResults((prevResults) => {
            const newResults = [...prevResults, ...partialResults]
            setTotalResults(newResults.length)
            return newResults
          })

          // Update progress
          setSearchProgress((prev) => ({
            ...prev,
            [dbId]: partialResults.length,
          }))
        },
      }).catch((error) => {
        console.error(`Error retrying database ${databaseId}:`, error)
      })
    },
    [lastSearchParams]
  )

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Advanced Medicine Database Search</h1>
        <p className="text-gray-600">
          Search for active ingredients across multiple trusted medical and pharmaceutical databases.
        </p>
      </div>

      <SearchForm onSubmit={handleSearch} isLoading={isLoading} onCancel={handleCancelSearch} />

      {(results.length > 0 || isLoading) && (
        <SearchResults
          results={results}
          totalResults={totalResults}
          isLoading={isLoading}
          searchProgress={searchProgress}
          onRetryDatabase={handleRetryDatabase}
        />
      )}
    </div>
  )
}
