// API configuration for regulatory databases

export interface ApiConfig {
  baseUrl: string
  apiKey?: string
  requiresAuth: boolean
  authType?: "apiKey" | "oauth" | "basic"
  headers?: Record<string, string>
  searchEndpoint: string
  searchMethod: "GET" | "POST"
  responseType: "json" | "xml" | "html"
  rateLimitPerMinute?: number
  parser: (data: any, query: string) => any
}

// Configuration for databases with available APIs
export const apiConfigurations: Record<string, ApiConfig> = {
  // FDA API
  "fda-drugs": {
    baseUrl: "https://api.fda.gov",
    requiresAuth: false,
    searchEndpoint: "/drug/label.json",
    searchMethod: "GET",
    responseType: "json",
    rateLimitPerMinute: 240, // FDA API limit
    parser: (data, query) => {
      if (!data.results) return []

      return data.results.map((result: any) => ({
        id: result.id || result.openfda?.application_number?.[0] || `fda-${Math.random().toString(36).substring(7)}`,
        title: result.openfda?.brand_name?.[0] || result.openfda?.generic_name?.[0] || "Unnamed Drug",
        url: `https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process&ApplNo=${result.openfda?.application_number?.[0] || ""}`,
        source: "FDA",
        date: result.effective_time || new Date().toISOString().split("T")[0],
        snippet: result.description || result.indications_and_usage?.[0] || "No description available",
        authors: result.openfda?.manufacturer_name || [],
        relevanceScore: 1,
      }))
    },
  },

  // PubMed API (via NCBI E-utilities)
  pubmed: {
    baseUrl: "https://eutils.ncbi.nlm.nih.gov",
    requiresAuth: false,
    searchEndpoint: "/entrez/eutils/esearch.fcgi",
    searchMethod: "GET",
    responseType: "xml",
    rateLimitPerMinute: 10, // Be conservative with NCBI
    parser: (data, query) => {
      // This is a simplified parser - in reality you'd need to parse XML
      // and make a second request to fetch details
      if (!data.ids) return []

      return data.ids.map((id: string) => ({
        id: id,
        title: `PubMed Article ${id}`,
        url: `https://pubmed.ncbi.nlm.nih.gov/${id}/`,
        source: "PubMed",
        date: new Date().toISOString().split("T")[0],
        snippet: `Article related to search term: ${query}`,
        authors: [],
        relevanceScore: 1,
      }))
    },
  },

  // EMA (European Medicines Agency)
  "ema-medicines": {
    baseUrl: "https://www.ema.europa.eu",
    requiresAuth: false,
    searchEndpoint: "/en/medicines/api/medicines",
    searchMethod: "GET",
    responseType: "json",
    parser: (data, query) => {
      if (!data.medicines) return []

      return data.medicines.map((med: any) => ({
        id: med.medicine_id || `ema-${Math.random().toString(36).substring(7)}`,
        title: med.medicine_name || "Unnamed Medicine",
        url: `https://www.ema.europa.eu/en/medicines/human/${med.category}/${med.medicine_id}`,
        source: "EMA",
        date: med.authorization_date || new Date().toISOString().split("T")[0],
        snippet:
          med.therapeutic_areas?.join(", ") || med.international_non_proprietary_name || "No description available",
        authors: [med.marketing_authorization_holder || "Unknown manufacturer"],
        relevanceScore: 1,
      }))
    },
  },

  // WHO API
  "who-iris": {
    baseUrl: "https://apps.who.int",
    requiresAuth: false,
    searchEndpoint: "/iris/rest/search",
    searchMethod: "GET",
    responseType: "json",
    parser: (data, query) => {
      if (!data.items) return []

      return data.items.map((item: any) => ({
        id: item.id || `who-${Math.random().toString(36).substring(7)}`,
        title: item.title || "Unnamed Document",
        url: item.handle || `https://iris.who.int/handle/${item.id}`,
        source: "WHO IRIS",
        date: item.issued || new Date().toISOString().split("T")[0],
        snippet: item.abstract || "No abstract available",
        authors: item.authors || [],
        relevanceScore: 1,
      }))
    },
  },

  // Health Canada Drug Product Database API
  "canada-drug-db": {
    baseUrl: "https://health-products.canada.ca",
    requiresAuth: false,
    searchEndpoint: "/api/drug/drugproduct",
    searchMethod: "GET",
    responseType: "json",
    parser: (data, query) => {
      if (!data.data) return []

      return data.data.map((product: any) => ({
        id: product.drug_identification_number || `hc-${Math.random().toString(36).substring(7)}`,
        title: product.brand_name || "Unnamed Product",
        url: `https://health-products.canada.ca/dpd-bdpp/info.do?lang=en&code=${product.drug_identification_number}`,
        source: "Health Canada",
        date: product.last_update || new Date().toISOString().split("T")[0],
        snippet: `${product.company_name}: ${product.descriptor || product.class_name || ""}`,
        authors: [product.company_name || "Unknown manufacturer"],
        relevanceScore: 1,
      }))
    },
  },
}

// For databases without APIs, we'll need to use a server-side proxy
export const proxyEndpoint = "/api/proxy-search"
