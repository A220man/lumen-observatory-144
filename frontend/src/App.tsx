import { Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Layout from './components/Layout'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/agents" element={<Dashboard />} />
        <Route path="/executions" element={<Dashboard />} />
        <Route path="/workspaces" element={<Dashboard />} />
      </Routes>
    </Layout>
  )
}

export default App
