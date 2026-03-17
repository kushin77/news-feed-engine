import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ConnectorPanel } from '@components/ConnectorPanel'

describe('ConnectorPanel', () => {
  it('renders all platform connectors', () => {
    render(<ConnectorPanel />)
    expect(screen.getByText(/Instagram\/Meta/i)).toBeInTheDocument()
    expect(screen.getByText(/TikTok/i)).toBeInTheDocument()
    expect(screen.getByText(/YouTube/i)).toBeInTheDocument()
    expect(screen.getByText(/X \/ Twitter/i)).toBeInTheDocument()
  })

  it('displays connector header', () => {
    render(<ConnectorPanel />)
    expect(screen.getByText(/Social Platform Connectors/i)).toBeInTheDocument()
    expect(screen.getByText(/80%\+ of digital audiences/i)).toBeInTheDocument()
  })

  it('shows stats grid with reach and platform metrics', () => {
    render(<ConnectorPanel />)
    expect(screen.getByText(/Connected/i)).toBeInTheDocument()
    expect(screen.getByText(/Total Reach/i)).toBeInTheDocument()
    expect(screen.getByText(/Ready to Publish/i)).toBeInTheDocument()
    expect(screen.getByText(/Trend Score/i)).toBeInTheDocument()
  })

  it('displays platform info in footer', () => {
    render(<ConnectorPanel />)
    expect(screen.getByText(/Platform Coverage/i)).toBeInTheDocument()
    expect(screen.getByText(/2.96B users/i)).toBeInTheDocument()
  })

  it('shows connect button for disconnected platforms', () => {
    render(<ConnectorPanel />)
    const connectButtons = screen.getAllByText(/Connect Account/i)
    expect(connectButtons.length).toBeGreaterThan(0)
  })
})
