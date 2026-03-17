import React from 'react'
import { useEffect } from 'react'
import { Zap, Users, Share2, TrendingUp } from 'lucide-react'
import { ConnectorCard } from './ConnectorCard'
import { useConnectorStore } from '../store/connectors'
import type { ConnectorPlatform } from '../types/connectors'

/**
 * Social Connectors Panel - Display and manage social media connections
 *
 * Shows connection status for all platforms (Instagram, TikTok, YouTube, X, etc.).
 * Uses Zustand for global state management of connector connections.
 *
 * Features:
 * - Display all platform connectors with current connection status
 * - Connect/disconnect buttons with loading states
 * - Real-time follower count and sync status
 * - Connector details view
 * - Error handling and user feedback
 *
 * @returns {React.ReactElement} Connector panel component
 *
 * @example
 * ```tsx
 * <ConnectorPanel />
 * ```
 */
export function ConnectorPanel(): React.ReactElement {
  const { connectors, selectedConnector, loadingConnectorId, selectConnector, setConnectors, connectPlatform, disconnectPlatform } = useConnectorStore()

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
    instagram: 'Instagram: 2.96B users, Reels + Stories + Posts',
    tiktok: 'TikTok: 1.56B users, vertical video native',
    youtube: 'YouTube: 2.6B users, discovery engine',
    twitter: 'X/Twitter: 368M users, real-time engagement',
    facebook: 'Facebook: 2.96B users, broad demographic',
    threads: 'Threads: Meta\'s text-based platform',
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">Social Platform Connectors</h2>
        <p className="text-slate-400">Connect your accounts and reach billions of potential audiences</p>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Connected', value: `${connectedCount}/${connectors.length}`, icon: <Zap className="w-5 h-5" /> },
          { label: 'Total Reach', value: `${(totalFollowers / 1000000).toFixed(1)}M`, icon: <Users className="w-5 h-5" /> },
          { label: 'Ready to Publish', value: String(readyToPublish), icon: <Share2 className="w-5 h-5" /> },
          { label: 'Platforms', value: String(connectors.length), icon: <TrendingUp className="w-5 h-5" /> },
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

      {/* Connectors Grid */}
      {connectors.length > 0 && (
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
                onConnect={connectPlatform}
                onDisconnect={disconnectPlatform}
                onSelect={selectConnector}
                isLoading={loadingConnectorId === connector.id}
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
          <p className="text-sm text-slate-400 mt-4">{platformDescriptions[selectedConnector.platform]}</p>
        </div>
      )}
    </div>
  )
}
