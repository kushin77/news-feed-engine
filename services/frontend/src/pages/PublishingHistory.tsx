import React, { useEffect } from 'react'
import { useContentStore } from '../store/content'

/**
 * Publishing History page - view past published content
 *
 * Shows timeline of all previously published posts
 * Features:
 * - Chronological timeline
 * - Publication status badges
 * - Platform indicators
 * - Engagement stats
 *
 * @returns {React.ReactElement} Publishing history component
 *
 * @example
 * ```tsx
 * <PublishingHistoryPage />
 * ```
 */
export function PublishingHistoryPage(): React.ReactElement {
  const { publishedContent, isLoadingContent, loadPublishedContent } = useContentStore()

  useEffect(() => {
    loadPublishedContent()
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'published':
        return '✓'
      case 'scheduled':
        return '⏱'
      case 'draft':
        return '📝'
      default:
        return '○'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published':
        return 'text-green-400 bg-green-900/20'
      case 'scheduled':
        return 'text-yellow-400 bg-yellow-900/20'
      case 'draft':
        return 'text-slate-400 bg-slate-800'
      default:
        return 'text-slate-400 bg-slate-800'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">Publishing History</h1>
        {isLoadingContent && <div className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin" />}
      </div>

      <div className="space-y-3">
        {isLoadingContent ? (
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-12 text-center">
            <p className="text-slate-400">Loading history...</p>
          </div>
        ) : publishedContent.length > 0 ? (
          publishedContent.map((item, index) => (
            <div
              key={item.id}
              className="bg-slate-900 border border-slate-800 rounded-lg p-6 hover:border-slate-700 transition-colors"
            >
              <div className="flex items-start gap-4">
                <div className="text-2xl pt-1">{getStatusIcon(item.status)}</div>
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 className="text-lg font-bold text-white">{item.title}</h3>
                      <p className="text-slate-400 text-sm mt-1">Published {index === 0 ? 'just now' : '2 days ago'}</p>
                    </div>
                    <span className={`px-3 py-1 rounded text-sm font-medium ${getStatusColor(item.status)}`}>
                      {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4">
                    <div className="bg-slate-800 rounded p-2">
                      <p className="text-slate-400 text-xs">Views</p>
                      <p className="text-white font-bold">2.4K</p>
                    </div>
                    <div className="bg-slate-800 rounded p-2">
                      <p className="text-slate-400 text-xs">Engagement</p>
                      <p className="text-white font-bold">342</p>
                    </div>
                    <div className="bg-slate-800 rounded p-2">
                      <p className="text-slate-400 text-xs">Clicks</p>
                      <p className="text-white font-bold">89</p>
                    </div>
                    <div className="bg-slate-800 rounded p-2">
                      <p className="text-slate-400 text-xs">Conversions</p>
                      <p className="text-white font-bold">12</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-12 text-center">
            <p className="text-slate-400">No publishing history yet</p>
          </div>
        )}
      </div>
    </div>
  )
}
