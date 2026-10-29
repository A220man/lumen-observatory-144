import { useState, useEffect } from 'react'
import './Dashboard.css'

interface HealthResponse {
  status: string
  service: string
}

export default function Dashboard() {
  const [health, setHealth] = useState<HealthResponse | null>(null)

  useEffect(() => {
    fetch('/api/v1/health')
      .then(res => res.json())
      .then(data => {
        setHealth(data)
      })
      .catch(() => {
        // Error handling could be added here
      })
  }, [])

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p>Welcome to Lumen Observatory - Agent Management Platform</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">🤖</div>
          <div className="stat-content">
            <span className="stat-value">0</span>
            <span className="stat-label">Agents Registered</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⚡</div>
          <div className="stat-content">
            <span className="stat-value">0</span>
            <span className="stat-label">Executions Today</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📁</div>
          <div className="stat-content">
            <span className="stat-value">0</span>
            <span className="stat-label">Workspaces</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">{health ? '✅' : '⏳'}</div>
          <div className="stat-content">
            <span className="stat-value">{health?.status || 'Loading...'}</span>
            <span className="stat-label">API Status</span>
          </div>
        </div>
      </div>

      <div className="dashboard-sections">
        <section className="section">
          <h2>Quick Start</h2>
          <div className="quick-start-grid">
            <div className="quick-start-card">
              <h3>Register an Agent</h3>
              <p>Add a new agent to the registry with its configuration and capabilities.</p>
              <button className="btn btn-primary">Add Agent</button>
            </div>
            <div className="quick-start-card">
              <h3>Run Execution</h3>
              <p>Execute an agent with input data and monitor the results in real-time.</p>
              <button className="btn btn-primary">Run Agent</button>
            </div>
            <div className="quick-start-card">
              <h3>Create Workspace</h3>
              <p>Organize your agents and executions into logical workspaces.</p>
              <button className="btn btn-primary">New Workspace</button>
            </div>
          </div>
        </section>

        <section className="section">
          <h2>Recent Activity</h2>
          <div className="empty-state">
            <p>No activity yet. Register your first agent to get started!</p>
          </div>
        </section>
      </div>
    </div>
  )
}
