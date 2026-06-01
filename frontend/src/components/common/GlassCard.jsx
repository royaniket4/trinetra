import { motion } from 'framer-motion'

export default function GlassCard({ 
  children, 
  className = '', 
  hover = false,
  glow = false,
  onClick
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`
        glass-card p-4
        ${hover ? 'hover:border-neon-cyan/30 hover:shadow-[0_0_20px_rgba(0,229,255,0.1)] transition-all cursor-pointer' : ''}
        ${glow ? 'neon-border' : ''}
        ${onClick ? 'cursor-pointer' : ''}
        ${className}
      `}
      onClick={onClick}
    >
      {children}
    </motion.div>
  )
}