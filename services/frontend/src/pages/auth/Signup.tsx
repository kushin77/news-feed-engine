import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

/**
 * Signup page - user registration
 *
 * Allows new users to create an account
 *
 * @returns {React.ReactElement} Signup page component
 *
 * @example
 * ```tsx
 * <SignupPage />
 * ```
 */
export function SignupPage(): React.ReactElement {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (password !== confirmPassword) {
      alert('Passwords do not match')
      return
    }
    setIsLoading(true)
    try {
      // TODO: Call signup API endpoint
      // const response = await apiClient.post('/auth/signup', { email, password })
      // Store token and redirect
      setIsLoading(false)
      navigate('/dashboard')
    } catch (error) {
      console.error('Signup failed:', error)
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 to-slate-900 flex items-center justify-center">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <Link to="/" className="text-2xl font-bold text-white hover:text-purple-400 transition-colors">
            The Feed
          </Link>
          <h2 className="text-2xl font-bold text-white mt-6">Create Account</h2>
          <p className="text-slate-400 mt-2">Get started for free</p>
        </div>

        {/* Signup Form */}
        <form onSubmit={handleSubmit} className="bg-slate-900 border border-slate-800 rounded-lg p-8 space-y-6">
          <div>
            <label className="block text-sm font-medium text-white mb-2">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-purple-500"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-white mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-purple-500"
              placeholder="••••••••"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-white mb-2">Confirm Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-purple-500"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white font-bold py-2 px-4 rounded-lg transition-colors"
          >
            {isLoading ? 'Creating account...' : 'Sign Up'}
          </button>
        </form>

        {/* Login Link */}
        <p className="text-center text-slate-400 mt-6">
          Already have an account?{' '}
          <Link to="/auth/login" className="text-purple-400 hover:text-purple-300 font-medium">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
