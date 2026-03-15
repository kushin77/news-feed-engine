import React from 'react'
import { useEffect } from 'react'
import { Zap, Users, Share2, TrendingUp } from 'lucide-react'
import { ConnectorCard } from './ConnectorCard'
import { useConnectorStore } from '../store/connectors'
import type { ConnectorPlatform } from '../types/connectors'

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
      const platformNames: Record<ConnectorPlatform, string> = {
        instagram: 'Instagram',
        tiktok: 'TikTok',
        youtube: 'YouTube',
        twitter: 'X/Twitter',
        facebook: 'Facebook',
        threads: 'Threads',
      }
      const platformIcons: Record<ConnectorPlatform, string> = {
        instagram: '📸',
        tiktok: '🎵',
        youtube: '📺',
        twitter: '𝕏',
        facebook: 'f',
        threads: '💬',
      }
      const initialConnectors = platforms.map((platform) => ({
        id: `${platform}-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
        platform,
        name: platformNames[platform],
        icon: platformIcons[platform],
        status: 'disconnected' as const,
        handle: '',
        followerCount: 0,
      }))
      setConnectors(initialConnectors)
    }
  }, [connectors.length, setConnectors])

  // Calculate stats
  const connectedCount = connectors.filter((c) => c.status === 'connected').length
  const totalFollowers = connectors.reduce((sum, c) => sum + (c.followerCount || 0), 0)
  const readyToPublish = connectors.filter((c) => c.status === 'connected').length

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
              className={`cursor-pointer transition-all ${
                selectedConnector?.id === connector.id
                  ? 'ring-2 ring-purple-500 ring-offset-2 ring-offset-slate-950'
                  : ''
              }`}
            >
              <ConnectorCard
                connector={connector}
                onConnect={(id) => console.log('Connect:', id)}
                onDisconnect={(id) => console.log('Disconnect:', id)}
                onSelect={() => selectConnector(connector)}
              />
            </div>
          ))}
        </div>
      )}

      {/* Selected Connector Details */}
      {selectedConnector && (
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 rounded-lg p-6">
          <h3 className="text-lg font-bold text-white mb-4">Connector Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase mb-1">Platform</p>
              <p className="text-white capitalize">{selectedConnector.platform}</p>
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase mb-1">Status</p>
              <div className="flex items-center gap-2">
                <div
                  className={`w-2 h-2 rounded-full ${
                    selectedConnector.status === 'connected' ? 'bg-green-500' : 'bg-slate-500'
                  }`}
                />
                <p className="text-white capitalize">{selectedConnector.status}</p>
              </div>
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase mb-1">Followers</p>
              <p className="text-white">{(selectedConnector.followerCount || 0).toLocaleString()}</p>
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
