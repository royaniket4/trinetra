import { motion } from 'framer-motion'

export default function NeonButton({ 
  children, 
  onClick, 
  variant = 'primary',
  size = 'md',
  disabled = false,
  className = '',
}) {
  const variants = {
    primary: 'bg-neon-cyan/20 border-neon-cyan/50 text-neon-cyan hover:bg-neon-cyan/30',
    secondary: 'bg-electric-blue/20 border-electric-blue/50 text-electric-blue hover:bg-electric-blue/30',
    danger: 'bg-critical/20 border-critical/50 text-critical hover:bg-critical/30',
    success: 'bg-success/20 border-success/50 text-success hover:bg-success/30',
  }

  const sizes = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  }

  return (
    <motion.button
      whileHover={{ scale: disabled ? 1 : 1.02 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
      onClick={onClick}
      disabled={disabled}
      className={`
        font-medium rounded-lg border transition-all
        disabled:opacity-50 disabled:cursor-not-allowed
        ${variants[variant]}
        ${sizes[size]}
        ${className}
      `}
    >
      {children}
    </motion.button>
  )
}