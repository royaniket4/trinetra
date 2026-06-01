import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Bell, AlertTriangle, Shield, Zap, X, CheckCircle, Clock } from 'lucide-react'
import useStore from '../../store/useStore'

export default function NotificationsDropdown({ isOpen, onClose }) {
  const navigate = useNavigate()
  const { alerts, selectAlert } = useStore()
  const [notifications, setNotifications] = useState([])
  const [activeTab, setActiveTab] = useState('all')

  useEffect(() => {
    const recentAlerts = alerts
      .filter(a => a.severity >= 4)
      .slice(0, 20)
      .map(alert => ({
        id: alert.id,
        type: 'alert',
        title: alert.rule_name,
        message: `Source: ${alert.source_ip || 'Unknown'}`,
        severity: alert.severity,
        timestamp: new Date(alert.timestamp),
        read: false,
      }))
    
    setNotifications(recentAlerts)
  }, [alerts])

  const unreadCount = notifications.filter(n => !n.read).length

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 5:
        return <Zap className="w-4 h-4 text-critical" />
      case 4:
        return <AlertTriangle className="w-4 h-4 text-warning" />
      default:
        return <Shield className="w-4 h-4 text-electric-blue" />
    }
  }

  const formatTime = (date) => {
    const now = new Date()
    const diff = now - date
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    
    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    return date.toLocaleDateString()
  }

  const markAllRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })))
  }

  const handleNotificationClick = (notification) => {
    setNotifications(prev => prev.map(n => n.id === notification.id ? { ...n, read: true } : n))
    selectAlert(notification.id)
    navigate('/alerts')
    onClose()
  }

  const handleViewAllAlerts = () => {
    navigate('/alerts')
    onClose()
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40"
            onClick={onClose}
          />
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            className="absolute right-0 top-12 w-96 bg-bg-secondary border border-white/10 rounded-xl shadow-2xl z-50 overflow-hidden"
          >
            <div className="p-4 border-b border-white/10 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Bell className="w-5 h-5 text-neon-cyan" />
                <span className="font-heading text-white">Notifications</span>
                {unreadCount > 0 && (
                  <span className="px-2 py-0.5 text-xs bg-critical text-white rounded-full">
                    {unreadCount}
                  </span>
                )}
              </div>
              {unreadCount > 0 && (
                <button 
                  onClick={markAllRead}
                  className="text-xs text-neon-cyan hover:underline"
                >
                  Mark all read
                </button>
              )}
            </div>

            <div className="flex border-b border-white/10">
              <button
                onClick={() => setActiveTab('all')}
                className={`flex-1 py-2 text-sm ${activeTab === 'all' ? 'text-neon-cyan border-b-2 border-neon-cyan' : 'text-gray-500'}`}
              >
                All
              </button>
              <button
                onClick={() => setActiveTab('critical')}
                className={`flex-1 py-2 text-sm ${activeTab === 'critical' ? 'text-critical border-b-2 border-critical' : 'text-gray-500'}`}
              >
                Critical
              </button>
              <button
                onClick={() => setActiveTab('high')}
                className={`flex-1 py-2 text-sm ${activeTab === 'high' ? 'text-warning border-b-2 border-warning' : 'text-gray-500'}`}
              >
                High
              </button>
            </div>

            <div className="max-h-96 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  <Shield className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>No notifications</p>
                </div>
              ) : (
                <div className="divide-y divide-white/5">
                  {notifications
                    .filter(n => activeTab === 'all' || 
                      (activeTab === 'critical' && n.severity === 5) ||
                      (activeTab === 'high' && n.severity === 4))
                    .map(notification => (
                      <div
                        key={notification.id}
                        className={`p-4 hover:bg-white/5 cursor-pointer transition-colors ${
                          !notification.read ? 'bg-neon-cyan/5' : ''
                        }`}
                        onClick={() => handleNotificationClick(notification)}
                      >
                        <div className="flex items-start gap-3">
                          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                            notification.severity === 5 ? 'bg-critical/20' :
                            notification.severity === 4 ? 'bg-warning/20' : 'bg-electric-blue/20'
                          }`}>
                            {getSeverityIcon(notification.severity)}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <p className={`text-sm truncate ${!notification.read ? 'text-white font-medium' : 'text-gray-300'}`}>
                                {notification.title}
                              </p>
                              {!notification.read && (
                                <div className="w-2 h-2 bg-neon-cyan rounded-full flex-shrink-0" />
                              )}
                            </div>
                            <p className="text-xs text-gray-500 truncate">{notification.message}</p>
                            <div className="flex items-center gap-1 mt-1 text-xs text-gray-600">
                              <Clock className="w-3 h-3" />
                              {formatTime(notification.timestamp)}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              )}
            </div>

            <div className="p-3 border-t border-white/10">
              <button 
                onClick={handleViewAllAlerts}
                className="w-full text-center text-sm text-neon-cyan hover:underline py-1"
              >
                View all alerts →
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
