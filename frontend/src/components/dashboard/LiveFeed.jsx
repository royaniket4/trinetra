import { useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import PulseDot from '../common/PulseDot'
import { AlertTriangle, Shield, Target } from 'lucide-react'

const severityConfig = {
  1: { label: 'Info', color: 'text-gray-400' },
  2: { label: 'Low', color: 'text-electric-blue' },
  3: { label: 'Medium', color: 'text-warning' },
  4: { label: 'High', color: 'text-orange-500' },
  5: { label: 'Critical', color: 'text-critical' },
}

export default function LiveFeed({ alerts = [] }) {
  const containerRef = useRef(null)

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = 0
    }
  }, [alerts.length])

  return (
    <div className="glass-card p-4 h-[400px] flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-heading text-sm text-neon-cyan flex items-center gap-2">
          <Target className="w-4 h-4" />
          Live Alert Feed
        </h3>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 bg-success rounded-full animate-pulse" />
          <span className="text-xs text-gray-400">Real-time</span>
        </div>
      </div>
      
      <div 
        ref={containerRef}
        className="flex-1 overflow-y-auto space-y-2 pr-2"
      >
        <AnimatePresence>
          {alerts.slice(0, 50).map((alert, index) => (
            <motion.div
              key={alert.id || index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0 }}
              transition={{ delay: index * 0.05 }}
              className="p-3 bg-bg-primary/50 rounded-lg border border-white/5 hover:border-white/10 transition-colors"
            >
              <div className="flex items-start gap-3">
                <PulseDot severity={alert.severity} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className={`text-xs font-medium ${severityConfig[alert.severity]?.color}`}>
                      {severityConfig[alert.severity]?.label}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(alert.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-sm text-white mt-1 truncate">
                    {alert.rule_name}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    {alert.source_ip && (
                      <span className="text-xs text-gray-500 font-mono">
                        {alert.source_ip}
                      </span>
                    )}
                    {alert.mitre_tactic && (
                      <span className="text-xs px-2 py-0.5 rounded bg-purple/20 text-purple">
                        {alert.mitre_tactic}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        
        {alerts.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <Shield className="w-8 h-8 mb-2 opacity-50" />
            <p className="text-sm">No alerts yet</p>
            <p className="text-xs mt-1">Start the simulator to generate alerts</p>
          </div>
        )}
      </div>
    </div>
  )
}