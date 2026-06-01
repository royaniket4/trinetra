import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Clock, Monitor, User, Shield, FileText, Activity, Zap, ShieldAlert, Lock, Eye, Terminal, Brain, Siren } from 'lucide-react'
import SeverityBadge from './SeverityBadge'
import MitreBadge from './MitreBadge'
import { alertsApi, aiApi, playbookApi } from '../../services/api'
import useStore from '../../store/useStore'

const REMEDIATION_STEPS = {
  'Brute Force Detection': [
    { icon: Lock, text: 'Block source IP address immediately', action: 'block_ip' },
    { icon: Eye, text: 'Review failed login patterns for password spraying', action: 'investigate' },
    { icon: Terminal, text: 'Force password reset for affected accounts', action: 'reset_password' },
    { icon: Shield, text: 'Enable MFA on all user accounts', action: 'enable_mfa' },
  ],
  'PowerShell Encoded Command': [
    { icon: Terminal, text: 'Block PowerShell execution policy for non-admin users', action: 'policy' },
    { icon: Eye, text: 'Investigate parent process and network connections', action: 'investigate' },
    { icon: Shield, text: 'Disable Windows Script Host if not needed', action: 'disable_wsh' },
    { icon: Zap, text: 'Quarantine affected endpoint for forensic analysis', action: 'quarantine' },
  ],
  'Reverse Shell Signature': [
    { icon: Zap, text: 'Isolate affected system from network immediately', action: 'isolate' },
    { icon: Terminal, text: 'Identify and kill reverse shell process', action: 'kill_process' },
    { icon: Eye, text: 'Review recent commands and lateral movement', action: 'investigate' },
    { icon: Shield, text: 'Review and revoke any suspicious user sessions', action: 'revoke_sessions' },
  ],
  'Credential Dumping Indicators': [
    { icon: ShieldAlert, text: 'Reset all credentials for compromised accounts', action: 'reset_creds' },
    { icon: Lock, text: 'Disable compromised user accounts pending review', action: 'disable_account' },
    { icon: Eye, text: 'Check for privilege escalation and persistence mechanisms', action: 'investigate' },
    { icon: Zap, text: 'Rotate all service account passwords', action: 'rotate_secrets' },
  ],
  'SQL Injection Attempt': [
    { icon: Shield, text: 'Block source IP at WAF/Firewall', action: 'block_ip' },
    { icon: Eye, text: 'Audit database for data exfiltration indicators', action: 'audit_db' },
    { icon: Terminal, text: 'Patch application input validation', action: 'patch' },
    { icon: Zap, text: 'Enable WAF blocking rules for SQLi patterns', action: 'waf_rules' },
  ],
  'Suspicious File Download': [
    { icon: Zap, text: 'Quarantine the downloaded file for analysis', action: 'quarantine_file' },
    { icon: Eye, text: 'Check file hash against threat intelligence', action: 'check_hash' },
    { icon: Terminal, text: 'Review browser/download history for scope', action: 'investigate' },
    { icon: Shield, text: 'Block file download from untrusted sources', action: 'block_downloads' },
  ],
  'Port Scan Detected': [
    { icon: Eye, text: 'Review scan source and target scope', action: 'investigate' },
    { icon: Shield, text: 'Verify firewall rules block unauthorized scanning', action: 'check_fw' },
    { icon: Lock, text: 'Implement rate limiting on exposed services', action: 'rate_limit' },
  ],
  'default': [
    { icon: Eye, text: 'Analyze alert details and context', action: 'investigate' },
    { icon: Shield, text: 'Implement containment measures', action: 'contain' },
    { icon: Zap, text: 'Block malicious indicators', action: 'block' },
    { icon: Terminal, text: 'Document findings and response actions', action: 'document' },
  ],
}

