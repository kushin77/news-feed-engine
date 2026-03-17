import React from 'react'

/**
 * Trending page - view trending content metrics
 *
 * Shows what's trending across connected platforms
 *
 * @returns {React.ReactElement} Trending page component
 *
 * @example
 * ```tsx
 * <TrendingPage />
 * ```
 */
export function TrendingPage(): React.ReactElement {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">Trending</h1>

      <div className="bg-slate-900 border border-slate-800 rounded-lg p-12 text-center">
        <p className="text-slate-400">No trending data yet</p>
      </div>
    </div>
  )
}
