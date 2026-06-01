import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Shield, Target, CheckCircle, XCircle, AlertTriangle, ChevronDown, ChevronRight, Lightbulb } from 'lucide-react'
import GlassCard from '../components/common/GlassCard'
import api from '../services/api'

const tacticColors = {
  'Reconnaissance': { bg: 'bg-blue-500/10', border: 'border-blue-500/30', text: 'text-blue-400' },
  'Resource Development': { bg: 'bg-gray-500/10', border: 'border-gray-500/30', text: 'text-gray-400' },
  'Initial Access': { bg: 'bg-red-500/10', border: 'border-red-500/30', text: 'text-red-400' },
  'Execution': { bg: 'bg-orange-500/10', border: 'border-orange-500/30', text: 'text-orange-400' },
  'Persistence': { bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', text: 'text-yellow-400' },
  'Privilege Escalation': { bg: 'bg-purple-500/10', border: 'border-purple-500/30', text: 'text-purple-400' },
  'Defense Evasion': { bg: 'bg-pink-500/10', border: 'border-pink-500/30', text: 'text-pink-400' },
  'Credential Access': { bg: 'bg-cyan-500/10', border: 'border-cyan-500/30', text: 'text-cyan-400' },
  'Discovery': { bg: 'bg-teal-500/10', border: 'border-teal-500/30', text: 'text-teal-400' },
  'Lateral Movement': { bg: 'bg-indigo-500/10', border: 'border-indigo-500/30', text: 'text-indigo-400' },
  'Collection': { bg: 'bg-violet-500/10', border: 'border-violet-500/30', text: 'text-violet-400' },
  'Command & Control': { bg: 'bg-rose-500/10', border: 'border-rose-500/30', text: 'text-rose-400' },
  'Exfiltration': { bg: 'bg-fuchsia-500/10', border: 'border-fuchsia-500/30', text: 'text-fuchsia-400' },
  'Impact': { bg: 'bg-red-600/10', border: 'border-red-600/30', text: 'text-red-500' },
}

export default function MitreNavigatorPage() {
  const [coverage, setCoverage] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)
  const [expandedTactic, setExpandedTactic] = useState(null)

  useEffect(() => {
    Promise.all([
      api.get('/enterprise/mitre/coverage'),
      api.get('/enterprise/mitre/recommendations'),
    ]).then(([cRes, rRes]) => {
      setCoverage(cRes.data)
      setRecommendations(rRes.data)
    }).catch(console.error).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-center py-12 text-gray-500">Loading MITRE ATT&CK data...</div>

  const getTechColor = (tech) => {
    if (!tech.covered) return 'bg-bg-primary'
    if (tech.severity >= 5) return 'bg-critical/30'
    if (tech.severity >= 4) return 'bg-warning/30'
    return 'bg-success/30'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-neon-cyan/20 flex items-center justify-center">
            <Target className="w-6 h-6 text-neon-cyan" />
          </div>
          <div>
            <h1 className="text-2xl font-heading font-bold text-white">MITRE ATT&CK Navigator</h1>
            <p className="text-sm text-gray-500">Detection coverage heatmap</p>
          </div>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <span className="text-green-400">{coverage?.covered_techniques} covered</span>
          <span className="text-gray-600">/ {coverage?.total_techniques}</span>
          <span className="px-3 py-1 rounded-full bg-neon-cyan/20 text-neon-cyan font-bold text-lg">
            {coverage?.overall_coverage_pct}%
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 xl:grid-cols-7 gap-2">
        {coverage?.tactics?.map(tactic => {
          const colors = tacticColors[tactic.name] || { bg: 'bg-gray-500/10', border: 'border-gray-500/30', text: 'text-gray-400' }
          return (
            <motion.div key={tactic.name} whileHover={{ scale: 1.05 }}
              onClick={() => setExpandedTactic(expandedTactic === tactic.name ? null : tactic.name)}
              className={`p-2 rounded-lg border cursor-pointer transition-all text-center ${colors.bg} ${colors.border}`}
            >
              <div className={`text-[10px] font-medium ${colors.text} truncate`}>{tactic.name}</div>
              <div className="flex items-center justify-center gap-1 mt-1">
                <div className="flex gap-0.5">
                  {tactic.techniques?.slice(0, 5).map((t, i) => (
                    <div key={i} className={`w-3 h-3 rounded-sm ${getTechColor(t)} ${t.covered ? `border border-white/20` : 'border border-white/10'}`} />
                  ))}
                </div>
                <span className={`text-[10px] ${tactic.coverage_pct >= 50 ? 'text-green-400' : tactic.coverage_pct >= 25 ? 'text-warning' : 'text-critical'}`}>
                  {tactic.detected}/{tactic.total}
                </span>
              </div>
            </motion.div>
          )
        })}
      </div>

      {expandedTactic && coverage?.tactics?.find(t => t.name === expandedTactic) && (
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <GlassCard>
            <h3 className="font-heading text-neon-cyan mb-3">{expandedTactic} Techniques</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {coverage.tactics.find(t => t.name === expandedTactic).techniques.map((tech, i) => (
                <div key={i} className={`p-3 rounded-lg ${getTechColor(tech)} border border-white/10`}>
                  <div className="flex items-center gap-1 mb-1">
                    {tech.covered ? <CheckCircle className="w-3 h-3 text-green-400" /> : <XCircle className="w-3 h-3 text-gray-600" />}
                    <span className="text-xs font-mono text-gray-400">{tech.id}</span>
                  </div>
                  <p className="text-xs text-white truncate">{tech.name}</p>
                  {tech.covered && <p className="text-[10px] text-gray-500 mt-1">{tech.alert_count} alerts</p>}
                </div>
              ))}
            </div>
          </GlassCard>
        </motion.div>
      )}

      <GlassCard>
        <div className="flex items-center gap-2 mb-4">
          <Lightbulb className="w-5 h-5 text-warning" />
          <h3 className="font-heading text-warning">Coverage Recommendations</h3>
        </div>
        {recommendations.length === 0 ? (
          <div className="text-center py-4 text-gray-500 text-sm">No recommendations - all techniques covered!</div>
        ) : (
          <div className="space-y-2">
            {recommendations.map((rec, i) => (
              <motion.div key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}
                className="p-3 bg-bg-primary/50 rounded-lg border-l-4 border-l-warning"
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${rec.priority === 'high' ? 'bg-critical/20 text-critical' : 'bg-warning/20 text-warning'}`}>
                    {rec.priority}
                  </span>
                  <span className="text-xs text-gray-500">{rec.tactic}</span>
                </div>
                <p className="text-sm text-gray-300">{rec.message}</p>
              </motion.div>
            ))}
          </div>
        )}
      </GlassCard>
    </div>
  )
}