export default function AlertDetail({ alertId, onClose }) {
  const navigate = useNavigate()
  const { alerts, setAiPanelOpen, setAiContext, updateAlertInList } = useStore()
  const [alert, setAlert] = useState(null)
  const [loading, setLoading] = useState(true)
  const [evidenceExpanded, setEvidenceExpanded] = useState(true)
  const [remediationExpanded, setRemediationExpanded] = useState(true)
  const [updating, setUpdating] = useState(false)

  useEffect(() => {
    if (alertId) {
      const existing = alerts.find(a => a.id === alertId)
      if (existing) {
        setAlert(existing)
        setLoading(false)
      } else {
        alertsApi.getById(alertId)
          .then(res => setAlert(res.data))
          .catch(err => console.error('Failed to load alert:', err))
          .finally(() => setLoading(false))
      }
    }
  }, [alertId, alerts])


  if (!alertId) return null

  let parsedEvidence = {}
  try {
    if (alert?.evidence) {
      parsedEvidence = JSON.parse(alert.evidence)
    }
  } catch (e) {
    parsedEvidence = { raw: alert?.evidence }
  }

  const getRemediationSteps = () => {
    return REMEDIATION_STEPS[alert?.rule_name] || REMEDIATION_STEPS['default']
  }

  const handleInvestigate = () => {
    console.log('Investigate clicked for alert:', alertId)
    onClose()
    window.location.href = '/alerts'
  }

  const handleFalsePositive = async () => {
    console.log('False Positive clicked for alert:', alertId)
    setUpdating(true)
    try {
      await alertsApi.update(alertId, { status: 'false_positive' })
      updateAlertInList(alertId, { status: 'false_positive' })
      if (alert) setAlert({ ...alert, status: 'false_positive' })
      console.log('Alert marked as false positive')
    } catch (err) {
      console.error('Failed to mark as false positive:', err)
      alert('Failed to update alert: ' + err.message)
    } finally {
      setUpdating(false)
    }
  }

  const handleRemediationAction = async (action) => {
    console.log('Remediation action:', action, 'for alert:', alertId)
    try {
      await playbookApi.trigger(alertId)
      window.location.href = '/soar'
    } catch (err) {
      console.error('Failed to trigger playbook:', err)
      window.alert('Failed to trigger playbook: ' + err.message)
    }
  }

  const openAiWithWorkflow = (workflow) => {
    console.log('AI workflow:', workflow, 'for alert:', alert?.id)
    if (!alert?.id) {
      console.error('No alert id found, alert:', alert)
      return
    }
    const context = { alert_id: alert.id, workflow }
    console.log('Setting AI context:', context)
    setAiContext(context)
    setAiPanelOpen(true)
    console.log('AI panel should open now')
  }

  return (
    <motion.div
      initial={{ x: '100%' }}
      animate={{ x: 0 }}
      exit={{ x: '100%' }}
      transition={{ type: 'spring', damping: 25 }}
      className="fixed right-0 top-16 bottom-0 w-[450px] bg-bg-secondary border-l border-white/10 overflow-y-auto z-[100]"
    >
      <div className="p-4 border-b border-white/10 flex items-center justify-between sticky top-0 bg-bg-secondary/90 backdrop-blur-md z-10">
        <h2 className="font-heading text-sm text-neon-cyan">Alert Details</h2>
        <button 
          onClick={onClose}
          className="p-1 hover:bg-white/10 rounded"
        >
          <X className="w-5 h-5 text-gray-400" />
        </button>
      </div>

      {loading ? (
        <div className="p-4 text-gray-500">Loading...</div>
      ) : alert ? (
        <div className="p-4 space-y-4">
          <div className="flex items-start justify-between">
            <h3 className="font-heading text-lg font-bold text-white pr-4">
              {alert.rule_name}
            </h3>
            <SeverityBadge severity={alert.severity} />
          </div>

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="bg-bg-primary/50 p-3 rounded-lg">
              <div className="text-xs text-gray-500 mb-1">Alert ID</div>
              <div className="font-mono text-neon-cyan text-xs">{alert.alert_id}</div>
            </div>
            <div className="bg-bg-primary/50 p-3 rounded-lg">
              <div className="text-xs text-gray-500 mb-1">Status</div>
              <div className="text-white capitalize">{alert.status}</div>
            </div>
            <div className="bg-bg-primary/50 p-3 rounded-lg">
              <div className="text-xs text-gray-500 mb-1">Confidence</div>
              <div className="text-white">{(alert.confidence * 100).toFixed(0)}%</div>
            </div>
            <div className="bg-bg-primary/50 p-3 rounded-lg">
              <div className="text-xs text-gray-500 mb-1">Created</div>
              <div className="text-white text-xs">
                {new Date(alert.timestamp).toLocaleString()}
              </div>
            </div>
          </div>

          <div className="bg-bg-primary/50 p-3 rounded-lg space-y-2">
            <div className="flex items-center gap-2 text-gray-400">
              <Monitor className="w-4 h-4" />
              <span className="text-xs">Source: {alert.source_ip || 'N/A'}</span>
            </div>
            {alert.dest_ip && (
              <div className="flex items-center gap-2 text-gray-400">
                <Activity className="w-4 h-4" />
                <span className="text-xs">Destination: {alert.dest_ip}</span>
              </div>
            )}
            {alert.username && (
              <div className="flex items-center gap-2 text-gray-400">
                <User className="w-4 h-4" />
                <span className="text-xs">User: {alert.username}</span>
              </div>
            )}
          </div>

          {(alert.mitre_tactic || alert.mitre_technique) && (
            <div className="bg-purple/10 border border-purple/30 p-3 rounded-lg">
              <div className="text-xs text-purple mb-2">MITRE ATT&CK</div>
              <MitreBadge 
                tactic={alert.mitre_tactic}
                technique={alert.mitre_technique}
                tacticName={alert.mitre_tactic_name}
                techniqueName={alert.mitre_technique_name}
              />
            </div>
          )}

          <div>
            <button
              onClick={() => setEvidenceExpanded(!evidenceExpanded)}
              className="flex items-center gap-2 text-sm text-gray-400 mb-2"
            >
              <FileText className="w-4 h-4" />
              Evidence
            </button>
            <AnimatePresence>
              {evidenceExpanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="bg-bg-primary p-3 rounded-lg overflow-x-auto"
                >
                  <pre className="text-xs text-gray-300 font-mono whitespace-pre-wrap">
                    {JSON.stringify(parsedEvidence, null, 2)}
                  </pre>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <div className="border-t border-white/10 pt-4">
            <button
              onClick={() => setRemediationExpanded(!remediationExpanded)}
              className="flex items-center gap-2 text-sm text-neon-cyan mb-3"
            >
              <Zap className="w-4 h-4" />
              AI Remediation Steps
            </button>
            <AnimatePresence>
              {remediationExpanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="space-y-2"
                >
                  
                  <div className="text-xs text-gray-500 mb-2">Recommended Actions:</div>
                  {getRemediationSteps().map((step, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.1 }}
                      className="flex items-start gap-3 p-3 bg-bg-primary/50 rounded-lg hover:bg-bg-primary transition-colors group"
                    >
                      <div className="w-8 h-8 rounded-lg bg-neon-cyan/20 flex items-center justify-center flex-shrink-0">
                        <step.icon className="w-4 h-4 text-neon-cyan" />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm text-white">{step.text}</p>
                        <button type="button" onClick={async () => { 
                            console.log('Execute clicked, alertId:', alertId)
                            try{ 
                              console.log('Calling playbookApi.trigger with alertId:', alertId)
                              const res = await playbookApi.trigger(alertId)
                              console.log('Playbook triggered:', res)
                              window.location.href='/soar'
                            }catch(e){ 
                              console.error('Playbook error:', e)
                              if (e.response?.status === 404) {
                                window.alert('No matching playbook found for this alert type')
                              } else {
                                window.alert('Error: '+e.message)
                              } 
                            } 
                          }}
                          className="text-xs text-neon-cyan opacity-0 group-hover:opacity-100 transition-opacity mt-1"
                        >
                          Execute →
                        </button>
                      </div>
                    </motion.div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <div className="flex gap-2 pt-4 border-t border-white/10">
            <button onClick={handleInvestigate} className="flex-1 px-3 py-2 bg-neon-cyan/20 border border-neon-cyan/50 rounded-lg text-neon-cyan hover:bg-neon-cyan/30 text-sm font-medium flex items-center justify-center gap-2">
              <Eye className="w-4 h-4" /> Investigate
            </button>
            <button onClick={handleFalsePositive} disabled={updating} className="flex-1 px-3 py-2 bg-electric-blue/20 border border-electric-blue/50 rounded-lg text-electric-blue hover:bg-electric-blue/30 text-sm font-medium text-center disabled:opacity-50">
              {updating ? 'Updating...' : 'False Positive'}
            </button>
          </div>
          
          <div className="pt-4 mt-4 border-t border-white/10">
            <button onClick={() => openAiWithWorkflow('chat')} className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-neon-cyan/20 to-purple/20 border border-neon-cyan/30 rounded-lg text-neon-cyan hover:from-neon-cyan/30 hover:to-purple/30 transition-all">
              <Brain className="w-5 h-5" />
              Ask TrinetraMind
            </button>
            <div className="flex gap-2 mt-2">
              <button onClick={() => openAiWithWorkflow('explain')} className="flex-1 text-xs py-2 px-3 bg-bg-primary/50 rounded-lg text-gray-400 hover:text-white hover:bg-bg-primary transition-colors text-center">
                Explain Alert
              </button>
              <button onClick={() => openAiWithWorkflow('playbook')} className="flex-1 text-xs py-2 px-3 bg-bg-primary/50 rounded-lg text-gray-400 hover:text-white hover:bg-bg-primary transition-colors text-center">
                Generate Playbook
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-4 text-gray-500">Alert not found</div>
      )}
    </motion.div>
  )
}