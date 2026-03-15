import React, { useState } from 'react'
import { ConnectorPanel } from '@components/ConnectorPanel'

/**
 * Dashboard page - main content area showing feed stats and controls
 *
 * Displays stats, quick actions, and connectors management with tab navigation.
 *
 * @returns {React.ReactElement} Dashboard component
 *
 * @example
 * ```tsx
 * <Dashboard />
 * ```
 */
export function Dashboard(): React.ReactElement {
  const [activeTab, setActiveTab] = useState<'overview' | 'connectors'>('overview')
  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-slate-400">Welcome to your AI-powered content platform</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-slate-800">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'overview'
              ? 'text-purple-400 border-b-2 border-purple-500'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Overview
        </button>
        <button
          onClick={() => setActiveTab('connectors')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'connectors'
              ? 'text-purple-400 border-b-2 border-purple-500'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Social Connectors
        </button>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { label: 'Total Posts', value: '0', icon: '📝' },
          { label: 'Reach', value: '0', icon: '👥' },
          { label: 'Engagement', value: '0%', icon: '📊' },
          { label: 'Scheduled', value: '0', icon: '📅' },
        ].map((stat, i) => (
          <div key={i} className="bg-slate-900 border border-slate-800 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <p className="text-slate-400 font-medium">{stat.label}</p>
              <span className="text-2xl">{stat.icon}</span>
            </div>
            <p className="text-3xl font-bold text-white">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-bold text-white mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { title: 'Create Content', desc: 'Start a new post', action: 'new_content' },
            { title: 'Schedule Post', desc: 'Plan future content', action: 'schedule' },
            { title: 'View Analytics', desc: 'Check performance', action: 'analytics' },
          ].map((action, i) => (
            <button
              key={i}
              className="bg-slate-900 border border-slate-800 hover:border-purple-500 rounded-lg p-6 text-left transition-all hover:shadow-lg hover:shadow-purple-500/20"
            >
              <h3 className="font-bold text-white mb-1">{action.title}</h3>
              <p className="text-sm text-slate-400">{action.desc}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div>
        <h2 className="text-xl font-bold text-white mb-4">Recent Activity</h2>
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
          <p className="text-slate-400 text-center py-12">No activity yet. Create your first post!</p>
        </div>
      </div>
      )}

      {/* Connectors Tab */}
      {activeTab === 'connectors' && <ConnectorPanel />}
