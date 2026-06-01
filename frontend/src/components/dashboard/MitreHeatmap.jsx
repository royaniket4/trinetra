import { useMemo } from 'react'
import { motion } from 'framer-motion'

const mitreTactics = [
  'Reconnaissance',
  'Resource Development',
  'Initial Access',
  'Execution',
  'Persistence',
  'Privilege Escalation',
  'Defense Evasion',
  'Credential Access',
  'Discovery',
  'Lateral Movement',
  'Collection',
  'Command and Control',
  'Exfiltration',
  'Impact',
]

const mitreShortTactics = [
  'TA0043', 'TA0042', 'TA0001', 'TA0002', 'TA0003', 'TA0004', 
  'TA0005', 'TA0006', 'TA0007', 'TA0008', 'TA0009', 'TA0011', 'TA0010', 'TA0040',
]

export default function MitreHeatmap({ alerts = [] }) {
  const coverage = useMemo(() => {
    const counts = {}
    alerts.forEach(alert => {
      if (alert.mitre_tactic) {
        counts[alert.mitre_tactic] = (counts[alert.mitre_tactic] || 0) + 1
      }
    })
    return counts
  }, [alerts])

  const maxCount = Math.max(...Object.values(coverage), 1)

  return (
    <div className="glass-card p-4">
      <h3 className="font-heading text-sm text-neon-cyan mb-4">
        MITRE ATT&CK Coverage
      </h3>
      
      <div className="grid grid-cols-7 gap-1">
        {mitreTactics.map((tactic, index) => {
          const count = coverage[tactic] || 0
          const intensity = count > 0 ? (count / maxCount) : 0
          
          return (
            <motion.div
              key={tactic}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: index * 0.02 }}
              className="aspect-square rounded-sm relative group cursor-pointer"
              style={{
                backgroundColor: count > 0 
                  ? `rgba(0, 229, 255, ${0.1 + intensity * 0.9})`
                  : 'rgba(255, 255, 255, 0.05)',
                border: count > 0 
                  ? '1px solid rgba(0, 229, 255, 0.5)'
                  : '1px solid rgba(255, 255, 255, 0.1)',
              }}
            >
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-bg-secondary rounded text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity z-10">
                <div className="font-medium text-neon-cyan">{tactic}</div>
                <div className="text-gray-400">{mitreShortTactics[index]}</div>
                <div className="text-gray-500">Alerts: {count}</div>
              </div>
            </motion.div>
          )
        })}
      </div>

      <div className="mt-4 flex items-center justify-center gap-4 text-xs text-gray-500">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-sm bg-neon-cyan/10 border border-neon-cyan/30" />
          <span>Low</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-sm bg-neon-cyan/50 border border-neon-cyan/50" />
          <span>Medium</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-sm bg-neon-cyan border border-neon-cyan" />
          <span>High</span>
        </div>
      </div>
    </div>
  )
}