import axios, { AxiosInstance } from 'axios'

/**
 * API client configuration for news-feed-engine backend
 * Handles authentication, rate limiting, and error handling
 */

interface APIConfig {
  baseURL: string
  timeout: number
  retries: number
}

/**
 * Initialize API client with base configuration
 * @param config API configuration options
 * @returns Configured axios instance
 * @example
 * ```tsx
 * const api = createAPIClient({ baseURL: 'http://localhost:8080' })
 * const data = await api.get('/feed')
 * ```
 */
export function createAPIClient(config: Partial<APIConfig> = {}): AxiosInstance {
  const defaultConfig: APIConfig = {
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8082',
    timeout: 10000,
    retries: 3,
  }

  const finalConfig = { ...defaultConfig, ...config }

  const instance = axios.create({
    baseURL: finalConfig.baseURL,
    timeout: finalConfig.timeout,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  // Request interceptor - add auth token
  instance.interceptors.request.use((config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  })

  // Response interceptor - handle retries & errors
  instance.interceptors.response.use(
    (response) => response,
    async (error) => {
      const config = error.config as any

      // Retry logic
      config.retryCount = config.retryCount || 0
      if (config.retryCount < finalConfig.retries && error.response?.status === 429) {
        config.retryCount++
        const delay = Math.pow(2, config.retryCount) * 1000
        return new Promise((resolve) => {
          setTimeout(() => resolve(instance(config)), delay)
        })
      }

      return Promise.reject(error)
    },
  )

  return instance
}

/**
 * Health check endpoint
 * @param api API client instance
 * @returns Health status
 */
export async function checkHealth(api: AxiosInstance): Promise<boolean> {
  try {
    const response = await api.get('/health')
    return response.status === 200
  } catch {
    return false
  }
}

/**
 * Fetch feed data
 * @param api API client instance
 * @param params Query parameters
 * @returns Feed data
 */
export async function fetchFeed(
  api: AxiosInstance,
  params?: Record<string, unknown>,
): Promise<unknown> {
  const response = await api.get('/feed', { params })
  return response.data
}

/**
 * Fetch analytics data
 * @param api API client instance
 * @returns Analytics metrics
 */
export async function fetchAnalytics(api: AxiosInstance): Promise<unknown> {
  const response = await api.get('/analytics')
  return response.data
}
