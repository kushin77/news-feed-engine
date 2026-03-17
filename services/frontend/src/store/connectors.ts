import { create } from 'zustand'
import type { ConnectorConfig, ConnectorStatus } from '../types/connectors'
import * as connectorAPI from '../services/connectors'

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
 * Calls the connector API service which provides:
 * - Mock implementations for development
 * - Easy transition to real API endpoints when backend is ready
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
   * FLOW:
   * 1. Call connectorAPI.initiateConnectorAuth(id) to get OAuth URL + state
   * 2. Open OAuth URL in new window/popup (user authorizes with provider)
   * 3. Provider redirects to /auth/callback?code=...&state=...
   * 4. Frontend captures code + state, calls connectorAPI.completeConnectorAuth(id, code, state)
   * 5. Backend exchanges code for token, returns connector with credentials
   * 6. Store updates connector status to "connected"
   */
  connectPlatform: async (id: string) => {
    set({ loadingConnectorId: id, error: null })
    try {
      // Step 1: Initiate OAuth flow (get auth URL from backend)
      const authResult = await connectorAPI.initiateConnectorAuth(id)

      // TODO: Step 2: Open OAuth URL in popup
      // window.open(authResult.authUrl, 'oauth', 'width=500,height=600')
      // User authorizes on provider side

      // Step 3-4: Simulate OAuth callback (in production, this happens after user auth)
      // For now, complete the flow immediately with mock code/state
      const connectedConnector = await connectorAPI.completeConnectorAuth(id, 'mock_auth_code', authResult.state)

      // Step 5: Update store with connected connector
      set((state) => ({
        connectors: state.connectors.map((c) => (c.id === id ? connectedConnector : c)),
        loadingConnectorId: null,
      }))
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to connect platform'
      set({
        loadingConnectorId: null,
        error: message,
      })
      console.error(`[Store] connectPlatform error for ${id}:`, message)
      throw error
    }
  },

  /**
   * Disconnect a social media platform
   * @param id Connector ID to disconnect
   * @throws Error if disconnection fails
   *
   * FLOW:
   * 1. Call connectorAPI.disconnectConnector(id)
   * 2. Backend revokes stored credentials/tokens
   * 3. Frontend resets connector to "disconnected" state
   */
  disconnectPlatform: async (id: string) => {
    set({ loadingConnectorId: id, error: null })
    try {
      // Call API to disconnect (backend revokes tokens)
      await connectorAPI.disconnectConnector(id)

      // Reset connector state in store
      set((state) => ({
        connectors: state.connectors.map((c) =>
          c.id === id
            ? {
                ...c,
                status: 'disconnected',
                handle: undefined,
                followerCount: undefined,
                lastSync: undefined,
                error: undefined,
              }
            : c,
        ),
        loadingConnectorId: null,
      }))
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to disconnect platform'
      set({
        loadingConnectorId: null,
        error: message,
      })
      console.error(`[Store] disconnectPlatform error for ${id}:`, message)
      throw error
    }
  },

  setError: (error) => set({ error }),

  setLoading: (loading) => set({ isLoading: loading }),
}))
