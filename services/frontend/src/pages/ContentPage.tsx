import React from 'react'
import { Link } from 'react-router-dom'

/**
 * Content page - main content management view
 *
 * Lists all created content with filters and bulk actions
 *
 * @returns {React.ReactElement} Content page component
 *
 * @example
 * ```tsx
 * <ContentPage />
 * ```
 */
export function ContentPage(): React.ReactElement {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">Content</h1>
        <Link
          to="/content/editor"
          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors"
        >
          Create Post
        </Link>
      </div>

      <div className="grid gap-4">
        {/* Content List Placeholder */}
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-12 text-center">
          <p className="text-slate-400">No content yet. Create your first post!</p>
        </div>
      </div>
    </div>
  )
}
