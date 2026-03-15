import React from 'react'
import { Layout } from '@components/Layout'
import { Dashboard } from '@pages/Dashboard'
import '@/styles/globals.css'

/**
 * Main App component - FAANG-grade news feed engine frontend
 *
 * @returns {React.ReactElement} Application root element
 *
 * @example
 * ```tsx
 * <App />
 * ```
 */
export function App(): React.ReactElement {
  return (
    <Layout>
      <Dashboard />
    </Layout>
  )
}

export default App
