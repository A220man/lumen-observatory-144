import { Outlet, Link, useLocation } from 'react-router-dom'
import './Layout.css'

const navigation = [
  { path: '/', label: 'Dashboard' },
  { path: '/agents', label: 'Agents' },
  { path: '/executions', label: 'Executions' },
  { path: '/workspaces', label: 'Workspaces' },
]

interface LayoutProps {
  children?: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()

  return (
    <div className="layout">
      <header className="header">
        <div className="header-content">
          <Link to="/" className="logo">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="16" cy="16" r="14" stroke="#3b82f6" strokeWidth="2"/>
              <path d="M16 8V24M8 16H24" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            <span>Lumen Observatory</span>
          </Link>
          <nav className="nav">
            {navigation.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={location.pathname === item.path ? 'active' : ''}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <main className="main">
        {children || <Outlet />}
      </main>
    </div>
  )
}
