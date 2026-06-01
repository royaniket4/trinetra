import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Shield, Ban, UserX, FileWarning, MonitorOff, Play, History } from 'lucide-react'
import GlassCard from '../common/GlassCard'
import NeonButton from '../common/NeonButton'
import { soarApi } from '../../services/api'

const actionTypes = [
  { id: 'block_ip', label: 'Block IP', icon: Ban, color: 'danger' },
  { id: 'disable_user', label: 'Disable User', icon: UserX, color: 'danger' },
  { id: 'quarantine_file', label: 'Quarantine File', icon: FileWarning, color: 'warning' },
  { id: 'isolate_endpoint', label: 'Isolate Endpoint', icon: MonitorOff, color: 'warning' },
]

export default function ResponseActions() {
  const [actions, setActions] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [selectedAction, setSelectedAction] = useState(null)
  const [target, setTarget] = useState('')

  const fetchActions = async () => {
    try {
      const response = await soarApi.getActions({ limit: 20 })
      setActions(response.data)
    } catch (error) {
      console.error('Failed to fetch actions:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchActions()
  }, [])

  const executeAction = async () => {
    if (!target.trim()) return
    
    try {
      await soarApi.executeAction({
        action_type: selectedAction,
        target: target,
        triggered_by: 'manual',
      })
      setTarget('')
      setShowModal(false)
      fetchActions()
    } catch (error) {
      console.error('Failed to execute action:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {actionTypes.map(action => (
          <motion.button
            key={action.id}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => {
              setSelectedAction(action.id)
              setShowModal(true)
            }}
            className="glass-card p-4 hover:border-white/20 transition-colors text-center"
          >
            <action.icon className={`w-8 h-8 mx-auto mb-2 ${
              action.color === 'danger' ? 'text-critical' : 'text-warning'
            }`} />
            <span className="text-sm font-medium">{action.label}</span>
          </motion.button>
        ))}
      </div>

      <GlassCard>
        <div className="flex items-center gap-2 mb-4">
          <History className="w-5 h-5 text-neon-cyan" />
          <h3 className="font-heading text-neon-cyan">Recent Actions</h3>
        </div>

        {loading ? (
          <div className="text-center py-8 text-gray-500">Loading...</div>
        ) : actions.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No response actions yet
          </div>
        ) : (
          <div className="space-y-2">
            {actions.map((action, index) => (
              <motion.div
                key={action.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-center justify-between p-3 bg-bg-primary/50 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                    action.action_type === 'block_ip' ? 'bg-critical/20' :
                    action.action_type === 'disable_user' ? 'bg-critical/20' :
                    'bg-warning/20'
                  }`}>
                    {action.action_type === 'block_ip' && <Ban className="w-4 h-4 text-critical" />}
                    {action.action_type === 'disable_user' && <UserX className="w-4 h-4 text-critical" />}
                    {action.action_type === 'quarantine_file' && <FileWarning className="w-4 h-4 text-warning" />}
                    {action.action_type === 'isolate_endpoint' && <MonitorOff className="w-4 h-4 text-warning" />}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white">
                      {action.action_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </p>
                    <p className="text-xs text-gray-500 font-mono">{action.target}</p>
                  </div>
                </div>
                <div className="text-right">
                  <span className={`text-xs ${
                    action.status === 'completed' ? 'text-success' : 'text-warning'
                  }`}>
                    {action.status}
                  </span>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(action.executed_at).toLocaleString()}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </GlassCard>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card p-6 w-full max-w-md"
          >
            <h3 className="text-lg font-heading text-white mb-4">
              Execute {actionTypes.find(a => a.id === selectedAction)?.label}
            </h3>
            <input
              type="text"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              placeholder={
                selectedAction === 'block_ip' ? 'IP Address (e.g., 192.168.1.100)' :
                selectedAction === 'disable_user' ? 'Username (e.g., admin)' :
                selectedAction === 'quarantine_file' ? 'File path' :
                'Hostname or IP'
              }
              className="w-full bg-bg-primary border border-white/10 rounded-lg px-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan/50 mb-4"
            />
            <div className="flex gap-2 justify-end">
              <NeonButton variant="secondary" onClick={() => setShowModal(false)}>
                Cancel
              </NeonButton>
              <NeonButton onClick={executeAction}>
                <Play className="w-4 h-4 mr-1" />
                Execute
              </NeonButton>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  )
}