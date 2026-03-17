import React from 'react'
import { Link } from 'react-router-dom'

/**
 * Landing page - public marketing/welcome page
 *
 * Displays product information and calls-to-action for login/signup
 *
 * @returns {React.ReactElement} Landing page component
 *
 * @example
 * ```tsx
 * <LandingPage />
 * ```
 */
export function LandingPage(): React.ReactElement {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-900 to-slate-950">
      {/* Navigation */}
      <nav className="border-b border-slate-800 bg-slate-950/50 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-white">The Feed</h1>
          <div className="flex gap-4">
            <Link
              to="/auth/login"
              className="px-4 py-2 text-slate-300 hover:text-white transition-colors"
            >
              Login
            </Link>
            <Link
              to="/auth/signup"
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors font-medium"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-6xl mx-auto px-6 py-24 text-center">
        <h2 className="text-5xl font-bold text-white mb-6">
          Manage All Your Content in One Place
        </h2>
        <p className="text-xl text-slate-300 mb-12 max-w-2xl mx-auto">
          Create, schedule, and publish content across all social platforms with AI assistance
        </p>
        <Link
          to="/auth/signup"
          className="inline-block px-8 py-4 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-bold transition-all hover:shadow-lg hover:shadow-purple-500/30"
        >
          Start Free Trial
        </Link>
      </section>

      {/* Features Section */}
      <section className="max-w-6xl mx-auto px-6 py-20">
        <h3 className="text-3xl font-bold text-white mb-12 text-center">Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            { icon: '🤖', title: 'AI Assistant', desc: 'Generate content with AI' },
            { icon: '📅', title: 'Schedule', desc: 'Plan posts in advance' },
            { icon: '📊', title: 'Analytics', desc: 'Track performance metrics' },
          ].map((feature, i) => (
            <div key={i} className="bg-slate-900 border border-slate-800 rounded-lg p-8 text-center">
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h4 className="text-xl font-bold text-white mb-2">{feature.title}</h4>
              <p className="text-slate-400">{feature.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-6xl mx-auto px-6 py-20 text-center border-t border-slate-800">
        <h3 className="text-3xl font-bold text-white mb-6">Ready to get started?</h3>
        <Link
          to="/auth/signup"
          className="inline-block px-8 py-4 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-bold transition-all hover:shadow-lg hover:shadow-purple-500/30"
        >
          Create Your Account
        </Link>
      </section>
    </div>
  )
}
