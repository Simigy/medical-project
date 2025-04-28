export interface Database {
  id: string
  name: string
  url: string
  description: string
  logo?: string
}

export interface SearchParams {
  activeIngredients: string[]
  databaseUrls: string[]
  fromDate: string | null
  toDate: string | null
  additionalFilters: Record<string, any>
}

export interface SearchResult {
  id: string
  title: string
  url: string
  source: string
  date: string
  snippet: string
  authors: string[]
  relevanceScore?: number
  isError?: boolean // Flag to indicate if this is an error result
}

export interface ApiError {
  message: string
  code?: string
  status?: number
}
