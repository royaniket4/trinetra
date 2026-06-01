import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bell, Search, Wifi, WifiOff, Settings, LogOut, User as UserIcon, Shield } from 'lucide-react'
import useStore from '../../store/useStore'
import { useAuth } from '../../contexts/AuthContext'
import SettingsModal from '../common/SettingsModal'
import NotificationsDropdown from '../common/NotificationsDropdown'
import { motion, AnimatePresence } from 'framer-motion'

export default function TopBar() {
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const { wsConnected, alerts } = useStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [showSettings, setShowSettings] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)

  const criticalAlerts = alerts.filter(a => a.severity === 5).length

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="fixed top-0 right-0 left-64 h-16 bg-bg-secondary/80 backdrop-blur-md border-b border-white/10 z-30 px-6 flex items-center justify-between">
      <div className="flex items-center gap-4 flex-1">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text"
            placeholder="Search alerts, logs, IPs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-bg-primary/50 border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan/50"
          />
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-bg-primary/50 border border-white/10">
          {wsConnected ? (
            <><Wifi className="w-4 h-4 text-success" /><span className="text-xs text-success">Live</span></>
          ) : (
            <><WifiOff className="w-4 h-4 text-critical" /><span className="text-xs text-critical">Offline</span></>
          )}
        </div>

        <div className="relative">
          <button onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 hover:bg-white/10 rounded-lg transition-colors">
            <Bell className="w-5 h-5 text-gray-400" />
            {criticalAlerts > 0 && <span className="absolute top-1 right-1 w-2 h-2 bg-critical rounded-full animate-pulse" />}
          </button>
          <NotificationsDropdown isOpen={showNotifications} onClose={() => setShowNotifications(false)} />
        </div>

        <button onClick={() => setShowSettings(true)}
          className="p-2 hover:bg-white/10 rounded-lg transition-colors">
          <Settings className="w-5 h-5 text-gray-400" />
        </button>

        <div className="relative">
          <button onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-2 p-1.5 hover:bg-white/10 rounded-lg transition-colors">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-neon-cyan to-electric-blue flex items-center justify-center">
              <span className="text-xs font-bold">{user?.username?.charAt(0).toUpperCase() || 'S'}</span>
            </div>
            <div className="hidden md:block text-left">
              <div className="text-xs text-white leading-tight">{user?.username || 'SOC Analyst'}</div>
              <div className="text-[10px] text-gray-500 capitalize">{user?.role || 'analyst'}</div>
            </div>
          </button>

          <AnimatePresence>
            {showUserMenu && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setShowUserMenu(false)} />
                <motion.div
                  initial={{ opacity: 0, y: -10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -10, scale: 0.95 }}
                  className="absolute right-0 top-12 w-48 bg-bg-secondary border border-white/10 rounded-xl shadow-2xl z-50 overflow-hidden"
                >
                  <div className="p-3 border-b border-white/10">
                    <div className="text-sm text-white">{user?.username}</div>
                    <div className="text-xs text-gray-500">{user?.email}</div>
                    <div className="flex items-center gap-1 mt-1">
                      {user?.role === 'admin' ? <Shield className="w-3 h-3 text-warning" /> : <UserIcon className="w-3 h-3 text-neon-cyan" />}
                      <span className="text-[10px] text-gray-500 capitalize">{user?.role}</span>
                    </div>
                  </div>
                  <button onClick={handleLogout}
                    className="w-full flex items-center gap-2 px-3 py-2.5 text-sm text-gray-400 hover:text-white hover:bg-white/5 transition-colors">
                    <LogOut className="w-4 h-4" />
                    Sign Out
                  </button>
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </div>
      </div>

      <SettingsModal isOpen={showSettings} onClose={() => setShowSettings(false)} />
    </header>
  )
}
