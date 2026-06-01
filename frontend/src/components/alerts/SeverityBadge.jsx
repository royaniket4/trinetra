import { motion } from 'framer-motion'

const severityConfig = {
  5: { label: 'CRITICAL', color: 'text-critical', bg: 'bg-critical/20', border: 'border-critical', glow: 'shadow-[0_0_10px_rgba(255,59,59,0.5)]' },
  4: { label: 'HIGH', color: 'text-warning', bg: 'bg-warning/20', border: 'border-warning', glow: 'shadow-[0_0_8px_rgba(255,176,32,0.4)]' },
  3: { label: 'MEDIUM', color: 'text-yellow-400', bg: 'bg-yellow-400/20', border: 'border-yellow-400', glow: '' },
  2: { label: 'LOW', color: 'text-electric-blue', bg: 'bg-electric-blue/20', border: 'border-electric-blue', glow: '' },
  1: { label: 'INFO', color: 'text-gray-400', bg: 'bg-gray-400/20', border: 'border-gray-400', glow: '' },
}

export default function SeverityBadge({ severity = 1, showLabel = true }) {
  const config = severityConfig[severity] || severityConfig[1]
  
  return (
    <motion.span
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className={`
        inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full
        font-heading text-[10px] font-bold uppercase tracking-wider
        ${config.color} ${config.bg} ${config.border}
        ${severity === 5 ? config.glow : ''}
      `}
    >
      {severity === 5 && (
        <span className="w-1.5 h-1.5 rounded-full bg-critical animate-pulse" />
      )}
      {showLabel && config.label}
    </motion.span>
  )
}