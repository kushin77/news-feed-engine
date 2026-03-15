import React from 'react'

interface LayoutProps {
  children: React.ReactNode
}

/**
 * Main layout wrapper component providing header, sidebar, and content area
 *
 * @param {LayoutProps} props - Component props
 * @param {React.ReactNode} props.children - Child components to render
 * @returns {React.ReactElement} Layout wrapper element
 *
 * @example
 * ```tsx
 * <Layout>
 *   <Dashboard />
 * </Layout>
 * ```
 */
export function Layout({ children }: LayoutProps): React.ReactElement {
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(true)

  return (
    <div className="flex min-h-screen bg-slate-950">
      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 h-screen bg-slate-900 border-r border-slate-800 transition-transform duration-300 ${
          isSidebarOpen ? 'w-64' : 'w-0'
        } overflow-hidden z-40`}
      >
        <div className="p-6">
          <h2 className="text-xl font-bold text-white">The Feed</h2>
        </div>
        <nav className="space-y-2 p-4">
          <a href="#" className="block px-4 py-2 text-slate-300 hover:bg-slate-800 rounded">
            Dashboard
          </a>
          <a href="#" className="block px-4 py-2 text-slate-300 hover:bg-slate-800 rounded">
            Content
          </a>
          <a href="#" className="block px-4 py-2 text-slate-300 hover:bg-slate-800 rounded">
            Analytics
          </a>
          <a href="#" className="block px-4 py-2 text-slate-300 hover:bg-slate-800 rounded">
            Settings
          </a>
        </nav>
      </aside>

      {/* Main Content */}
      <div className={`flex-1 transition-all duration-300 ${isSidebarOpen ? 'ml-64' : 'ml-0'}`}>
        {/* Header */}
        <header className="sticky top-0 z-30 bg-slate-900/95 backdrop-blur border-b border-slate-800 px-6 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 hover:bg-slate-800 rounded text-white"
            >
              ☰
            </button>
            <div className="flex items-center gap-4">
              <span className="text-slate-300">User</span>
              <img
                src="https://via.placeholder.com/40"
                alt="avatar"
                className="w-10 h-10 rounded-full"
              />
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-6">{children}</main>
      </div>
    </div>
  )
}
