import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Activity, AlertTriangle, Users, Zap, Shield, 
  Brain, Loader, CheckCircle, XCircle, TrendingUp,
  Clock, Eye, User, Server
} from 'lucide-react'
import GlassCard from '../components/common/GlassCard'
import NeonButton from '../components/common/NeonButton'
import { detectionApi } from '../services/api'

const tabs = [
  { id: 'correlation', label: 'Correlation Rules', icon: Brain },
  { id: 'results', label: 'Correlation Results', icon: Activity },
  { id: 'users', label: 'User Analytics', icon: Users },
  { id: 'anomalies', label: 'Anomaly Detection', icon: TrendingUp },
  { id: 'custom', label: 'Custom Rules', icon: Shield },
]

export default function Detection() {
  const [activeTab, setActiveTab] = useState('correlation')
  const [correlationRules, setCorrelationRules] = useState([])
  const [correlationResults, setCorrelationResults] = useState([])
  const [userScores, setUserScores] = useState([])
  const [anomalies, setAnomalies] = useState(null)
  const [customRules, setCustomRules] = useState([])
  const [loading, setLoading] = useState({})
  const [runResult, setRunResult] = useState(null)

  useEffect(() => {
    fetchCorrelationRules()
    fetchCorrelationResults()
    fetchUserScores()
    fetchAnomalies()
    fetchCustomRules()
  }, [])

  const fetchCorrelationRules = async () => {
    try {
      const res = await detectionApi.getCorrelationRules()
      setCorrelationRules(res.data)
    } catch (e) { console.error(e) }
  }

  const fetchCorrelationResults = async () => {
    try {
      const res = await detectionApi.getCorrelationResults()
      setCorrelationResults(res.data)
    } catch (e) { console.error(e) }
  }

  const fetchUserScores = async () => {
    try {
      const res = await detectionApi.getUserRiskScores()
      setUserScores(res.data)
    } catch (e) { console.error(e) }
  }

  const fetchAnomalies = async () => {
    try {
      const res = await detectionApi.getAnomalies()
      setAnomalies(res.data)
    } catch (e) { console.error(e) }
  }

  const fetchCustomRules = async () => {
    try {
      const res = await detectionApi.getRules()
      setCustomRules(res.data)
    } catch (e) { console.error(e) }
  }

  const handleRunCorrelation = async () => {
    setLoading(prev => ({ ...prev, correlation: true }))
    try {
      const res = await detectionApi.runCorrelation()
      setRunResult(res.data)
      fetchCorrelationResults()
    } catch (e) { console.error(e) }
    finally { setLoading(prev => ({ ...prev, correlation: false })) }
  }

  const getRiskColor = (level) => {
    switch (level) {
      case 'critical': return 'text-critical bg-critical/10 border-critical/30'
      case 'high': return 'text-warning bg-warning/10 border-warning/30'
      case 'medium': return 'text-electric-blue bg-electric-blue/10 border-electric-blue/30'
      default: return 'text-green-400 bg-green-400/10 border-green-400/30'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-neon-cyan/20 flex items-center justify-center">
          <Shield className="w-6 h-6 text-neon-cyan" />
        </div>
        <div>
          <h1 className="text-2xl font-heading font-bold text-white">Advanced Detection</h1>
          <p className="text-sm text-gray-500">Multi-event correlation, user analytics, and anomaly detection</p>
        </div>
      </div>

      <div className="flex gap-2 border-b border-white/10 pb-2 overflow-x-auto">
        {tabs.map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm whitespace-nowrap transition-colors ${
              activeTab === tab.id ? 'bg-neon-cyan/20 text-neon-cyan' : 'text-gray-500 hover:text-white'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'correlation' && (
        <div className="space-y-4">
          <GlassCard>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Brain className="w-5 h-5 text-neon-cyan" />
                <h3 className="font-heading text-neon-cyan">Multi-Event Correlation Rules</h3>
              </div>
              <NeonButton onClick={handleRunCorrelation} disabled={loading.correlation}>
                {loading.correlation ? <Loader className="w-4 h-4 animate-spin mr-1" /> : <Zap className="w-4 h-4 mr-1" />}
                Run Correlation
              </NeonButton>
            </div>

            <AnimatePresence>
              {runResult && (
                <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                  className={`p-3 mb-4 rounded-lg text-sm ${
                    runResult.alerts_generated > 0 ? 'bg-warning/10 border border-warning/30 text-warning' : 'bg-green-400/10 border border-green-400/30 text-green-400'
                  }`}
                >
                  {runResult.alerts_generated > 0
                    ? `Generated ${runResult.alerts_generated} correlation alert(s): ${runResult.alert_ids?.join(', ')}`
                    : 'No correlation matches found'}
                </motion.div>
              )}
            </AnimatePresence>

            <div className="grid gap-3">
              {correlationRules.map((rule, idx) => (
                <motion.div key={idx} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="p-4 bg-bg-primary/50 rounded-lg border border-white/10"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        rule.severity >= 5 ? 'bg-critical/20' : rule.severity >= 4 ? 'bg-warning/20' : 'bg-neon-cyan/20'
                      }`}>
                        <Brain className={`w-5 h-5 ${
                          rule.severity >= 5 ? 'text-critical' : rule.severity >= 4 ? 'text-warning' : 'text-neon-cyan'
                        }`} />
                      </div>
                      <div>
                        <h4 className="text-white font-medium">{rule.name}</h4>
                        <p className="text-xs text-gray-500 mt-1">{rule.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 text-xs">
                      <span className={`px-2 py-0.5 rounded-full ${
                        rule.severity >= 5 ? 'bg-critical/20 text-critical' : rule.severity >= 4 ? 'bg-warning/20 text-warning' : 'bg-neon-cyan/20 text-neon-cyan'
                      }`}>
                        Sev {rule.severity}
                      </span>
                      <span className="text-gray-500">{rule.time_window_minutes}m window</span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </GlassCard>
        </div>
      )}

      {activeTab === 'results' && (
        <GlassCard>
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-5 h-5 text-neon-cyan" />
            <h3 className="font-heading text-neon-cyan">Correlation Results (24h)</h3>
            <span className="px-2 py-0.5 text-xs bg-neon-cyan/20 text-neon-cyan rounded-full">{correlationResults.length}</span>
          </div>

          {correlationResults.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Brain className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>No correlation alerts yet</p>
              <p className="text-xs mt-1">Run correlation rules or wait for real-time processing</p>
            </div>
          ) : (
            <div className="space-y-2">
              {correlationResults.map((result, idx) => (
                <motion.div key={idx} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.03 }}
                  className="flex items-center justify-between p-3 bg-bg-primary/50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <AlertTriangle className={`w-4 h-4 ${result.severity >= 5 ? 'text-critical' : 'text-warning'}`} />
                    <div>
                      <p className="text-sm text-white">{result.rule_name}</p>
                      <p className="text-xs text-gray-500">{result.source_ip && `Source: ${result.source_ip} • `}{result.timestamp && new Date(result.timestamp).toLocaleString()}</p>
                    </div>
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    result.severity >= 5 ? 'bg-critical/20 text-critical' : result.severity >= 4 ? 'bg-warning/20 text-warning' : 'bg-neon-cyan/20 text-neon-cyan'
                  }`}>
                    Sev {result.severity}
                  </span>
                </motion.div>
              ))}
            </div>
          )}
        </GlassCard>
      )}

      {activeTab === 'users' && (
        <GlassCard>
          <div className="flex items-center gap-2 mb-4">
            <Users className="w-5 h-5 text-neon-cyan" />
            <h3 className="font-heading text-neon-cyan">User Risk Scores</h3>
            <span className="px-2 py-0.5 text-xs bg-neon-cyan/20 text-neon-cyan rounded-full">{userScores.length} users</span>
          </div>

          {userScores.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <User className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>No user risk data available</p>
            </div>
          ) : (
            <div className="space-y-2">
              {userScores.map((user, idx) => (
                <motion.div key={idx} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="flex items-center justify-between p-3 bg-bg-primary/50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-bg-primary flex items-center justify-center">
                      <User className="w-4 h-4 text-neon-cyan" />
                    </div>
                    <div>
                      <p className="text-sm text-white">{user.username}</p>
                      <p className="text-xs text-gray-500">{user.alerts_last_24h} alerts in 24h • {user.alerts_last_hour} in last hour</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className={`px-2 py-0.5 text-xs rounded-full border ${getRiskColor(user.risk_level)}`}>
                      {user.risk_level.toUpperCase()} ({user.risk_score})
                    </span>
                    {user.top_alert_types?.length > 0 && (
                      <p className="text-xs text-gray-600 mt-1">{user.top_alert_types.slice(0, 2).join(', ')}</p>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </GlassCard>
      )}

      {activeTab === 'anomalies' && (
        <div className="space-y-4">
          <GlassCard>
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-5 h-5 text-neon-cyan" />
              <h3 className="font-heading text-neon-cyan">Anomaly Detection</h3>
            </div>

            <div className="grid gap-3">
              {anomalies?.anomalies?.length > 0 ? (
                anomalies.anomalies.map((anomaly, idx) => (
                  <motion.div key={idx} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                    className={`p-4 rounded-lg border ${
                      anomaly.severity === 'high' ? 'bg-critical/10 border-critical/30' : 'bg-warning/10 border-warning/30'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      {anomaly.severity === 'high' ? (
                        <AlertTriangle className="w-5 h-5 text-critical" />
                      ) : (
                        <Zap className="w-5 h-5 text-warning" />
                      )}
                      <span className={`font-medium ${anomaly.severity === 'high' ? 'text-critical' : 'text-warning'}`}>
                        {anomaly.type?.replace('_', ' ').toUpperCase()}
                      </span>
                      <span className={`ml-auto text-xs px-2 py-0.5 rounded-full ${
                        anomaly.severity === 'high' ? 'bg-critical/20 text-critical' : 'bg-warning/20 text-warning'
                      }`}>
                        {anomaly.severity}
                      </span>
                    </div>
                    <p className="text-sm text-gray-300">{anomaly.description}</p>
                    {anomaly.z_score && (
                      <p className="text-xs text-gray-500 mt-1">Z-score: {anomaly.z_score} | Expected: {anomaly.expected_mean} | Actual: {anomaly.current_count}</p>
                    )}
                    {anomaly.ratio && (
                      <p className="text-xs text-gray-500 mt-1">{anomaly.recent_count} recent vs {anomaly.previous_count} previous ({anomaly.ratio}x increase)</p>
                    )}
                  </motion.div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <CheckCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>No anomalies detected</p>
                  <p className="text-xs mt-1">Baseline normal behavior established</p>
                </div>
              )}
            </div>

            {anomalies?.baseline && (
              <div className="mt-4 p-3 bg-bg-primary/50 rounded-lg">
                <div className="text-xs text-gray-500 mb-2">Volume Baseline</div>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <div className="text-xs text-gray-600">Mean (per hour)</div>
                    <div className="text-sm text-white">{Math.round(anomalies.baseline.mean)}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-600">Std Deviation</div>
                    <div className="text-sm text-white">{Math.round(anomalies.baseline.std)}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-600">Hours Analyzed</div>
                    <div className="text-sm text-white">{anomalies.baseline.total_hours}</div>
                  </div>
                </div>
              </div>
            )}
          </GlassCard>
        </div>
      )}

      {activeTab === 'custom' && (
        <div className="space-y-4">
          <div className="flex items-center gap-3 p-4 bg-bg-primary/50 rounded-lg border border-white/10">
            <Shield className="w-5 h-5 text-neon-cyan" />
            <div className="flex-1">
              <p className="text-sm text-gray-300">Custom rule builder is available via the API. Use these endpoints to create rules:</p>
              <div className="mt-2 space-y-1">
                <code className="text-xs text-neon-cyan block">POST /api/detection/rules - Create a rule</code>
                <code className="text-xs text-neon-cyan block">GET /api/detection/rules - List rules</code>
                <code className="text-xs text-neon-cyan block">PUT /api/detection/rules/{'{id}'} - Update a rule</code>
              </div>
            </div>
          </div>

          {customRules.length > 0 && (
            <GlassCard>
              <h3 className="font-heading text-neon-cyan mb-4">Your Custom Rules ({customRules.length})</h3>
              <div className="space-y-2">
                {customRules.map((rule, idx) => (
                  <motion.div key={rule.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className="flex items-center justify-between p-3 bg-bg-primary/50 rounded-lg"
                  >
                    <div>
                      <p className="text-sm text-white">{rule.name}</p>
                      <p className="text-xs text-gray-500">{rule.rule_type} • {rule.event_type || 'regex'} • Severity {rule.severity}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${rule.enabled ? 'bg-green-400/20 text-green-400' : 'bg-gray-500/20 text-gray-500'}`}>
                        {rule.enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </GlassCard>
          )}
        </div>
      )}
    </div>
  )
}
