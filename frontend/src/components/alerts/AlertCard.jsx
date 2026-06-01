import { useMemo } from 'react'
import { motion } from 'framer-motion'
import { Clock, User, Monitor } from 'lucide-react'
import SeverityBadge from './SeverityBadge'
import MitreBadge from './MitreBadge'

const severityBorderColors = {
  5: 'border-l-critical',
  4: 'border-l-warning',
  3: 'border-l-yellow-400',
  2: 'border-l-electric-blue',
  1: 'border-l-gray-500',
}

export default function AlertCard({ alert, onClick, isSelected }) {
  const timeAgo = useMemo(() => {
    if (!alert.timestamp) return 'Unknown'
    const now = new Date()
    const alertTime = new Date(alert.timestamp)
    const diffMs = now - alertTime
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    return alertTime.toLocaleDateString()
  }, [alert.timestamp])

  const isNew = useMemo(() => {
    if (!alert.timestamp) return false
    const now = new Date()
    const alertTime = new Date(alert.timestamp)
    return (now - alertTime) < 10000
  }, [alert.timestamp])

  return (
    <motion.div
      initial={{ x: 50, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: -50, opacity: 0 }}
      whileHover={{ scale: 1.01 }}
      onClick={onClick}
      className={`
        glass-card p-4 cursor-pointer transition-all
        border-l-4 ${severityBorderColors[alert.severity] || 'border-l-gray-500'}
        ${isSelected ? 'ring-2 ring-neon-cyan/50' : ''}
        ${isNew ? 'animate-pulse' : ''}
      `}
    >
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-heading text-sm font-bold text-white truncate flex-1 mr-2">
          {alert.rule_name}
        </h3>
        <SeverityBadge severity={alert.severity} />
      </div>
      
      <div className="flex items-center gap-3 text-xs text-gray-400 mb-3">
        {alert.source_ip && (
          <span className="flex items-center gap-1 font-mono">
            <Monitor className="w-3 h-3" />
            {alert.source_ip}
          </span>
        )}
        {alert.username && (
          <span className="flex items-center gap-1">
            <User className="w-3 h-3" />
            {alert.username}
          </span>
        )}
        <span className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          {timeAgo}
        </span>
      </div>
      
      <div className="flex items-center justify-between">
        <MitreBadge 
          tactic={alert.mitre_tactic}
          technique={alert.mitre_technique}
          tacticName={alert.mitre_tactic_name}
          techniqueName={alert.mitre_technique_name}
        />
        <span className="text-xs text-gray-500">
          {(alert.confidence * 100).toFixed(0)}% confidence
        </span>
      </div>
    </motion.div>
  )
}