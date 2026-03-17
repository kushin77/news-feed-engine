import React from 'react'

/**
 * Settings page - user and account settings
 *
 * Configure profile, preferences, and account options
 *
 * @returns {React.ReactElement} Settings page component
 *
 * @example
 * ```tsx
 * <SettingsPage />
 * ```
 */
export function SettingsPage(): React.ReactElement {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">Settings</h1>

      <div className="max-w-2xl space-y-6">
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4">Profile</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-white mb-2">Name</label>
              <input
                type="text"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-purple-500"
                placeholder="Your name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-white mb-2">Email</label>
              <input
                type="email"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-purple-500"
                placeholder="your@email.com"
              />
            </div>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4">Notifications</h2>
          <div className="flex items-center justify-between">
            <span className="text-white">Email notifications</span>
            <input type="checkbox" defaultChecked className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4">Danger Zone</h2>
          <button className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors">
            Delete Account
          </button>
        </div>
      </div>
    </div>
  )
}
