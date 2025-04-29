/**
 * MedSearch API Integration Utilities
 * 
 * This module provides utilities for integrating with official APIs
 * of medical databases when available, to be used instead of scraping.
 */

import { apiConfigurations } from '../api/api-config';
import type { SearchResult } from '@/types';

/**
 * Check if a database has an official API available
 */
export function hasOfficialApi(databaseId: string): boolean {
  return !!apiConfigurations[databaseId];
}

/**
 * Get the API configuration for a specific database
 */
export function getApiConfig(databaseId: string) {
  return apiConfigurations[databaseId];
}

/**
 * Search using the official API for a database
 */
export async function searchWithOfficialApi(
  databaseId: string,
  query: string,
  options: { signal?: AbortSignal } = {}
): Promise<SearchResult[]> {
  const config = apiConfigurations[databaseId];
  
  if (!config) {
    throw new Error(`No API configuration available for database: ${databaseId}`);
  }
  
  try {
    const searchParams = new URLSearchParams();
    
    // Add query parameter based on the database
    if (databaseId === 'fda-drugs') {
      searchParams.append('search', `openfda.brand_name:"${query}" openfda.generic_name:"${query}"`);
      searchParams.append('limit', '10');
    } else if (databaseId === 'pubmed') {
      searchParams.append('term', query);
      searchParams.append('retmax', '10');
      searchParams.append('retmode', 'json');
    } else {
      searchParams.append('q', query);
    }
    
    // Add API key if required
    if (config.apiKey) {
      searchParams.append('api_key', config.apiKey);
    }
    
    const url = `${config.baseUrl}${config.searchEndpoint}?${searchParams.toString()}`;
    
    const response = await fetch(url, {
      method: config.searchMethod,
      headers: config.headers || {},
      signal: options.signal,
    });
    
    if (!response.ok) {
      throw new Error(`API request failed with status: ${response.status}`);
    }
    
    let data;
    if (config.responseType === 'json') {
      data = await response.json();
    } else if (config.responseType === 'xml') {
      const text = await response.text();
      // In a real implementation, you would parse XML here
      data = { text, ids: [] };
    } else {
      data = await response.text();
    }
    
    // Parse the response using the database-specific parser
    return config.parser(data, query);
  } catch (error) {
    console.error(`Error searching ${databaseId} API:`, error);
    throw error;
  }
}

/**
 * Determine whether to use the official API or fall back to scraping
 */
export function shouldUseOfficialApi(databaseId: string): boolean {
  // Always prefer official APIs when available
  return hasOfficialApi(databaseId);
}