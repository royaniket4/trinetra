import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Play, AlertTriangle, CheckCircle, XCircle, Clock, 
  Shield, Ban, UserX, FileWarning, MonitorOff, Bell,
  ChevronRight, Loader, Siren
} from 'lucide-react'
import GlassCard from '../common/GlassCard'
import NeonButton from '../common/NeonButton'
import { playbookApi } from '../../services/api'

const actionIcons = {
  block_ip: Ban,
  disable_user: UserX,
  quarantine_file: FileWarning,
  isolate_endpoint: MonitorOff,
  notify: Bell,
}

const actionColors = {
  block_ip: 'text-critical',
  disable_user: 'text-critical',
  quarantine_file: 'text-warning',
  isolate_endpoint: 'text-warning',
  notify: 'text-neon-cyan',
}

export default function PlaybookEngine() {
  const [playbooks, setPlaybooks] = useState([])
  const [executionResult, setExecutionResult] = useState(null)
  const [selectedPlaybook, setSelectedPlaybook] = useState(null)
  const [alertId, setAlertId] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    playbookApi.getPlaybooks().then(res => setPlaybooks(res.data)).catch(() => {})
  }, [])

  const handleTrigger = async () => {
    if (!alertId.trim()) return
    setLoading(true)
    setExecutionResult(null)
    
    try {
      const res = await playbookApi.trigger(parseInt(alertId))
      setExecutionResult(res.data)
    } catch (err) {
      setExecutionResult({ status: 'error', error: err.response?.data?.detail || 'Failed to trigger playbook' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <GlassCard>
        <div className="flex items-center gap-2 mb-4">
          <Siren className="w-5 h-5 text-neon-cyan" />
          <h3 className="font-heading text-neon-cyan">Trigger Playbook</h3>
        </div>
        <p className="text-sm text-gray-500 mb-4">Enter an Alert ID to automatically execute the matching response playbook</p>
        
        <div className="flex gap-3">
          <input
            type="number"
            value={alertId}
            onChange={(e) => setAlertId(e.target.value)}
            placeholder="Alert ID (e.g., 1)"
            className="flex-1 bg-bg-primary border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan/50"
          />
          <NeonButton onClick={handleTrigger} disabled={loading || !alertId.trim()}>
            {loading ? <Loader className="w-4 h-4 animate-spin mr-1" /> : <Play className="w-4 h-4 mr-1" />}
            Execute Playbook
          </NeonButton>
        </div>
      </GlassCard>

      <AnimatePresence>
        {executionResult && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            <GlassCard>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Shield className="w-5 h-5 text-neon-cyan" />
                  <h3 className="font-heading text-neon-cyan">{executionResult.playbook_name || 'Execution Result'}</h3>
                </div>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  executionResult.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                  executionResult.status === 'partial_failure' ? 'bg-warning/20 text-warning' :
                  executionResult.status === 'running' ? 'bg-neon-cyan/20 text-neon-cyan' :
                  'bg-critical/20 text-critical'
                }`}>
                  {executionResult.status?.replace('_', ' ').toUpperCase()}
                </span>
              </div>

              {executionResult.steps && (
                <div className="space-y-2">
                  {executionResult.steps.map((step, idx) => {
                    const Icon = actionIcons[step.step?.action_type] || Shield
                    const color = actionColors[step.step?.action_type] || 'text-gray-400'

                    return (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="flex items-center justify-between p-3 bg-bg-primary/50 rounded-lg"
                      >
                        <div className="flex items-center gap-3">
                          <div className={`w-8 h-8 rounded-lg bg-bg-primary flex items-center justify-center ${color}`}>
                            <Icon className="w-4 h-4" />
                          </div>
                          <div>
                            <p className="text-sm text-white">{step.step?.label || step.step?.action_type}</p>
                            <p className="text-xs text-gray-500 font-mono">{step.target || step.step?.target}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {step.status === 'completed' && <CheckCircle className="w-5 h-5 text-green-400" />}
                          {step.status === 'failed' && <XCircle className="w-5 h-5 text-critical" />}
                          {step.status === 'pending_approval' && <Clock className="w-5 h-5 text-warning animate-pulse" />}
                          {step.status === 'skipped' && <AlertTriangle className="w-5 h-5 text-gray-500" />}
                          <span className="text-xs text-gray-500 capitalize">{step.status.replace('_', ' ')}</span>
                        </div>
                      </motion.div>
                    )
                  })}
                </div>
              )}

              {executionResult.error && (
                <div className="p-3 bg-critical/10 border border-critical/30 rounded-lg text-critical text-sm mt-2">
                  {executionResult.error}
                </div>
              )}
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>

      <GlassCard>
        <div className="flex items-center gap-2 mb-4">
          <Shield className="w-5 h-5 text-neon-cyan" />
          <h3 className="font-heading text-neon-cyan">Available Playbooks</h3>
        </div>

        <div className="grid gap-4">
          {playbooks.map(pb => (
            <motion.div
              key={pb.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-4 bg-bg-primary/50 rounded-lg hover:bg-bg-primary/70 transition-colors cursor-pointer"
              onClick={() => setSelectedPlaybook(selectedPlaybook === pb.id ? null : pb.id)}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-white font-medium">{pb.name}</h4>
                  <p className="text-xs text-gray-500 mt-1">{pb.description}</p>
                </div>
                <ChevronRight className={`w-5 h-5 text-gray-500 transition-transform ${
                  selectedPlaybook === pb.id ? 'rotate-90' : ''
                }`} />
              </div>

              <AnimatePresence>
                {selectedPlaybook === pb.id && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="mt-4 space-y-2 overflow-hidden"
                  >
                    <div className="text-xs text-gray-500 mb-2">
                      Trigger: {pb.trigger_conditions?.rule_names?.join(', ')} | Min Severity: {pb.trigger_conditions?.min_severity}
                    </div>
                    {pb.steps?.map((step, idx) => {
                      const StepIcon = actionIcons[step.action_type] || Shield
                      return (
                        <div key={idx} className="flex items-center gap-3 p-2 bg-bg-secondary/50 rounded-lg">
                          <div className="w-6 h-6 rounded bg-bg-primary flex items-center justify-center">
                            <span className="text-xs text-gray-500">{step.order}</span>
                          </div>
                          <StepIcon className={`w-4 h-4 ${actionColors[step.action_type] || 'text-gray-400'}`} />
                          <span className="text-sm text-gray-300 flex-1">{step.label}</span>
                          {step.requires_approval && (
                            <span className="text-xs text-warning flex items-center gap-1">
                              <Clock className="w-3 h-3" /> Approval
                            </span>
                          )}
                        </div>
                      )
                    })}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      </GlassCard>
    </div>
  )
}
