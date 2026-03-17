import { create } from 'zustand'
import type { ConnectorConfig, ConnectorStatus } from '../types/connectors'

/**
 * Connector store state interface
 */
interface ConnectorState {
  connectors: ConnectorConfig[]
  selectedConnector: ConnectorConfig | null
  isLoading: boolean
  error: string | null
  loadingConnectorId: string | null

  // Actions
  setConnectors: (connectors: ConnectorConfig[]) => void
  selectConnector: (connector: ConnectorConfig | null) => void
  updateConnectorStatus: (id: string, status: ConnectorStatus) => void
  connectPlatform: (id: string) => Promise<void>
  disconnectPlatform: (id: string) => Promise<void>
  setError: (error: string | null) => void
  setLoading: (loading: boolean) => void
}

/**
 * Zustand store for managing social media connectors
 *
 * Manages the state of all connected social media platforms.
 * Currently uses simulated API calls; replace TODO sections with real API integration.
 */
export const useConnectorStore = create<ConnectorState>((set) => ({
  connectors: [],
  selectedConnector: null,
  isLoading: false,
  error: null,
  loadingConnectorId: null,

  setConnectors: (connectors) => set({ connectors }),

  selectConnector: (connector) => set({ selectedConnector: connector }),

  updateConnectorStatus: (id, status) =>
    set((state) => ({
      connectors: state.connectors.map((c) => (c.id === id ? { ...c, status } : c)),
    })),

  /**
   * Connect a social media platform via OAuth
   * @param id Connector ID to connect
   * @throws Error if connection fails
   *
   * TODO: Replace simulated delay with actual OAuth flow:
   * 1. POST /api/v1/connectors/{id}/auth to get OAuth URL
   * 2. Redirect to provider authorization
   * 3. Handle callback at /auth/callback
   * 4. Exchange code for token
   * 5. Store credentials securely
   */
  connectPlatform: async (id: string) => {
    set({ loadingConnectorId: id, error: null })
    try {
      // Simulate OAuth flow delay (replace with real API call)
      await new Promise((resolve) => setTimeout(resolve, 1500))

      // Mock: Generate fake follower count
      const followers = Math.floor(Math.random() * 100000) + 1000
      const lastSync = new Date()

      set((state) => ({
        connectors: state.connectors.map((c) =>
          c.id === id
            ? {
                ...c,
                status: 'connected',
                handle: `@user_${id.slice(0, 8)}`,
                followerCount: followers,
                lastSync,
                error: undefined,
              }
            : c,
        ),
        loadingConnectorId: null,
      }))
    } catch (error) {
      set({
        loadingConnectorId: null,
        error: error instanceof Error ? error.message : 'Failed to connect platform',
      })
      throw error
    }
  },

  /**
   * Disconnect a social media platform
   * @param id Connector ID to disconnect
   * @throws Error if disconnection fails
   *
   * TODO: Replace simulated delay with actual API call:
   * DELETE /api/v1/connectors/{id}
   */
  disconnectPlatform: async (id: string) => {
    set({ loadingConnectorId: id, error: null })
    try {
      // Simulate API delay (replace with real DELETE /api/v1/connectors/{id})
      await new Promise((resolve) => setTimeout(resolve, 800))

      set((state) => ({
        connectors: state.connectors.map((c) =>
          c.id === id
            ? {
                ...c,
                status: 'disconnected',
                handle: '',
                followerCount: 0,
                lastSync: undefined,
                error: undefined,
              }
            : c,
        ),
        loadingConnectorId: null,
      }))
    } catch (error) {
      set({
        loadingConnectorId: null,
        error: error instanceof Error ? error.message : 'Failed to disconnect platform',
      })
      throw error
    }
  },

  setError: (error) => set({ error }),

  setLoading: (loading) => set({ isLoading: loading }),
}))
