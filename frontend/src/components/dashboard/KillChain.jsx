import { motion } from 'framer-motion'
import { CheckCircle, Circle, Loader } from 'lucide-react'

const killChainPhases = [
  { name: 'Recon', short: '1' },
  { name: 'Initial Access', short: '2' },
  { name: 'Execution', short: '3' },
  { name: 'Persistence', short: '4' },
  { name: 'Privilege Escalation', short: '5' },
  { name: 'Lateral Movement', short: '6' },
  { name: 'Actions on Objectives', short: '7' },
]

export default function KillChain({ alerts = [] }) {
  const activePhases = new Set()
  alerts.slice(0, 10).forEach(alert => {
    if (alert.mitre_tactic) {
      const tacticMap = {
        'Reconnaissance': 0,
        'Resource Development': 1,
        'Initial Access': 1,
        'Execution': 2,
        'Persistence': 3,
        'Privilege Escalation': 4,
        'Defense Evasion': 4,
        'Credential Access': 4,
        'Discovery': 5,
        'Lateral Movement': 5,
        'Collection': 6,
        'Command and Control': 6,
        'Exfiltration': 6,
        'Impact': 6,
      }
      const phase = tacticMap[alert.mitre_tactic]
      if (phase !== undefined) {
        activePhases.add(phase)
      }
    }
  })

  return (
    <div className="glass-card p-4">
      <h3 className="font-heading text-sm text-neon-cyan mb-4">
        Attack Kill Chain
      </h3>

      <div className="flex flex-wrap items-center justify-center gap-1">
        {killChainPhases.map((phase, index) => {
          const isActive = activePhases.has(index)
          const isPast = index < Math.max(...activePhases, -1)
          
          return (
            <div key={phase.name} className="flex items-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="flex flex-col items-center"
              >
                <div 
                  className={`
                    w-6 h-6 rounded-full flex items-center justify-center text-[10px]
                    ${isActive 
                      ? 'bg-critical/20 border-2 border-critical' 
                      : isPast
                        ? 'bg-success/20 border-2 border-success'
                        : 'bg-bg-primary border-2 border-gray-700'
                    }
                  `}
                >
                  {isActive ? (
                    <Loader className="w-3 h-3 text-critical animate-spin" />
                  ) : isPast ? (
                    <CheckCircle className="w-3 h-3 text-success" />
                  ) : (
                    <Circle className="w-3 h-3 text-gray-600" />
                  )}
                </div>
                <span className={`text-[8px] mt-0.5 ${isActive ? 'text-critical' : 'text-gray-500'}`}>
                  {phase.short}
                </span>
              </motion.div>
              
              {index < killChainPhases.length - 1 && (
                <div 
                  className={`
                    h-0.5 w-4 mx-0.5
                    ${isPast ? 'bg-success' : 'bg-gray-700'}
                  `}
                />
              )}
            </div>
          )
        })}
      </div>

      <div className="mt-3 flex flex-wrap gap-1 justify-center">
        {killChainPhases.map((phase, index) => (
          <span 
            key={phase.name}
            className={`
              text-[8px] px-1.5 py-0.5 rounded whitespace-nowrap
              ${activePhases.has(index) 
                ? 'bg-critical/20 text-critical' 
                : 'bg-bg-primary text-gray-600'
              }
            `}
          >
            {phase.name}
          </span>
        ))}
      </div>
    </div>
  )
}