import React from 'react'
import { useEffect } from 'react'
import { Zap, Users, Share2, TrendingUp } from 'lucide-react'
import { ConnectorCard } from './ConnectorCard'
import { useConnectorStore } from '@store/connectors'
import { CONNECTOR_CAPABILITIES } from '@types/connectors'
import type { ConnectorPlatform } from '@types/connectors'

/**
 * Social Connectors Panel - Display and manage social media connections
 *
 * Shows connection status for all Tier 1 platforms (Instagram, TikTok, YouTube, X).
 * Uses Zustand for global state management of connector connections.
 *
 * @returns {React.ReactElement} Connector panel component
 *
 * @example
 * ```tsx
 * <ConnectorPanel />
 * ```
 */
export function ConnectorPanel(): React.ReactElement {
  const { connectors, selectedConnector, isLoading, selectConnector, setConnectors } = useConnectorStore()

  // Initialize connectors on mount if empty
  useEffect(() => {
    if (connectors.length === 0) {
      const platforms: ConnectorPlatform[] = ['instagram', 'tiktok', 'youtube', 'twitter', 'facebook', 'threads']
      const initialConnectors = platforms.map((platform) => ({
        id: `${platform}-${Date.now()}`,
        platform,
        status: 'disconnected' as const,
        handle: '',
        followers: 0,
        lastSync: null,
        config: CONNECTOR_CAPABILITIES[platform],
        createdAt: new Date().toISOString(),
      }))
      setConnectors(initialConnectors)
    }
  }, [connectors.length, setConnectors])

  // Calculate stats
  const connectedCount = connectors.filter((c) => c.status === 'connected').length
  const totalFollowers = connectors.reduce((sum, c) => sum + c.followers, 0)
  const readyToPublish = connectors.filter((c) => c.status === 'connected' && c.config.canPublish).length

  const platformDescriptions: Record<ConnectorPlatform, string> = {
    instagram: 'Instagram/Meta: 2.96B users, Reels + Stories + Posts',
    tiktok: 'TikTok: 1.56B users, vertical video native',
    youtube: 'YouTube: 2.6B users, discovery engine',
    twitter: 'X/Twitter: 368M users, real-time engagement + news',
    facebook: 'Facebook: 2.96B users, broad demographic reach',
    threads: 'Threads: Meta\'s text-based social platform',
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">Social Platform Connectors</h2>
        <p className="text-slate-400">Connect your social media accounts to reach 80%+ of digital audiences</p>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Connected', value: `${connectedCount}/${connectors.length}`, icon: <Zap className="w-5 h-5" /> },
          { label: 'Total Reach', value: `${(totalFollowers / 1000).toFixed(1)}K`, icon: <Users className="w-5 h-5" /> },
          { label: 'Ready to Publish', value: String(readyToPublish), icon: <Share2 className="w-5 h-5" /> },
          { label: 'Trend Score', value: '0%', icon: <TrendingUp className="w-5 h-5" /> },
        ].map((stat, i) => (
          <div key={i} className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="text-purple-500">{stat.icon}</div>
              <p className="text-sm text-slate-400">{stat.label}</p>
            </div>
            <p className="text-2xl font-bold text-white">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border border-purple-500/30 border-t-purple-500" />
          <span className="ml-3 text-slate-400">Loading connectors...</span>
        </div>
      )}

      {/* Connectors Grid */}
      {!isLoading && connectors.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {connectors.map((connector) => (
            <div
              key={connector.id}
              onClick={() => selectConnector(connector.id)}
              className={`cursor-pointer transition-all ${
                selectedConnector === connector.id ? 'ring-2 ring-purple-500 ring-offset-2 ring-offset-slate-950' : ''
              }`}
            >
              <ConnectorCard connector={connector} isSelected={selectedConnector === connector.id} />
            </div>
          ))}
        </div>
      )}

      {/* Selected Connector Details */}
      {selectedConnector && connectors.find((c) => c.id === selectedConnector) && (
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 rounded-lg p-6">
          <h3 className="text-lg font-bold text-white mb-4">Connector Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase mb-1">Platform</p>
              <p className="text-white capitalize">{connectors.find((c) => c.id === selectedConnector)?.platform}</p>
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase mb-1">Status</p>
              <div className="flex items-center gap-2">
                <div
                  className={`w-2 h-2 rounded-full ${
                    connectors.find((c) => c.id === selectedConnector)?.status === 'connected'
                      ? 'bg-green-500'
                      : 'bg-slate-500'
                  }`}
                />
                <p className="text-white capitalize">{connectors.find((c) => c.id === selectedConnector)?.status}</p>
              </div>
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase mb-1">Capabilities</p>
              <div className="flex flex-wrap gap-2">
                {connectors.find((c) => c.id === selectedConnector)?.config?.canPublish && (
                  <span className="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded">Publish</span>
                )}
                {connectors.find((c) => c.id === selectedConnector)?.config?.canSchedule && (
                  <span className="px-2 py-1 bg-purple-500/20 text-purple-300 text-xs rounded">Schedule</span>
                )}
                {connectors.find((c) => c.id === selectedConnector)?.config?.canAnalytics && (
                  <span className="px-2 py-1 bg-orange-500/20 text-orange-300 text-xs rounded">Analytics</span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Info Card */}
      <div className="bg-gradient-to-r from-purple-500/10 to-blue-500/10 border border-purple-500/20 rounded-lg p-6">
        <h4 className="font-bold text-white mb-2">🚀 Platform Coverage</h4>
        <ul className="space-y-2 text-sm text-slate-300">
          {Object.entries(platformDescriptions)
            .slice(0, 4)
            .map(([_, desc]) => (
              <li key={desc}>
                <strong>{desc.split(':')[0]}:</strong> {desc.split(': ')[1]}
              </li>
            ))}
        </ul>
      </div>
    </div>
  )
}
