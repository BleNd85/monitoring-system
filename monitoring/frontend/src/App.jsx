import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import Navbar from './components/Navbar'
import AgentsPage from './pages/AgentsPage'
import AgentDashboard from './pages/AgentDashboard'
import NewAgentPage from './pages/NewAgentPage'

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900 transition-colors">
          <Navbar />
          <Routes>
            <Route path="/" element={<AgentsPage />} />
            <Route path="/agents/new" element={<NewAgentPage />} />
            <Route path="/agents/:agentId" element={<AgentDashboard />} />
          </Routes>
        </div>
      </BrowserRouter>
    </ThemeProvider>
  )
}