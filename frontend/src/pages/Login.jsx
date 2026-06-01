import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Shield, Activity, Loader, Eye, EyeOff } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(form.username, form.password)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-bg-primary grid-bg flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Activity className="w-10 h-10 text-neon-cyan" />
            <span className="font-heading text-3xl font-bold neon-text">TRINETRA</span>
          </div>
          <p className="text-gray-500 text-sm">AI-Powered Cyber Defense Command Center</p>
        </div>

        <div className="bg-bg-secondary border border-white/10 rounded-xl p-8 shadow-2xl">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-neon-cyan/20 flex items-center justify-center">
              <Shield className="w-5 h-5 text-neon-cyan" />
            </div>
            <div>
              <h2 className="font-heading text-lg text-white">Sign In</h2>
              <p className="text-xs text-gray-500">Access your SOC dashboard</p>
            </div>
          </div>

          {error && (
            <div className="p-3 mb-4 bg-critical/10 border border-critical/30 rounded-lg text-critical text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm text-gray-400 mb-1 block">Username</label>
              <input type="text" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })}
                className="w-full bg-bg-primary border border-white/10 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-neon-cyan/50" 
                placeholder="Enter username" required />
            </div>

            <div>
              <label className="text-sm text-gray-400 mb-1 block">Password</label>
              <div className="relative">
                <input type={showPassword ? 'text' : 'password'} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })}
                  className="w-full bg-bg-primary border border-white/10 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-neon-cyan/50 pr-10" 
                  placeholder="Enter password" required />
                <button type="button" onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white">
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button type="submit" disabled={loading}
              className="w-full py-2.5 bg-gradient-to-r from-neon-cyan to-electric-blue rounded-lg text-white font-medium hover:opacity-90 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
            >
              {loading ? <Loader className="w-4 h-4 animate-spin" /> : null}
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <p className="text-center text-xs text-gray-600 mt-6">
            Don't have an account? <Link to="/register" className="text-neon-cyan hover:underline">Register</Link>
          </p>
        </div>

        <p className="text-center text-xs text-gray-700 mt-6">
          First user to register gets admin privileges
        </p>
      </motion.div>
    </div>
  )
}
