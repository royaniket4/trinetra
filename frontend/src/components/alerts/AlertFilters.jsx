import { useState, useEffect } from 'react'
import { X, Filter } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

const severityOptions = [
  { value: 5, label: 'Critical' },
  { value: 4, label: 'High' },
  { value: 3, label: 'Medium' },
  { value: 2, label: 'Low' },
  { value: 1, label: 'Info' },
]

const statusOptions = [
  { value: 'all', label: 'All Status' },
  { value: 'open', label: 'Open' },
  { value: 'investigating', label: 'Investigating' },
  { value: 'closed', label: 'Closed' },
]

export default function AlertFilters({ filters, onFilterChange, onClear }) {
  const [localSourceIp, setLocalSourceIp] = useState(filters.source_ip)
  
  useEffect(() => {
    const timeout = setTimeout(() => {
      if (localSourceIp !== filters.source_ip) {
        onFilterChange({ source_ip: localSourceIp })
      }
    }, 300)
    return () => clearTimeout(timeout)
  }, [localSourceIp])

  const handleSeverityToggle = (severity) => {
    const newSeverity = filters.severity.includes(severity)
      ? filters.severity.filter(s => s !== severity)
      : [...filters.severity, severity]
    onFilterChange({ severity: newSeverity })
  }

  const hasActiveFilters = filters.severity.length > 0 || 
    filters.status !== 'all' || 
    filters.source_ip

  return (
    <div className="glass-card p-4 mb-4">
      <div className="flex items-center gap-2 mb-3">
        <Filter className="w-4 h-4 text-neon-cyan" />
        <span className="font-heading text-sm text-neon-cyan">Filters</span>
        {hasActiveFilters && (
          <button
            onClick={onClear}
            className="ml-auto text-xs text-gray-500 hover:text-white flex items-center gap-1"
          >
            <X className="w-3 h-3" />
            Clear
          </button>
        )}
      </div>
      
      <div className="flex flex-wrap gap-3">
        <div className="flex flex-wrap gap-1">
          {severityOptions.map(opt => (
            <button
              key={opt.value}
              onClick={() => handleSeverityToggle(opt.value)}
              className={`
                px-2.5 py-1 rounded text-xs font-medium transition-all
                ${filters.severity.includes(opt.value)
                  ? 'bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/50'
                  : 'bg-bg-primary text-gray-400 border border-white/10 hover:border-white/20'
                }
              `}
            >
              {opt.label}
            </button>
          ))}
        </div>
        
        <select
          value={filters.status}
          onChange={(e) => onFilterChange({ status: e.target.value })}
          className="bg-bg-primary border border-white/10 rounded px-3 py-1 text-xs text-white focus:outline-none focus:border-neon-cyan/50"
        >
          {statusOptions.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
        
        <input
          type="text"
          placeholder="Search by IP..."
          value={localSourceIp}
          onChange={(e) => setLocalSourceIp(e.target.value)}
          className="bg-bg-primary border border-white/10 rounded px-3 py-1 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan/50 w-32"
        />
      </div>
    </div>
  )
}