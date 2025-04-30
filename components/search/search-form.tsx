"use client"

import type React from "react"

import { useState } from "react"
import { Search, PlusCircle, MinusCircle, X, Database as DatabaseIcon, Zap, AlertTriangle, Terminal } from "lucide-react"
import type { SearchParams } from "@/types"
import { defaultDatabases } from "@/data/default-databases"
import SearchLogs from "./search-logs"
import { runBatchSearch } from "@/lib/scraping/client"

interface SearchFormProps {
  onSubmit: (params: SearchParams) => void
  isLoading: boolean
  onCancel?: () => void
}

interface Database {
  id: string
  name: string
  description: string
  url: string
}

export default function SearchForm({ onSubmit, isLoading, onCancel }: SearchFormProps) {
  const [activeIngredients, setActiveIngredients] = useState<string[]>([""])
  const [selectedDatabases, setSelectedDatabases] = useState<string[]>(["pubmed", "fda-drugs", "ema-medicines", "nejm", "amjmed"])
  // Set default date range to 2025
  const futureDate = new Date("2025-12-31")
  const startDate = new Date("2025-01-01")

  const defaultFromDate = startDate.toISOString().split('T')[0] // Format: YYYY-MM-DD
  const defaultToDate = futureDate.toISOString().split('T')[0] // Format: YYYY-MM-DD

  const [fromDate, setFromDate] = useState<string>(defaultFromDate)
  const [toDate, setToDate] = useState<string>(defaultToDate)
  const [databaseFilter, setDatabaseFilter] = useState("")
  const [expandedCategories, setExpandedCategories] = useState<string[]>(["Australia", "United States"])
  const [useBatchSearch, setUseBatchSearch] = useState<boolean>(true)
  const [batchSearchLimit, setBatchSearchLimit] = useState<number>(10)
  const [useCommercialDatabases, setUseCommercialDatabases] = useState<boolean>(false)
  const [useCaptchaSolver, setUseCaptchaSolver] = useState<boolean>(true)
  const [useBrowserAutomation, setUseBrowserAutomation] = useState<boolean>(true)

  // Logs state
  const [logs, setLogs] = useState<string[]>([])
  const [showLogs, setShowLogs] = useState<boolean>(false)
  const [isStreaming, setIsStreaming] = useState<boolean>(false)

  const handleAddActiveIngredient = () => {
    setActiveIngredients([...activeIngredients, ""])
  }

  const handleRemoveActiveIngredient = (index: number) => {
    const updatedIngredients = [...activeIngredients]
    updatedIngredients.splice(index, 1)
    setActiveIngredients(updatedIngredients)
  }

  const handleIngredientChange = (index: number, value: string) => {
    const updatedIngredients = [...activeIngredients]
    updatedIngredients[index] = value
    setActiveIngredients(updatedIngredients)
  }

  const handleDatabaseChange = (databaseId: string) => {
    if (selectedDatabases.includes(databaseId)) {
      setSelectedDatabases(selectedDatabases.filter((id) => id !== databaseId))
    } else {
      setSelectedDatabases([...selectedDatabases, databaseId])
    }
  }

  const filterDatabases = () => {
    if (!databaseFilter) return defaultDatabases

    return defaultDatabases.filter(
      (db) =>
        db.name.toLowerCase().includes(databaseFilter.toLowerCase()) ||
        db.description.toLowerCase().includes(databaseFilter.toLowerCase()),
    )
  }

  const getDatabaseCategories = () => {
    const categories: Record<string, Database[]> = {}

    defaultDatabases.forEach((db) => {
      // Extract category from description or name
      let category = "Other"

      if (db.id.startsWith("tga") || db.description.includes("Australian")) {
        category = "Australia"
      } else if (db.id.startsWith("fda") || db.description.includes("US Food")) {
        category = "United States"
      } else if (db.id.startsWith("mhra") || db.description.includes("UK")) {
        category = "United Kingdom"
      } else if (db.id.startsWith("ema") || db.description.includes("European")) {
        category = "European Union"
      } else if (db.id.startsWith("pmda") || db.description.includes("Japanese")) {
        category = "Japan"
      } else if (db.id.startsWith("hsa") || db.description.includes("Singapore")) {
        category = "Singapore"
      } else if (db.description.includes("Journal")) {
        category = "Medical Journals"
      } else if (db.id.startsWith("who") || db.description.includes("WHO")) {
        category = "WHO"
      } else if (db.id.startsWith("canada") || db.description.includes("Canada")) {
        category = "Canada"
      }

      if (!categories[category]) {
        categories[category] = []
      }

      categories[category].push(db)
    })

    return categories
  }

  const toggleCategory = (category: string) => {
    if (expandedCategories.includes(category)) {
      setExpandedCategories(expandedCategories.filter((c) => c !== category))
    } else {
      setExpandedCategories([...expandedCategories, category])
    }
  }

  const selectAllInCategory = (category: string, databases: Database[]) => {
    const dbIds = databases.map((db) => db.id)
    const allSelected = dbIds.every((id) => selectedDatabases.includes(id))

    if (allSelected) {
      // If all are selected, deselect all in this category
      setSelectedDatabases(selectedDatabases.filter((id) => !dbIds.includes(id)))
    } else {
      // Otherwise, ensure all in this category are selected
      // First remove any that might be in the category (to avoid duplicates)
      const filtered = selectedDatabases.filter((id) => !dbIds.includes(id))
      // Then add all database IDs from this category
      setSelectedDatabases([...filtered, ...dbIds])
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Filter out empty ingredients
    const filteredIngredients = activeIngredients.filter((ingredient) => ingredient.trim() !== "")

    if (filteredIngredients.length === 0) {
      alert("Please enter at least one active ingredient")
      return
    }

    if (selectedDatabases.length === 0) {
      alert("Please select at least one database")
      return
    }

    // If using batch search, call the batch search API
    if (useBatchSearch) {
      // Confirm if a large number of databases are selected
      if (selectedDatabases.length > 20 && batchSearchLimit === 0) {
        const confirmSearch = window.confirm(
          `You have selected ${selectedDatabases.length} databases for batch search. This may take a long time. Do you want to continue?`
        )
        if (!confirmSearch) {
          return
        }
      }

      // Clear previous logs and show the logs panel
      setLogs([])
      setShowLogs(true)
      setIsStreaming(true)

      try {
        // Call the batch search API with streaming response
        const response = await fetch("/api/batch-search", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            query: filteredIngredients.join(" OR "),
            databaseIds: selectedDatabases,
            limit: batchSearchLimit > 0 ? batchSearchLimit : undefined,
            fromDate: fromDate || null,
            toDate: toDate || null,
            useCommercialDatabases: useCommercialDatabases,
            useCaptchaSolver: useCaptchaSolver,
            useBrowserAutomation: useBrowserAutomation,
          }),
        })

        if (!response.ok) {
          throw new Error(`Server responded with status: ${response.status}`)
        }

        // Get the reader from the response body
        const reader = response.body?.getReader()
        if (!reader) {
          throw new Error("Failed to get reader from response")
        }

        // Process the stream
        let results: any[] = []
        let decoder = new TextDecoder()
        let buffer = ""

        while (true) {
          const { done, value } = await reader.read()

          if (done) {
            // Process any remaining buffer
            if (buffer) {
              setLogs(prev => [...prev, buffer])
            }
            break
          }

          // Decode the chunk and add it to the buffer
          const chunk = decoder.decode(value, { stream: true })
          buffer += chunk

          // Process complete lines
          const lines = buffer.split("\n")
          buffer = lines.pop() || "" // Keep the last incomplete line in the buffer

          for (const line of lines) {
            // Check if this is the results line
            if (line.startsWith("RESULTS:")) {
              try {
                results = JSON.parse(line.substring(8))
                setLogs(prev => [...prev, "Received search results"])
              } catch (e) {
                setLogs(prev => [...prev, `ERROR: Failed to parse results: ${e}`])
              }
            } else if (line.trim()) {
              // Add the line to logs
              setLogs(prev => [...prev, line])
            }
          }
        }

        setIsStreaming(false)

        // Create a search params object with the results
        const searchParams: SearchParams = {
          activeIngredients: filteredIngredients,
          databaseUrls: [],  // Not needed for batch search
          fromDate: fromDate || null,
          toDate: toDate || null,
          additionalFilters: {
            batchSearchResults: results,
            isBatchSearch: true,
          },
        }

        onSubmit(searchParams)
      } catch (error) {
        console.error("Batch search error:", error)
        setLogs(prev => [...prev, `ERROR: ${error instanceof Error ? error.message : "Unknown error"}`])
        setIsStreaming(false)
      }

      return
    }

    // Regular search - convert selected database IDs to URLs
    const databaseUrls = selectedDatabases
      .map((id) => {
        const database = defaultDatabases.find((db) => db.id === id)
        return database?.url || ""
      })
      .filter((url) => url !== "")

    // Add a warning if too many databases are selected
    if (selectedDatabases.length > 20) {
      const confirmSearch = window.confirm(
        `You have selected ${selectedDatabases.length} databases. Searching across many databases may take longer. Do you want to continue?`,
      )
      if (!confirmSearch) {
        return
      }
    }

    const searchParams: SearchParams = {
      activeIngredients: filteredIngredients,
      databaseUrls,
      fromDate: fromDate || null,
      toDate: toDate || null,
      additionalFilters: {},
    }

    onSubmit(searchParams)
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Search Medical Databases</h2>

      <form onSubmit={handleSubmit}>
        {/* Active Ingredients */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Active Ingredient(s)</label>

          {activeIngredients.map((ingredient, index) => (
            <div key={index} className="flex mb-2">
              <input
                type="text"
                value={ingredient}
                onChange={(e) => handleIngredientChange(index, e.target.value)}
                placeholder="Enter active ingredient (e.g., Methotrexate)"
                className="flex-grow px-4 py-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required={index === 0}
              />

              <button
                type="button"
                onClick={() => handleRemoveActiveIngredient(index)}
                disabled={activeIngredients.length === 1 && index === 0}
                className={`px-3 py-2 bg-red-50 border border-l-0 border-red-300 ${
                  activeIngredients.length === 1 && index === 0
                    ? "text-gray-400 cursor-not-allowed"
                    : "text-red-600 hover:bg-red-100"
                }`}
              >
                <MinusCircle size={18} />
              </button>

              {index === activeIngredients.length - 1 && (
                <button
                  type="button"
                  onClick={handleAddActiveIngredient}
                  className="px-3 py-2 bg-blue-50 border border-l-0 border-blue-300 text-blue-600 hover:bg-blue-100 rounded-r-md"
                >
                  <PlusCircle size={18} />
                </button>
              )}
            </div>
          ))}

          <p className="text-xs text-gray-500 mt-1">
            Enter one or more active ingredients to search for. Add multiple ingredients to search for any of them.
          </p>
        </div>

        {/* Database Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Select Databases to Search</label>

          <div className="mb-3">
            <input
              type="text"
              placeholder="Filter databases..."
              value={databaseFilter}
              onChange={(e) => setDatabaseFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            {databaseFilter && (
              <button
                type="button"
                onClick={() => setDatabaseFilter("")}
                className="absolute right-10 mt-2 text-gray-400 hover:text-gray-600"
              >
                <X size={16} />
              </button>
            )}
          </div>

          <div className="mb-2 text-sm text-gray-600">
            {selectedDatabases.length} of {defaultDatabases.length} databases selected
          </div>

          <div className="max-h-80 overflow-y-auto border border-gray-200 rounded-md p-2">
            {Object.entries(getDatabaseCategories()).map(([category, databases]) => {
              // Skip categories with no matches when filtering
              if (
                databaseFilter &&
                !databases.some(
                  (db) =>
                    db.name.toLowerCase().includes(databaseFilter.toLowerCase()) ||
                    db.description.toLowerCase().includes(databaseFilter.toLowerCase()),
                )
              ) {
                return null
              }

              const isExpanded = expandedCategories.includes(category)
              const filteredDatabases = databaseFilter
                ? databases.filter(
                    (db) =>
                      db.name.toLowerCase().includes(databaseFilter.toLowerCase()) ||
                      db.description.toLowerCase().includes(databaseFilter.toLowerCase()),
                  )
                : databases

              if (filteredDatabases.length === 0) return null

              const allSelected = filteredDatabases.every((db) => selectedDatabases.includes(db.id))

              return (
                <div key={category} className="mb-3">
                  <div
                    className="flex items-center justify-between bg-gray-100 p-2 rounded cursor-pointer"
                    onClick={() => toggleCategory(category)}
                  >
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        checked={allSelected}
                        onChange={() => selectAllInCategory(category, filteredDatabases)}
                        onClick={(e) => e.stopPropagation()}
                        className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 mr-2"
                      />
                      <span className="font-medium">
                        {category} ({filteredDatabases.length})
                      </span>
                    </div>
                    <span>{isExpanded ? "▼" : "►"}</span>
                  </div>

                  {isExpanded && (
                    <div className="pl-4 mt-1 space-y-1">
                      {filteredDatabases.map((database) => (
                        <div key={database.id} className="flex items-start py-1">
                          <input
                            type="checkbox"
                            id={`db-${database.id}`}
                            checked={selectedDatabases.includes(database.id)}
                            onChange={() => handleDatabaseChange(database.id)}
                            className="mt-1 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                          <label htmlFor={`db-${database.id}`} className="ml-2 block text-sm text-gray-700">
                            <span className="font-medium">{database.name}</span>
                            <span className="block text-xs text-gray-500">{database.description}</span>
                          </label>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )
            })}
          </div>

          <div className="mt-2 flex justify-between">
            <button
              type="button"
              onClick={() => {
                // Ensure we get all database IDs without duplicates
                const allDatabaseIds = defaultDatabases.map((db) => db.id)
                setSelectedDatabases(allDatabaseIds)
              }}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Select All
            </button>
            <button
              type="button"
              onClick={() => setSelectedDatabases([])}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Clear All
            </button>
          </div>
        </div>

        {/* Date Range */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label htmlFor="fromDate" className="block text-sm font-medium text-gray-700 mb-2">
              From Date
            </label>
            <input
              type="date"
              id="fromDate"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label htmlFor="toDate" className="block text-sm font-medium text-gray-700 mb-2">
              To Date
            </label>
            <input
              type="date"
              id="toDate"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Advanced Search Options */}
        <div className="mb-6 border border-gray-200 rounded-md p-4 bg-gray-50">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Advanced Search Options</h3>

          {/* Batch Search Option */}
          <div className="flex items-center mb-3">
            <input
              type="checkbox"
              id="useBatchSearch"
              checked={useBatchSearch}
              onChange={(e) => setUseBatchSearch(e.target.checked)}
              className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="useBatchSearch" className="ml-2 flex items-center text-sm font-medium text-gray-700">
              <Zap size={16} className="mr-1 text-yellow-500" />
              Use Batch Search (Fetch data from all selected databases at once)
            </label>
          </div>

          {/* Commercial Databases Option */}
          <div className="flex items-center mb-3">
            <input
              type="checkbox"
              id="useCommercialDatabases"
              checked={useCommercialDatabases}
              onChange={(e) => setUseCommercialDatabases(e.target.checked)}
              className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="useCommercialDatabases" className="ml-2 flex items-center text-sm font-medium text-gray-700">
              <DatabaseIcon size={16} className="mr-1 text-purple-500" />
              Include Commercial Databases (DrugBank, RxNav, ChEMBL)
            </label>
          </div>

          {/* CAPTCHA Solver Option */}
          <div className="flex items-center mb-3">
            <input
              type="checkbox"
              id="useCaptchaSolver"
              checked={useCaptchaSolver}
              onChange={(e) => setUseCaptchaSolver(e.target.checked)}
              className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="useCaptchaSolver" className="ml-2 flex items-center text-sm font-medium text-gray-700">
              <img src="/captcha-icon.svg" alt="CAPTCHA" className="w-4 h-4 mr-1" onError={(e) => e.currentTarget.style.display = 'none'} />
              Use CAPTCHA Solver (Helps access protected databases)
            </label>
          </div>

          {/* Browser Automation Option */}
          <div className="flex items-center mb-3">
            <input
              type="checkbox"
              id="useBrowserAutomation"
              checked={useBrowserAutomation}
              onChange={(e) => setUseBrowserAutomation(e.target.checked)}
              className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="useBrowserAutomation" className="ml-2 flex items-center text-sm font-medium text-gray-700">
              <Terminal size={16} className="mr-1 text-green-500" />
              Use Browser Automation (Human-like behavior to avoid detection)
            </label>
          </div>

          {useBatchSearch && (
            <div className="pl-6 mt-2">
              <div className="mb-2">
                <label htmlFor="batchSearchLimit" className="block text-sm font-medium text-gray-700 mb-1">
                  Database Limit (0 = no limit)
                </label>
                <input
                  type="number"
                  id="batchSearchLimit"
                  min="0"
                  max="149"
                  value={batchSearchLimit}
                  onChange={(e) => setBatchSearchLimit(parseInt(e.target.value) || 0)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Limit the number of databases to search (for faster testing). Set to 0 to search all selected databases.
                </p>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded p-3 text-sm text-yellow-800">
                <p className="flex items-center">
                  <AlertTriangle size={16} className="mr-1 flex-shrink-0" />
                  <span>
                    Batch search uses a Python script to fetch data from multiple databases at once.
                    This may take longer but provides more comprehensive results.
                  </span>
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Submit Button */}
        <div className="mt-6">
          <div className="flex justify-between items-center mb-4">
            {useBatchSearch && (
              <button
                type="button"
                onClick={() => setShowLogs(true)}
                className="flex items-center bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded-md font-medium"
              >
                <Terminal className="mr-2" size={18} />
                {logs.length > 0 ? `View Logs (${logs.length})` : "Show Logs"}
              </button>
            )}
            {!useBatchSearch && <div></div>}
          </div>

          {isLoading ? (
            <div className="flex space-x-4">
              <button
                type="button"
                onClick={onCancel}
                className="w-full py-3 px-6 flex items-center justify-center rounded-md text-white font-medium bg-red-600 hover:bg-red-700 transition-colors"
              >
                <X size={18} className="mr-2" />
                Cancel Search
              </button>
              <div className="w-full py-3 px-6 flex items-center justify-center rounded-md text-white font-medium bg-blue-400">
                <svg
                  className="animate-spin -ml-1 mr-2 h-5 w-5 text-white"
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
                {isStreaming ? "Processing..." : "Searching..."}
              </div>
            </div>
          ) : (
            <button
              type="submit"
              className="w-full py-3 px-6 flex items-center justify-center rounded-md text-white font-medium bg-blue-600 hover:bg-blue-700 transition-colors"
            >
              <Search size={18} className="mr-2" />
              Search Databases
            </button>
          )}
        </div>

        {/* Logs Modal */}
        <SearchLogs
          logs={logs}
          isVisible={showLogs}
          onClose={() => setShowLogs(false)}
        />
      </form>
    </div>
  )
}
