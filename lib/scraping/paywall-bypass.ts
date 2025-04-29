/**
 * MedSearch Paywall Bypass Utilities
 * 
 * This module provides utilities for accessing content behind paywalls
 * by finding open-access alternatives or using legal methods.
 */

import { fetchWithRetry } from './retry-utils';

/**
 * Sources for finding open-access versions of paywalled content
 */
export enum OpenAccessSource {
  PUBMED_CENTRAL = 'PubMed Central',
  ARXIV = 'arXiv',
  BIORXIV = 'bioRxiv',
  MEDRXIV = 'medRxiv',
  UNPAYWALL = 'Unpaywall',
  CORE = 'CORE',
  DOAJ = 'Directory of Open Access Journals'
}

/**
 * Configuration for open access search
 */
export interface OpenAccessConfig {
  sources: OpenAccessSource[];
  timeout: number;
  maxResults: number;
}

// Default configuration
export const defaultOpenAccessConfig: OpenAccessConfig = {
  sources: [
    OpenAccessSource.PUBMED_CENTRAL,
    OpenAccessSource.ARXIV,
    OpenAccessSource.BIORXIV,
    OpenAccessSource.MEDRXIV,
    OpenAccessSource.UNPAYWALL
  ],
  timeout: 30000, // 30 seconds
  maxResults: 5
};

/**
 * Result from searching for open access alternatives
 */
export interface OpenAccessResult {
  url: string;
  source: OpenAccessSource;
  title: string;
  confidence: number; // 0-1 score of how likely this is the correct paper
}

/**
 * Check if a URL is likely behind a paywall
 */
export function isLikelyPaywalled(url: string): boolean {
  const paywallDomains = [
    'nature.com',
    'sciencedirect.com',
    'springer.com',
    'wiley.com',
    'tandfonline.com',
    'elsevier.com',
    'bmj.com',
    'nejm.org',
    'jama.com',
    'oup.com',
    'sagepub.com'
  ];
  
  return paywallDomains.some(domain => url.includes(domain));
}

/**
 * Find open access alternatives for a paywalled article
 * @param doi DOI of the article
 * @param title Title of the article
 * @param authors Authors of the article
 * @param config Configuration options
 */
export async function findOpenAccessAlternatives(
  doi: string | null,
  title: string,
  authors: string[] = [],
  config: Partial<OpenAccessConfig> = {}
): Promise<OpenAccessResult[]> {
  const fullConfig = { ...defaultOpenAccessConfig, ...config };
  const results: OpenAccessResult[] = [];
  
  // Search PubMed Central if enabled
  if (fullConfig.sources.includes(OpenAccessSource.PUBMED_CENTRAL) && doi) {
    try {
      const pmcResults = await searchPubMedCentral(doi, title);
      results.push(...pmcResults);
    } catch (error) {
      console.error('Error searching PubMed Central:', error);
    }
  }
  
  // Search Unpaywall if enabled
  if (fullConfig.sources.includes(OpenAccessSource.UNPAYWALL) && doi) {
    try {
      const unpaywallResults = await searchUnpaywall(doi);
      results.push(...unpaywallResults);
    } catch (error) {
      console.error('Error searching Unpaywall:', error);
    }
  }
  
  // Search preprint servers if enabled
  if (fullConfig.sources.some(source => [
    OpenAccessSource.ARXIV,
    OpenAccessSource.BIORXIV,
    OpenAccessSource.MEDRXIV
  ].includes(source))) {
    try {
      const preprintResults = await searchPreprints(title, authors);
      results.push(...preprintResults);
    } catch (error) {
      console.error('Error searching preprint servers:', error);
    }
  }
  
  // Sort by confidence and limit results
  return results
    .sort((a, b) => b.confidence - a.confidence)
    .slice(0, fullConfig.maxResults);
}

/**
 * Search PubMed Central for open access version
 */
async function searchPubMedCentral(doi: string, title: string): Promise<OpenAccessResult[]> {
  // In a real implementation, this would query the PubMed Central API
  // This is a simplified placeholder
  console.log(`Searching PubMed Central for DOI: ${doi}`);
  
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Return empty array for now - in real implementation would return actual results
  return [];
}

/**
 * Search Unpaywall for open access version
 */
async function searchUnpaywall(doi: string): Promise<OpenAccessResult[]> {
  try {
    const response = await fetchWithRetry(
      `https://api.unpaywall.org/v2/${encodeURIComponent(doi)}?email=medsearch@example.com`
    );
    
    const data = await response.json();
    
    if (data.is_oa && data.best_oa_location && data.best_oa_location.url) {
      return [{
        url: data.best_oa_location.url,
        source: OpenAccessSource.UNPAYWALL,
        title: data.title || 'Unknown Title',
        confidence: 0.9
      }];
    }
    
    return [];
  } catch (error) {
    console.error('Error querying Unpaywall:', error);
    return [];
  }
}

/**
 * Search preprint servers for similar papers
 */
async function searchPreprints(title: string, authors: string[]): Promise<OpenAccessResult[]> {
  // In a real implementation, this would query arXiv, bioRxiv, and medRxiv APIs
  // This is a simplified placeholder
  console.log(`Searching preprint servers for: ${title}`);
  
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 700));
  
  // Return empty array for now - in real implementation would return actual results
  return [];
}