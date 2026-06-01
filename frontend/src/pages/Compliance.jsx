import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Shield, CheckCircle, XCircle, AlertTriangle, FileText, Download, ChevronRight } from 'lucide-react'
import GlassCard from '../components/common/GlassCard'
import NeonButton from '../components/common/NeonButton'
import api from '../services/api'

const frameworkColors = {
  nist: { bg: 'bg-blue-500/20', text: 'text-blue-400', border: 'border-blue-500/30' },
  pci_dss: { bg: 'bg-red-500/20', text: 'text-red-400', border: 'border-red-500/30' },
  soc2: { bg: 'bg-purple-500/20', text: 'text-purple-400', border: 'border-purple-500/30' },
  iso27001: { bg: 'bg-green-500/20', text: 'text-green-400', border: 'border-green-500/30' },
}

export default function Compliance() {
  const [frameworks, setFrameworks] = useState([])
  const [selectedFramework, setSelectedFramework] = useState(null)
  const [detail, setDetail] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/enterprise/compliance/frameworks')
      .then(res => setFrameworks(res.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const loadDetail = async (fwId) => {
    setSelectedFramework(fwId)
    try {
      const res = await api.get(`/enterprise/compliance/frameworks/${fwId}`)
      setDetail(res.data)
    } catch (e) {
      console.error(e)
    }
  }

  const getGradeColor = (grade) => {
    if (grade === 'A') return 'text-green-400'
    if (grade === 'B') return 'text-blue-400'
    if (grade === 'C') return 'text-warning'
    if (grade === 'D') return 'text-orange-400'
    return 'text-critical'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-neon-cyan/20 flex items-center justify-center">
            <Shield className="w-6 h-6 text-neon-cyan" />
          </div>
          <div>
            <h1 className="text-2xl font-heading font-bold text-white">Compliance</h1>
            <p className="text-sm text-gray-500">NIST, PCI DSS, SOC 2, ISO 27001 compliance scoring</p>
          </div>
        </div>
        <NeonButton variant="secondary" size="sm" onClick={() => { const a = document.createElement('a'); a.href = '/api/enterprise/reports/alerts-csv'; a.download = 'alerts_report.csv'; a.click(); }}>
          <Download className="w-4 h-4 mr-1" /> Export Report
        </NeonButton>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading frameworks...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          {frameworks.map(fw => (
            <motion.div key={fw.id} whileHover={{ scale: 1.02 }}
              onClick={() => loadDetail(fw.id)}
              className={`p-5 rounded-xl border cursor-pointer transition-all ${
                selectedFramework === fw.id
                  ? (frameworkColors[fw.id]?.border + ' ' + frameworkColors[fw.id]?.bg)
                  : 'bg-bg-primary/50 border-white/10 hover:border-white/20'
              }`}
            >
              <div className="flex items-center justify-between mb-4">
                <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${frameworkColors[fw.id]?.bg} ${frameworkColors[fw.id]?.text}`}>
                  {fw.name.split(' ')[0]}
                </span>
                <span className={`text-2xl font-bold font-heading ${getGradeColor(fw.grade)}`}>
                  {fw.grade}
                </span>
              </div>
              <h3 className="text-white font-medium text-sm mb-1">{fw.name}</h3>
              <p className="text-xs text-gray-500 mb-3">Version {fw.version}</p>
              <div className="flex items-center justify-between text-xs">
                <div className="flex gap-3">
                  <span className="text-green-400">{fw.controls_passed} passed</span>
                  <span className="text-gray-600">/ {fw.controls_total}</span>
                </div>
                <span className="text-neon-cyan font-medium">{fw.score}%</span>
              </div>
              <div className="mt-2 h-1.5 bg-bg-primary rounded-full overflow-hidden">
                <div className={`h-full rounded-full transition-all ${fw.score >= 70 ? 'bg-green-400' : fw.score >= 40 ? 'bg-warning' : 'bg-critical'}`}
                  style={{ width: `${fw.score}%` }} />
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {detail && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
          <GlassCard>
            <div className="flex items-center gap-2 mb-4">
              <Shield className="w-5 h-5 text-neon-cyan" />
              <h3 className="font-heading text-neon-cyan">{detail.framework} - Control Details</h3>
              <span className={`ml-auto text-sm font-bold font-heading ${getGradeColor(detail.overall_grade)}`}>
                Grade: {detail.overall_grade} ({detail.overall_score}%)
              </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
              {[
                { label: 'Controls', value: detail.controls_total },
                { label: 'Passed', value: detail.controls_passed, color: 'text-green-400' },
                { label: 'Partial', value: detail.controls_partial, color: 'text-warning' },
                { label: 'Failed', value: detail.controls_failed, color: 'text-critical' },
                { label: 'Resolution Rate', value: `${detail.evidence?.incident_resolution_rate || 0}%`, color: 'text-neon-cyan' },
              ].map((item, idx) => (
                <div key={idx} className="p-3 bg-bg-primary/50 rounded-lg text-center">
                  <div className={`text-lg font-bold ${item.color || 'text-white'}`}>{item.value}</div>
                  <div className="text-xs text-gray-500">{item.label}</div>
                </div>
              ))}
            </div>

            <div className="space-y-2">
              {detail.controls?.map((ctrl, idx) => (
                <motion.div key={idx} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: idx * 0.03 }}
                  className="flex items-center gap-3 p-3 bg-bg-primary/50 rounded-lg"
                >
                  {ctrl.status === 'passed' && <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />}
                  {ctrl.status === 'partial' && <AlertTriangle className="w-4 h-4 text-warning flex-shrink-0" />}
                  {ctrl.status === 'failed' && <XCircle className="w-4 h-4 text-critical flex-shrink-0" />}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-500 font-mono">{ctrl.id}</span>
                      <span className="text-sm text-white truncate">{ctrl.name}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-gray-500">{ctrl.category}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-20 h-1.5 bg-bg-primary rounded-full">
                      <div className={`h-full rounded-full ${ctrl.score >= 70 ? 'bg-green-400' : ctrl.score >= 40 ? 'bg-warning' : 'bg-critical'}`}
                        style={{ width: `${ctrl.score}%` }} />
                    </div>
                    <span className={`text-xs ${ctrl.score >= 70 ? 'text-green-400' : ctrl.score >= 40 ? 'text-warning' : 'text-critical'}`}>
                      {ctrl.score}%
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          </GlassCard>

          <GlassCard>
            <h3 className="font-heading text-neon-cyan mb-3">Evidence</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { label: 'Alerts (30d)', value: detail.evidence?.alerts_last_30d },
                { label: 'Critical Alerts', value: detail.evidence?.critical_alerts },
                { label: 'Incidents', value: detail.evidence?.incidents_created },
                { label: 'Audit Events (7d)', value: detail.evidence?.audit_events_last_7d },
              ].map((item, idx) => (
                <div key={idx} className="p-3 bg-bg-primary/50 rounded-lg text-center">
                  <div className="text-lg text-white font-bold">{item.value ?? 'N/A'}</div>
                  <div className="text-xs text-gray-500">{item.label}</div>
                </div>
              ))}
            </div>
          </GlassCard>
        </motion.div>
      )}
    </div>
  )
}
