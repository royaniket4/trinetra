import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown } from 'lucide-react'

export default function StatCard({ 
  title, 
  value, 
  icon: Icon, 
  trend = null,
  color = 'cyan',
  className = ''
}) {
  const colors = {
    cyan: 'text-neon-cyan',
    blue: 'text-electric-blue',
    green: 'text-success',
    red: 'text-critical',
    orange: 'text-warning',
    purple: 'text-purple',
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`glass-card p-4 ${className}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-gray-400 mb-1">{title}</p>
          <p className={`text-2xl font-bold font-heading ${colors[color]}`}>
            {value?.toLocaleString() || 0}
          </p>
        </div>
        {Icon && (
          <div className={`p-2 rounded-lg bg-${color}-cyan/10`}>
            <Icon className={`w-5 h-5 ${colors[color]}`} />
          </div>
        )}
      </div>
      {trend !== null && (
        <div className="mt-2 flex items-center gap-1 text-xs">
          {trend > 0 ? (
            <TrendingUp className="w-3 h-3 text-critical" />
          ) : (
            <TrendingDown className="w-3 h-3 text-success" />
          )}
          <span className={trend > 0 ? 'text-critical' : 'text-success'}>
            {Math.abs(trend)}% vs last hour
          </span>
        </div>
      )}
    </motion.div>
  )
}