import React from 'react'
import type { ConnectorConfig } from '../types/connectors'

interface ConnectorCardProps {
  connector: ConnectorConfig
  onConnect: (id: string) => void
  onDisconnect: (id: string) => void
  onSelect: (connector: ConnectorConfig) => void
}

/**
 * Connector card component showing status and quick actions
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
 * />
 * ```
 */
export function ConnectorCard({
  connector,
  onConnect,
  onDisconnect,
  onSelect,
}: ConnectorCardProps): React.ReactElement {
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
              onClick={(e) => {
                e.stopPropagation()
                onDisconnect(connector.id)
              }}
              className="flex-1 px-3 py-2 bg-red-500/10 border border-red-500/30 text-red-400 rounded text-sm font-medium hover:bg-red-500/20 transition-colors"
            >
              Disconnect
            </button>
          </>
        ) : (
          <button
            onClick={(e) => {
              e.stopPropagation()
              onConnect(connector.id)
            }}
            className="flex-1 px-3 py-2 bg-blue-500/10 border border-blue-500/30 text-blue-400 rounded text-sm font-medium hover:bg-blue-500/20 transition-colors"
          >
            Connect
          </button>
        )}
      </div>
    </div>
  )
}
