import { Zap, AlertTriangle, Target, FileText, Globe } from 'lucide-react'

const quickActions = [
  { 
    label: 'Critical alerts in last hour', 
    icon: AlertTriangle,
    query: 'Show me critical alerts in last hour'
  },
  { 
    label: 'Explain recent alert', 
    icon: Zap,
    query: 'Explain the most recent alert'
  },
  { 
    label: 'Top MITRE technique', 
    icon: Target,
    query: 'What is the top MITRE technique today?'
  },
  { 
    label: 'Threat brief', 
    icon: FileText,
    query: 'Generate a threat brief'
  },
  { 
    label: 'Failed SSH from Russia', 
    icon: Globe,
    query: 'Show failed SSH logins from Russia'
  },
]

export default function QuickActions({ onSelect, disabled }) {
  return (
    <div className="flex flex-wrap gap-2 mb-3">
      {quickActions.map((action, index) => (
        <button
          key={index}
          onClick={() => onSelect(action.query)}
          disabled={disabled}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-full 
            bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white 
            border border-white/10 hover:border-white/20 transition-all
            disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <action.icon className="w-3.5 h-3.5" />
          <span>{action.label}</span>
        </button>
      ))}
    </div>
  )
}