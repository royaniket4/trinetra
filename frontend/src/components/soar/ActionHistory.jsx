import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  History, Shield, Ban, UserX, FileWarning, MonitorOff, Bell,
  CheckCircle, XCircle, Clock, AlertTriangle, ChevronDown, ChevronRight
} from 'lucide-react'
import GlassCard from '../common/GlassCard'
import { playbookApi, soarApi } from '../../services/api'

const actionIcons = {
  block_ip: Ban,
  disable_user: UserX,
  quarantine_file: FileWarning,
  isolate_endpoint: MonitorOff,
  notify: Bell,
}

export default function ActionHistory() {
  const [executions, setExecutions] = useState([])
  const [actions, setActions] = useState([])
  const [loading, setLoading] = useState(true)
  const [expandedExecution, setExpandedExecution] = useState(null)
  const [tab, setTab] = useState('playbooks')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [execRes, actRes] = await Promise.all([
          playbookApi.getExecutions(),
          soarApi.getActions({ limit: 30 }),
        ])
        setExecutions(execRes.data)
        setActions(actRes.data)
      } catch (err) {
        console.error('Failed to fetch history:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const handleToggleExecution = async (executionId) => {
    if (expandedExecution === executionId) {
      setExpandedExecution(null)
      return
    }
    
    try {
      const res = await playbookApi.getExecution(executionId)
      setExpandedExecution(res.data)
    } catch (err) {
      console.error('Failed to fetch execution detail:', err)
    }
  }

  if (loading) {
    return (
      <GlassCard>
        <div className="text-center py-8 text-gray-500">
          <History className="w-8 h-8 mx-auto mb-2 opacity-50" />
          Loading history...
        </div>
      </GlassCard>
    )
  }

  return (
    <GlassCard>
      <div className="flex items-center gap-2 mb-4">
        <History className="w-5 h-5 text-neon-cyan" />
        <h3 className="font-heading text-neon-cyan">Action History</h3>
      </div>

      <div className="flex gap-2 mb-4 border-b border-white/10 pb-2">
        <button
          onClick={() => setTab('playbooks')}
          className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
            tab === 'playbooks' ? 'bg-neon-cyan/20 text-neon-cyan' : 'text-gray-500 hover:text-white'
          }`}
        >
          Playbook Executions
        </button>
        <button
          onClick={() => setTab('actions')}
          className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
            tab === 'actions' ? 'bg-neon-cyan/20 text-neon-cyan' : 'text-gray-500 hover:text-white'
          }`}
        >
          Individual Actions
        </button>
      </div>

      {tab === 'playbooks' ? (
        <div className="space-y-2">
          {executions.length === 0 ? (
            <div className="text-center py-6 text-gray-500 text-sm">No playbook executions yet</div>
          ) : (
            executions.map((exec, idx) => (
              <motion.div
                key={exec.execution_id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
              >
                <div
                  className="flex items-center justify-between p-3 bg-bg-primary/50 rounded-lg hover:bg-bg-primary/70 transition-colors cursor-pointer"
                  onClick={() => handleToggleExecution(exec.execution_id)}
                >
                  <div className="flex items-center gap-3">
                    <Shield className="w-4 h-4 text-neon-cyan" />
                    <div>
                      <p className="text-sm text-white">{exec.playbook_name}</p>
                      <p className="text-xs text-gray-500 font-mono">{exec.execution_id}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      exec.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                      exec.status === 'partial_failure' ? 'bg-warning/20 text-warning' :
                      exec.status === 'running' ? 'bg-neon-cyan/20 text-neon-cyan' :
                      'bg-critical/20 text-critical'
                    }`}>
                      {exec.status.replace('_', ' ')}
                    </span>
                    {expandedExecution?.execution?.execution_id === exec.execution_id ? (
                      <ChevronDown className="w-4 h-4 text-gray-500" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-gray-500" />
                    )}
                  </div>
                </div>

                {expandedExecution?.execution?.execution_id === exec.execution_id && expandedExecution?.steps && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    className="ml-6 mt-2 space-y-1 overflow-hidden"
                  >
                    {expandedExecution.steps.map((step, sIdx) => (
                      <div key={sIdx} className="flex items-center gap-2 p-2 bg-bg-secondary/50 rounded-lg text-xs">
                        <span className="text-gray-500 w-4">{step.order}.</span>
                        <span className="text-gray-300 flex-1">{step.label}</span>
                        <span className="font-mono text-gray-500">{step.target}</span>
                        {step.status === 'completed' && <CheckCircle className="w-3.5 h-3.5 text-green-400" />}
                        {step.status === 'failed' && <XCircle className="w-3.5 h-3.5 text-critical" />}
                        {step.status === 'pending' && <Clock className="w-3.5 h-3.5 text-warning" />}
                        {step.status === 'denied' && <AlertTriangle className="w-3.5 h-3.5 text-critical" />}
                        {step.completed_at && (
                          <span className="text-gray-600">{new Date(step.completed_at).toLocaleTimeString()}</span>
                        )}
                      </div>
                    ))}
                  </motion.div>
                )}
              </motion.div>
            ))
          )}
        </div>
      ) : (
        <div className="space-y-2">
          {actions.length === 0 ? (
            <div className="text-center py-6 text-gray-500 text-sm">No actions executed yet</div>
          ) : (
            actions.map((action, idx) => {
              const Icon = actionIcons[action.action_type] || Shield
              return (
                <motion.div
                  key={action.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.03 }}
                  className="flex items-center justify-between p-3 bg-bg-primary/50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-lg bg-bg-primary flex items-center justify-center ${
                      action.action_type === 'block_ip' || action.action_type === 'disable_user'
                        ? 'text-critical' : 'text-warning'
                    }`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-sm text-white capitalize">
                        {action.action_type.replace('_', ' ')}
                      </p>
                      <p className="text-xs text-gray-500 font-mono">{action.target}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className={`text-xs ${
                      action.status === 'completed' ? 'text-green-400' : 'text-warning'
                    }`}>
                      {action.status}
                    </span>
                    <p className="text-xs text-gray-600 mt-0.5">
                      {new Date(action.executed_at).toLocaleString()}
                    </p>
                  </div>
                </motion.div>
              )
            })
          )}
        </div>
      )}
    </GlassCard>
  )
}
