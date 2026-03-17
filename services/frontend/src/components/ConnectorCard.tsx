import React from 'react'
import type { ConnectorConfig } from '../types/connectors'

interface ConnectorCardProps {
  connector: ConnectorConfig
  onConnect: (id: string) => Promise<void>
  onDisconnect: (id: string) => Promise<void>
  onSelect: (connector: ConnectorConfig) => void
  isLoading?: boolean
}

/**
 * Connector card component showing status and quick actions
 *
 * Displays a social media platform connector with connection status,
 * follower count, and action buttons to connect/disconnect.
 *
 * @param {ConnectorCardProps} props - Component props
 * @returns {React.ReactElement} Connector card element
 *
 * @example
 * ```tsx
 * <ConnectorCard
 *   connector={instagramConnector}
 *   onConnect={handleConnect}
 *   onDisconnect={handleDisconnect}
 *   onSelect={handleSelect}
 *   isLoading={isLoading}
 * />
 * ```
 */
export function ConnectorCard({
  connector,
  onConnect,
  onDisconnect,
  onSelect,
  isLoading = false,
}: ConnectorCardProps): React.ReactElement {
  const [isLoadingLocal, setIsLoadingLocal] = React.useState(false)
  const isButtonLoading = isLoading || isLoadingLocal

  const handleConnect = async (e: React.MouseEvent) => {
    e.stopPropagation()
    setIsLoadingLocal(true)
    try {
      await onConnect(connector.id)
    } catch (error) {
      console.error('Failed to connect:', error)
    } finally {
      setIsLoadingLocal(false)
    }
  }

  const handleDisconnect = async (e: React.MouseEvent) => {
    e.stopPropagation()
    setIsLoadingLocal(true)
    try {
      await onDisconnect(connector.id)
    } catch (error) {
      console.error('Failed to disconnect:', error)
    } finally {
      setIsLoadingLocal(false)
    }
  }

  const statusColor = {
    connected: 'text-green-500',
    disconnected: 'text-slate-500',
    error: 'text-orange-500',
    pending: 'text-blue-500',
  }

  const statusBg = {
    connected: 'bg-green-500/10',
    disconnected: 'bg-slate-500/10',
    error: 'bg-orange-500/10',
    pending: 'bg-blue-500/10',
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 hover:border-slate-700 transition-all cursor-pointer" onClick={() => onSelect(connector)}>
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <span className="text-2xl">{connector.icon}</span>
            <h3 className="text-lg font-bold text-white">{connector.name}</h3>
          </div>
          <p className="text-sm text-slate-400">{connector.handle || 'Not connected'}</p>
        </div>
        <div className={`px-3 py-1 rounded-full text-xs font-semibold ${statusBg[connector.status]}`}>
          <span className={statusColor[connector.status]}>
            {connector.status.charAt(0).toUpperCase() + connector.status.slice(1)}
          </span>
        </div>
      </div>

      {connector.status === 'connected' && (
        <div className="mb-4 space-y-1 text-sm">
          {connector.followerCount && (
            <p className="text-slate-400">
              <strong className="text-slate-300">{connector.followerCount.toLocaleString()}</strong> followers
            </p>
          )}
          {connector.lastSync && (
            <p className="text-slate-400">
              Last synced: <strong className="text-slate-300">{new Date(connector.lastSync).toLocaleDateString()}</strong>
            </p>
          )}
        </div>
      )}

      {connector.error && (
        <div className="mb-4 p-2 bg-orange-500/10 border border-orange-500/30 rounded text-sm text-orange-400">
          {connector.error}
        </div>
      )}

      <div className="flex gap-2">
        {connector.status === 'connected' ? (
          <>
            <button
              onClick={handleDisconnect}
              disabled={isButtonLoading}
              className="flex-1 px-3 py-2 bg-red-500/10 border border-red-500/30 text-red-400 rounded text-sm font-medium hover:bg-red-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
            >
              {isButtonLoading ? (
                <>
                  <div className="w-3 h-3 rounded-full border border-red-400/30 border-t-red-400 animate-spin" />
                  Disconnecting...
                </>
              ) : (
                'Disconnect'
              )}
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation()
                onSelect(connector)
              }}
              className="flex-1 px-3 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded text-sm font-medium transition-colors"
            >
              Settings
            </button>
          </>
        ) : (
          <button
            onClick={handleConnect}
            disabled={isButtonLoading}
            className="flex-1 px-3 py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded text-sm font-medium transition-colors flex items-center justify-center gap-2"
          >
            {isButtonLoading ? (
              <>
                <div className="w-3 h-3 rounded-full border border-white/30 border-t-white animate-spin" />
                Connecting...
              </>
            ) : (
              'Connect'
            )}
          </button>
        )}
      </div>
    </div>
  )
}
