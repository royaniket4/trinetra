import { motion } from 'framer-motion'

export default function MitreBadge({ tactic, technique, tacticName, techniqueName }) {
  if (!technique) return null
  
  return (
    <motion.div
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className="group relative inline-flex"
    >
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-purple/20 border border-purple/50 text-purple text-xs font-mono">
        <span className="font-bold">{technique}</span>
        {tacticName && (
          <span className="text-purple/70 hidden group-hover:inline">→{tacticName}</span>
        )}
      </span>
      
      {(tacticName || techniqueName) && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-bg-secondary border border-purple/30 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50 min-w-[200px]">
          <div className="text-xs font-medium text-purple mb-1">{techniqueName || technique}</div>
          <div className="text-[10px] text-gray-400">{tacticName || tactic}</div>
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-2 h-2 bg-bg-secondary border-r border-b border-purple/30 rotate-45" />
        </div>
      )}
    </motion.div>
  )
}