import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Clock, CheckCircle, XCircle, Shield, Ban, UserX, 
  FileWarning, MonitorOff, Bell, Loader
} from 'lucide-react'
import GlassCard from '../common/GlassCard'
import NeonButton from '../common/NeonButton'
import { playbookApi } from '../../services/api'

const actionLabels = {
  block_ip: 'Block IP',
  disable_user: 'Disable User',
  quarantine_file: 'Quarantine File',
  isolate_endpoint: 'Isolate Endpoint',
  notify: 'Send Notification',
}

const actionIcons = {
  block_ip: Ban,
  disable_user: UserX,
  quarantine_file: FileWarning,
  isolate_endpoint: MonitorOff,
  notify: Bell,
}

export default function ApprovalQueue() {
  const [pendingSteps, setPendingSteps] = useState([])
  const [loading, setLoading] = useState(true)
  const [responding, setResponding] = useState(null)

  const fetchPending = async () => {
    try {
      const res = await playbookApi.getPendingApprovals()
      setPendingSteps(res.data)
    } catch (err) {
      console.error('Failed to fetch pending approvals:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPending()
    const interval = setInterval(fetchPending, 10000)
    return () => clearInterval(interval)
  }, [])

  const handleRespond = async (stepId, approved) => {
    setResponding(stepId)
    try {
      await playbookApi.respondApproval(stepId, approved)
      setPendingSteps(prev => prev.filter(s => s.id !== stepId))
    } catch (err) {
      console.error('Failed to respond:', err)
    } finally {
      setResponding(null)
    }
  }

  return (
    <GlassCard>
      <div className="flex items-center gap-2 mb-4">
        <Clock className="w-5 h-5 text-warning" />
        <h3 className="font-heading text-warning">Pending Approvals</h3>
        {pendingSteps.length > 0 && (
          <span className="px-2 py-0.5 text-xs bg-warning/20 text-warning rounded-full animate-pulse">
            {pendingSteps.length}
          </span>
        )}
      </div>

      {loading ? (
        <div className="text-center py-8 text-gray-500">
          <Loader className="w-6 h-6 animate-spin mx-auto mb-2" />
          Loading approvals...
        </div>
      ) : pendingSteps.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <CheckCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p>No pending approvals</p>
          <p className="text-xs mt-1">All actions have been processed</p>
        </div>
      ) : (
        <div className="space-y-3">
          <AnimatePresence>
            {pendingSteps.map((step) => {
              const Icon = actionIcons[step.action_type] || Shield
              return (
                <motion.div
                  key={step.id}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, height: 0, marginBottom: 0 }}
                  className="p-4 bg-bg-primary/50 rounded-lg border border-warning/20"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-lg bg-warning/20 flex items-center justify-center">
                      <Icon className="w-5 h-5 text-warning" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-white font-medium">{actionLabels[step.action_type] || step.action_type}</span>
                        <span className="px-1.5 py-0.5 text-xs bg-bg-primary rounded text-gray-500">{step.playbook_name}</span>
                      </div>
                      <p className="text-sm font-mono text-gray-400 mt-1">{step.target}</p>
                      <p className="text-xs text-gray-600 mt-1">
                        {step.label} • Step {step.order}
                      </p>
                      <p className="text-xs text-gray-600">
                        {new Date(step.started_at).toLocaleString()}
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-2 mt-3 pt-3 border-t border-white/10">
                    <NeonButton
                      variant="danger"
                      size="sm"
                      className="flex-1"
                      disabled={responding === step.id}
                      onClick={() => handleRespond(step.id, false)}
                    >
                      {responding === step.id ? (
                        <Loader className="w-4 h-4 animate-spin mr-1" />
                      ) : (
                        <XCircle className="w-4 h-4 mr-1" />
                      )}
                      Deny
                    </NeonButton>
                    <NeonButton
                      variant="success"
                      size="sm"
                      className="flex-1"
                      disabled={responding === step.id}
                      onClick={() => handleRespond(step.id, true)}
                    >
                      {responding === step.id ? (
                        <Loader className="w-4 h-4 animate-spin mr-1" />
                      ) : (
                        <CheckCircle className="w-4 h-4 mr-1" />
                      )}
                      Approve
                    </NeonButton>
                  </div>
                </motion.div>
              )
            })}
          </AnimatePresence>
        </div>
      )}
    </GlassCard>
  )
}
