import { useState, useEffect } from 'react'
import { Brain, AlertCircle, Activity, Clock, Zap } from 'lucide-react'
import api from '../../services/api'
import GlassCard from '../common/GlassCard'
import useStore from '../../store/useStore'

export default function ContextPanel() {
  const { aiHealth, aiContext } = useStore()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/stats/dashboard')
        setStats(response.data)
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
    const interval = setInterval(fetchStats, 30000)
    return () => clearInterval(interval)
  }, [])

  const isHealthy = aiHealth?.status === 'healthy'

  return (
    <GlassCard className="h-full flex flex-col">
      <div className="flex items-center gap-2 mb-4">
        <Brain className="w-5 h-5 text-neon-cyan" />
        <h3 className="font-heading text-neon-cyan">AI Context</h3>
      </div>

      <div className="space-y-4 flex-1 overflow-y-auto">
        <div className="p-3 rounded-lg bg-bg-primary/50">
          <div className="flex items-center gap-2 mb-2">
            <div className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-green-400' : 'bg-red-400'} animate-pulse`} />
            <span className="text-sm text-gray-300">Provider Status</span>
          </div>
          <div className="text-xs text-gray-500">
            {aiHealth?.provider || 'ollama'} • {aiHealth?.model || 'llama3.2:3b'}
          </div>
          {aiHealth?.latency && (
            <div className="text-xs text-gray-500 mt-1">
              Latency: {aiHealth.latency}ms
            </div>
          )}
        </div>

        {aiContext?.alert_id && (
          <div className="p-3 rounded-lg bg-bg-primary/50">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-4 h-4 text-neon-cyan" />
              <span className="text-sm text-gray-300">Selected Alert</span>
            </div>
            <div className="text-xs text-gray-400 font-mono">
              ID: #{aiContext.alert_id}
            </div>
            <div className="text-xs text-gray-500">
              Workflow: {aiContext.workflow}
            </div>
          </div>
        )}

        {aiContext?.alert_ids?.length > 0 && (
          <div className="p-3 rounded-lg bg-bg-primary/50">
            <div className="flex items-center gap-2 mb-2">
              <AlertCircle className="w-4 h-4 text-neon-cyan" />
              <span className="text-sm text-gray-300">Selected Alerts</span>
            </div>
            <div className="text-xs text-gray-400">
              {aiContext.alert_ids.length} alerts selected
            </div>
          </div>
        )}

        {!aiContext?.alert_id && !aiContext?.alert_ids?.length && (
          <div className="p-3 rounded-lg bg-bg-primary/50">
            <div className="text-xs text-gray-500 mb-2">Current Context</div>
            <div className="text-sm text-gray-400">General chat mode</div>
          </div>
        )}

        <div className="p-3 rounded-lg bg-bg-primary/50">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="w-4 h-4 text-neon-cyan" />
            <span className="text-sm text-gray-300">Platform Stats</span>
          </div>
          {loading ? (
            <div className="text-xs text-gray-500">Loading...</div>
          ) : stats ? (
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-500">Active Alerts</span>
                <span className="text-gray-300">{stats.total_alerts_24h || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Critical (1h)</span>
                <span className="text-red-400">{stats.critical_alerts_24h || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Incidents</span>
                <span className="text-gray-300">{stats.active_incidents || 0}</span>
              </div>
            </div>
          ) : (
            <div className="text-xs text-gray-500">Unavailable</div>
          )}
        </div>

        <div className="p-3 rounded-lg bg-bg-primary/50">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="w-4 h-4 text-neon-cyan" />
            <span className="text-sm text-gray-300">Session Stats</span>
          </div>
          <div className="text-xs text-gray-400">
            Tokens: {tokenCount || 0}
          </div>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-white/10">
        <div className="text-xs text-gray-500 text-center">
          TrinetraMind v4.0 • Privacy-first AI
        </div>
      </div>
    </GlassCard>
  )
}