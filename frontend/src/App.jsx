import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import Alerts from './pages/Alerts'
import Incidents from './pages/Incidents'
import ThreatHunt from './pages/ThreatHunt'
import AIAssistant from './pages/AIAssistant'
import SOAR from './pages/SOAR'
import Detection from './pages/Detection'
import LogExplorer from './pages/LogExplorer'
import Compliance from './pages/Compliance'
import MitreNavigator from './pages/MitreNavigator'
import Login from './pages/Login'
import Register from './pages/Register'

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  if (loading) return <div className="min-h-screen bg-bg-primary grid-bg flex items-center justify-center"><div className="text-gray-500">Loading...</div></div>
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return children
}

function PublicRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  if (loading) return null
  if (isAuthenticated) return <Navigate to="/" replace />
  return children
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
      <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route index element={<Dashboard />} />
        <Route path="alerts" element={<Alerts />} />
        <Route path="incidents" element={<Incidents />} />
        <Route path="logs" element={<LogExplorer />} />
          <Route path="compliance" element={<Compliance />} />
          <Route path="mitre" element={<MitreNavigator />} />
          <Route path="threat-hunt" element={<ThreatHunt />} />
        <Route path="ai-assistant" element={<AIAssistant />} />
        <Route path="soar" element={<SOAR />} />
        <Route path="detection" element={<Detection />} />
      </Route>
    </Routes>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
