import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Dashboard } from '@pages/Dashboard'

describe('Dashboard', () => {
  it('renders dashboard heading', () => {
    render(<Dashboard />)
    expect(screen.getByRole('heading', { name: /Dashboard/i })).toBeInTheDocument()
  })

  it('displays stats grid', () => {
    render(<Dashboard />)
    expect(screen.getByText(/Total Posts/i)).toBeInTheDocument()
    expect(screen.getByText(/Reach/i)).toBeInTheDocument()
    expect(screen.getByText(/Engagement/i)).toBeInTheDocument()
  })

  it('displays quick action buttons', () => {
    render(<Dashboard />)
    expect(screen.getByRole('button', { name: /Create Content/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Schedule Post/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /View Analytics/i })).toBeInTheDocument()
  })

  it('renders recent activity section', () => {
    render(<Dashboard />)
    expect(screen.getByText(/Recent Activity/i)).toBeInTheDocument()
  })
})
