import React from 'react'
import { ConnectorPanel } from '@components/ConnectorPanel'

/**
 * Connectors page - manage social media connections
 *
 * Shows all connected platforms and allows adding new connections
 *
 * @returns {React.ReactElement} Connectors page component
 *
 * @example
 * ```tsx
 * <ConnectorsPage />
 * ```
 */
export function ConnectorsPage(): React.ReactElement {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">Social Connectors</h1>
      <p className="text-slate-400">Connect your social media accounts to publish content</p>

      <ConnectorPanel />
    </div>
  )
}
