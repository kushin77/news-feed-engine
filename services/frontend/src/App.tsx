import '@/styles/globals.css'

import { Navigate, Route, Routes } from 'react-router-dom'

import { AIGeneratorPage } from '@pages/AIGenerator'
import { AIVideoPage } from '@pages/AIVideo'
import { AnalyticsPage } from '@pages/AnalyticsPage'
import { ConnectorSettingsPage } from '@pages/ConnectorSettings'
import { ConnectorsPage } from '@pages/ConnectorsPage'
import { ContentEditorPage } from '@pages/ContentEditor'
import { ContentPage } from '@pages/ContentPage'
import { Dashboard } from '@pages/Dashboard'
import { HelpPage } from '@pages/HelpPage'
import { LandingPage } from '@pages/public/Landing'
import { Layout } from '@components/Layout'
import { LoginPage } from '@pages/auth/Login'
import { PublishingHistoryPage } from '@pages/PublishingHistory'
import { PublishingPage } from '@pages/PublishingPage'
import React from 'react'
import { SettingsPage } from '@pages/SettingsPage'
import { SignupPage } from '@pages/auth/Signup'
import { TrendingPage } from '@pages/TrendingPage'

/**
 * Main App component with routing configuration
 *
 * Defines all 14 application routes:
 * - 3 public routes (Landing, Login, Signup)
 * - 11 protected routes (authenticated users only)
 *
 * @returns {React.ReactElement} Application with routes
 *
 * @example
 * ```tsx
 * <App />
 * ```
 */
export function App(): React.ReactElement {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/auth/login" element={<LoginPage />} />
      <Route path="/auth/signup" element={<SignupPage />} />

      {/* Protected Routes - All wrapped in Layout */}
      <Route element={<Layout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/content" element={<ContentPage />} />
        <Route path="/content/editor" element={<ContentEditorPage />} />
        <Route path="/connectors" element={<ConnectorsPage />} />
        <Route path="/connectors/:id/settings" element={<ConnectorSettingsPage />} />
        <Route path="/publishing" element={<PublishingPage />} />
        <Route path="/publishing/history" element={<PublishingHistoryPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/analytics/trending" element={<TrendingPage />} />
        <Route path="/ai/generator" element={<AIGeneratorPage />} />
        <Route path="/ai/video" element={<AIVideoPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/help" element={<HelpPage />} />
      </Route>

      {/* Catch-all redirect */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
