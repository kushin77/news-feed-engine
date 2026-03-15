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

  // Actions
  setConnectors: (connectors: ConnectorConfig[]) => void
  selectConnector: (connector: ConnectorConfig | null) => void
  updateConnectorStatus: (id: string, status: ConnectorStatus) => void
  connectPlatform: (platform: string) => Promise<void>
  disconnectPlatform: (id: string) => Promise<void>
  setError: (error: string | null) => void
  setLoading: (loading: boolean) => void
}

/**
 * Zustand store for managing social media connectors
 */
export const useConnectorStore = create<ConnectorState>((set, _get) => ({
  connectors: [],
  selectedConnector: null,
  isLoading: false,
  error: null,

  setConnectors: (connectors) => set({ connectors }),

  selectConnector: (connector) => set({ selectedConnector: connector }),

  updateConnectorStatus: (id, status) =>
    set((state) => ({
      connectors: state.connectors.map((c) => (c.id === id ? { ...c, status } : c)),
    })),

  connectPlatform: async (_platform) => {
    set({ isLoading: true, error: null })
    try {
      // TODO: Call API to initiate OAuth flow
      // const result = await apiClient.post(`/connectors/${platform}/auth`)
      set({ isLoading: false })
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to connect',
      })
    }
  },

  disconnectPlatform: async (id) => {
    set({ isLoading: true, error: null })
    try {
      // TODO: Call API to disconnect
      // await apiClient.delete(`/connectors/${id}`)
      set((state) => ({
        connectors: state.connectors.filter((c) => c.id !== id),
        isLoading: false,
      }))
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to disconnect',
      })
    }
  },

  setError: (error) => set({ error }),

  setLoading: (loading) => set({ isLoading: loading }),
}))
