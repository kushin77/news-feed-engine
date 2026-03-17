import React from 'react'
import { Link, Outlet, useLocation } from 'react-router-dom'

/**
 * Main layout wrapper component providing header, sidebar, and content area
 *
 * Used as a route wrapper for all protected pages. Provides:
 * - Navigation sidebar with active state highlighting
 * - Top header with user menu
 * - Content area for nested routes
 *
 * @returns {React.ReactElement} Layout wrapper element
 *
 * @example
 * ```tsx
 * <Route element={<Layout />}>
 *   <Route path="/dashboard" element={<Dashboard />} />
 * </Route>
 * ```
 */
export function Layout(): React.ReactElement {
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(true)
  const location = useLocation()

  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: '📊' },
    { label: 'Content', path: '/content', icon: '📝' },
    { label: 'Connectors', path: '/connectors', icon: '🔗' },
    { label: 'Publishing', path: '/publishing', icon: '📤' },
    { label: 'Analytics', path: '/analytics', icon: '📈' },
    { label: 'AI Generator', path: '/ai/generator', icon: '🤖' },
    { label: 'AI Video', path: '/ai/video', icon: '🎬' },
    { label: 'Settings', path: '/settings', icon: '⚙️' },
    { label: 'Help', path: '/help', icon: '❓' },
  ]

  const isActive = (path: string) => {
    if (path === '/dashboard') return location.pathname === path
    return location.pathname.startsWith(path)
  }

  return (
    <div className="flex min-h-screen bg-slate-950">
      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 h-screen bg-slate-900 border-r border-slate-800 transition-transform duration-300 ${
          isSidebarOpen ? 'w-64' : 'w-0'
        } overflow-hidden z-40`}
      >
        <div className="p-6 border-b border-slate-800">
          <Link to="/dashboard" className="text-xl font-bold text-white hover:text-purple-400 transition-colors">
            The Feed
          </Link>
        </div>
        <nav className="space-y-1 p-4">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
                isActive(item.path)
                  ? 'bg-purple-600/20 text-purple-400 border-l-2 border-purple-500'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <div className={`flex-1 transition-all duration-300 ${isSidebarOpen ? 'ml-64' : 'ml-0'}`}>
        {/* Header */}
        <header className="sticky top-0 z-30 bg-slate-900/95 backdrop-blur border-b border-slate-800 px-6 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 hover:bg-slate-800 rounded text-white transition-colors"
              title={isSidebarOpen ? 'Close sidebar' : 'Open sidebar'}
            >
              ☰
            </button>
            <div className="flex items-center gap-4">
              <span className="text-slate-300">User</span>
              <img
                src="https://via.placeholder.com/40"
                alt="avatar"
                className="w-10 h-10 rounded-full bg-purple-500"
              />
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
