/**
 * MedSearch Enhanced Retry Utilities
 * 
 * This module provides improved retry mechanisms with exponential backoff
 * and jitter for handling temporary website unavailability.
 */

/**
 * Configuration options for retry mechanism
 */
export interface RetryConfig {
  maxRetries: number;
  initialDelayMs: number;
  maxDelayMs: number;
  backoffFactor: number;
  jitterFactor: number;
}

// Default retry configuration
export const defaultRetryConfig: RetryConfig = {
  maxRetries: 3,
  initialDelayMs: 1000, // 1 second
  maxDelayMs: 30000, // 30 seconds
  backoffFactor: 2,
  jitterFactor: 0.25
};

/**
 * Adds random jitter to a delay value to prevent thundering herd problem
 * @param delay Base delay in milliseconds
 * @param jitterFactor Amount of randomness (0-1)
 */
function addJitter(delay: number, jitterFactor: number): number {
  const jitterAmount = delay * jitterFactor;
  return delay + (Math.random() * jitterAmount * 2) - jitterAmount;
}

/**
 * Calculate delay for the next retry attempt with exponential backoff and jitter
 * @param attempt Current attempt number (0-based)
 * @param config Retry configuration
 */
export function calculateBackoffDelay(attempt: number, config: RetryConfig = defaultRetryConfig): number {
  const { initialDelayMs, maxDelayMs, backoffFactor, jitterFactor } = config;
  
  // Calculate exponential backoff
  const exponentialDelay = initialDelayMs * Math.pow(backoffFactor, attempt);
  
  // Cap at maximum delay
  const cappedDelay = Math.min(exponentialDelay, maxDelayMs);
  
  // Add jitter
  return addJitter(cappedDelay, jitterFactor);
}

/**
 * Execute a function with retry logic using exponential backoff
 * @param fn The async function to execute
 * @param config Retry configuration
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  config: Partial<RetryConfig> = {}
): Promise<T> {
  const fullConfig: RetryConfig = { ...defaultRetryConfig, ...config };
  const { maxRetries } = fullConfig;
  
  let lastError: Error | null = null;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      // Execute the function
      return await fn();
    } catch (error) {
      lastError = error as Error;
      
      // If this was the last attempt, don't wait
      if (attempt >= maxRetries) {
        break;
      }
      
      // Calculate delay with exponential backoff and jitter
      const delay = calculateBackoffDelay(attempt, fullConfig);
      
      // Log retry attempt
      console.log(`Attempt ${attempt + 1} failed, retrying in ${Math.round(delay / 1000)}s...`);
      
      // Wait before next attempt
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  // If we get here, all retries failed
  throw new Error(`All ${maxRetries + 1} attempts failed. Last error: ${lastError?.message}`);
}

/**
 * Fetch with retry mechanism
 * @param url URL to fetch
 * @param options Fetch options
 * @param retryConfig Retry configuration
 */
export async function fetchWithRetry(
  url: string,
  options: RequestInit = {},
  retryConfig: Partial<RetryConfig> = {}
): Promise<Response> {
  return withRetry(
    async () => {
      const response = await fetch(url, options);
      
      // Throw error for non-2xx responses to trigger retry
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
      }
      
      return response;
    },
    retryConfig
  );
}