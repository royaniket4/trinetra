import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  X, Bell, Shield, Zap, Eye, Server,
  Brain, RefreshCw, Volume2, Map, Activity,
  ChevronRight, ChevronDown, Save
} from 'lucide-react'

const tabs = [
  { id: 'general', label: 'General', icon: Shield },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'ai', label: 'AI & Intelligence', icon: Brain },
  { id: 'simulator', label: 'Simulator', icon: Zap },
  { id: 'display', label: 'Display', icon: Eye },
  { id: 'system', label: 'System', icon: Server },
]

function Toggle({ checked, onChange }) {
  return (
    <label className="relative inline-flex items-center cursor-pointer flex-shrink-0">
      <input type="checkbox" className="sr-only peer" checked={checked} onChange={(e) => onChange(e.target.checked)} />
      <div className="w-11 h-6 bg-gray-700 rounded-full peer peer-checked:bg-neon-cyan peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all" />
    </label>
  )
}

function CardRow({ children }) {
  return (
    <div className="flex items-center justify-between gap-4 p-4 bg-bg-primary/50 rounded-lg">
      {children}
    </div>
  )
}

function AccordionSection({ id, icon: Icon, title, expanded, onToggle, children }) {
  return (
    <div>
      <button onClick={() => onToggle(id)}
        className="w-full flex items-center justify-between p-3 bg-bg-primary/50 rounded-lg hover:bg-bg-primary/70 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Icon className="w-4 h-4 text-neon-cyan shrink-0" />
          <span className="text-white text-sm font-medium">{title}</span>
        </div>
        {expanded ? <ChevronDown className="w-4 h-4 text-gray-500 shrink-0" /> : <ChevronRight className="w-4 h-4 text-gray-500 shrink-0" />}
      </button>
      {expanded && (
        <div className="p-4 bg-bg-primary/30 rounded-lg ml-4 mt-1">
          {children}
        </div>
      )}
    </div>
  )
}

export default function SettingsModal({ isOpen, onClose }) {
  const [activeTab, setActiveTab] = useState('general')
  const [expandedSection, setExpandedSection] = useState('auto_refresh')

  const [settings, setSettings] = useState({
    refreshInterval: 5,
    soundAlertsEnabled: false,
    notificationsEnabled: true,
    notifyOnCritical: true,
    notifyOnHigh: true,
    notifyOnMedium: false,
    simulatorEnabled: true,
    simulatorIntervalMin: 5,
    simulatorIntervalMax: 30,
    autoResponseEnabled: false,
    mapAnimationEnabled: true,
    aiProvider: 'ollama',
    aiModel: 'llama3.2:3b',
  })

  // ESC key
  useEffect(() => {
    if (!isOpen) return
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [isOpen, onClose])

  // Body scroll lock
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => { document.body.style.overflow = '' }
  }, [isOpen])

  const handleSave = useCallback(() => {
    console.log('Saving settings:', settings)
    onClose()
  }, [settings, onClose])

  const handleChange = (key, value) => setSettings(prev => ({ ...prev, [key]: value }))
  const toggleSection = (s) => setExpandedSection(prev => prev === s ? null : s)

  const renderContent = () => {
    switch (activeTab) {
      case 'general':
        return (
          <div className="space-y-3">
            <h3 className="font-heading text-base text-white mb-3">General Settings</h3>
            <AccordionSection id="auto_refresh" icon={RefreshCw} title="Auto-refresh" expanded={expandedSection === 'auto_refresh'} onToggle={toggleSection}>
              <div className="flex items-center justify-between gap-4">
                <div>
                  <div className="text-white text-sm">Dashboard Auto-refresh</div>
                  <div className="text-xs text-gray-500">Refresh dashboard data every 5 seconds</div>
                </div>
                <Toggle checked={settings.refreshInterval > 0} onChange={(v) => handleChange('refreshInterval', v ? 5 : 0)} />
              </div>
            </AccordionSection>
            <AccordionSection id="sound" icon={Volume2} title="Sound" expanded={expandedSection === 'sound'} onToggle={toggleSection}>
              <div className="flex items-center justify-between gap-4">
                <div>
                  <div className="text-white text-sm">Sound Alerts</div>
                  <div className="text-xs text-gray-500">Play alert sounds for critical events</div>
                </div>
                <Toggle checked={settings.soundAlertsEnabled} onChange={(v) => handleChange('soundAlertsEnabled', v)} />
              </div>
            </AccordionSection>
          </div>
        )
      case 'notifications':
        return (
          <div className="space-y-4">
            <h3 className="font-heading text-base text-white mb-3">Notification Settings</h3>
            <CardRow>
              <div>
                <div className="text-white text-sm">Enable Notifications</div>
                <div className="text-xs text-gray-500">Show in-app alert notifications</div>
              </div>
              <Toggle checked={settings.notificationsEnabled} onChange={(v) => handleChange('notificationsEnabled', v)} />
            </CardRow>
            <div className="p-4 bg-bg-primary/50 rounded-lg">
              <div className="text-sm text-gray-400 mb-3 font-medium">Alert Severity Notifications</div>
              <div className="space-y-2">
                {[
                  { key: 'notifyOnCritical', label: 'Critical (Severity 5)', color: 'text-critical' },
                  { key: 'notifyOnHigh', label: 'High (Severity 4)', color: 'text-warning' },
                  { key: 'notifyOnMedium', label: 'Medium (Severity 3)', color: 'text-electric-blue' },
                ].map(item => (
                  <label key={item.key} className="flex items-center justify-between p-3 bg-bg-primary/30 rounded-lg hover:bg-bg-primary/50 cursor-pointer">
                    <span className={`text-sm ${item.color}`}>{item.label}</span>
                    <input type="checkbox" checked={settings[item.key]} onChange={(e) => handleChange(item.key, e.target.checked)}
                      className="rounded bg-gray-700 border-gray-600 text-neon-cyan focus:ring-neon-cyan" />
                  </label>
                ))}
              </div>
            </div>
          </div>
        )
      case 'ai':
        return (
          <div className="space-y-4">
            <h3 className="font-heading text-base text-white mb-3">AI & Intelligence Settings</h3>
            <CardRow>
              <div className="w-full">
                <div className="text-white text-sm mb-1">AI Provider</div>
                <select value={settings.aiProvider} onChange={(e) => handleChange('aiProvider', e.target.value)}
                  className="w-full bg-bg-secondary border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:border-neon-cyan/50 focus:outline-none">
                  <option value="ollama">Ollama (Local)</option>
                  <option value="huggingface">HuggingFace</option>
                  <option value="local_gguf">Local GGUF</option>
                  <option value="custom_api">Custom API</option>
                </select>
              </div>
            </CardRow>
            <CardRow>
              <div className="w-full">
                <div className="text-white text-sm mb-1">AI Model</div>
                <input type="text" value={settings.aiModel} onChange={(e) => handleChange('aiModel', e.target.value)}
                  className="w-full bg-bg-secondary border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:border-neon-cyan/50 focus:outline-none" placeholder="llama3.2:3b" />
                <p className="text-xs text-gray-600 mt-1">Model name for the selected provider</p>
              </div>
            </CardRow>
            <CardRow>
              <div>
                <div className="text-white text-sm">TrinetraMind Status</div>
                <div className="text-xs text-gray-500">AI assistant is available</div>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                <span className="text-xs text-green-400">Online</span>
              </div>
            </CardRow>
          </div>
        )
      case 'simulator':
        return (
          <div className="space-y-4">
            <h3 className="font-heading text-base text-white mb-3">Attack Simulator Settings</h3>
            <CardRow>
              <div>
                <div className="text-white text-sm">Enable Simulator</div>
                <div className="text-xs text-gray-500">Generate synthetic attack traffic</div>
              </div>
              <Toggle checked={settings.simulatorEnabled} onChange={(v) => handleChange('simulatorEnabled', v)} />
            </CardRow>
            <CardRow>
              <div className="w-full">
                <div className="text-sm text-gray-400 mb-2 font-medium">Attack Interval (seconds)</div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs text-gray-500 mb-1 block">Minimum</label>
                    <input type="number" value={settings.simulatorIntervalMin} onChange={(e) => handleChange('simulatorIntervalMin', parseInt(e.target.value))}
                      className="w-full bg-bg-secondary border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:border-neon-cyan/50 focus:outline-none" />
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 mb-1 block">Maximum</label>
                    <input type="number" value={settings.simulatorIntervalMax} onChange={(e) => handleChange('simulatorIntervalMax', parseInt(e.target.value))}
                      className="w-full bg-bg-secondary border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:border-neon-cyan/50 focus:outline-none" />
                  </div>
                </div>
              </div>
            </CardRow>
            <CardRow>
              <div>
                <div className="text-white text-sm">Auto Response (Phase 5)</div>
                <div className="text-xs text-gray-500">Automatically execute SOAR actions</div>
              </div>
              <Toggle checked={settings.autoResponseEnabled} onChange={(v) => handleChange('autoResponseEnabled', v)} />
            </CardRow>
          </div>
        )
      case 'display':
        return (
          <div className="space-y-4">
            <h3 className="font-heading text-base text-white mb-3">Display Settings</h3>
            <CardRow>
              <div>
                <div className="text-white text-sm">Threat Map Animations</div>
                <div className="text-xs text-gray-500">Show animated attack arcs on the threat map</div>
              </div>
              <Toggle checked={settings.mapAnimationEnabled} onChange={(v) => handleChange('mapAnimationEnabled', v)} />
            </CardRow>
          </div>
        )
      case 'system':
        return (
          <div className="space-y-4">
            <h3 className="font-heading text-base text-white mb-3">System Information</h3>
            <CardRow>
              <div className="w-full">
                <div className="text-white text-sm mb-1">API Base URL</div>
                <input type="text" value="/api" disabled className="w-full bg-bg-secondary border border-white/10 rounded-lg px-3 py-2 text-gray-500 text-sm" />
              </div>
            </CardRow>
            <CardRow>
              <div className="w-full">
                <div className="text-white text-sm mb-1">WebSocket Endpoint</div>
                <input type="text" value="/ws" disabled className="w-full bg-bg-secondary border border-white/10 rounded-lg px-3 py-2 text-gray-500 text-sm" />
              </div>
            </CardRow>
            <CardRow>
              <div className="w-full">
                <div className="text-white text-sm mb-2">Database</div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-bg-secondary rounded-lg p-3">
                    <div className="text-xs text-gray-500">Type</div>
                    <div className="text-white text-sm mt-1">SQLite</div>
                  </div>
                  <div className="bg-bg-secondary rounded-lg p-3">
                    <div className="text-xs text-gray-500">Path</div>
                    <div className="text-white text-sm font-mono mt-1 truncate">./trinetra.db</div>
                  </div>
                </div>
              </div>
            </CardRow>
          </div>
        )
      default:
        return null
    }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[9999]"
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.15, ease: 'easeOut' }}
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            className="fixed inset-0 z-[9999] flex items-start justify-center pt-8 sm:pt-12 pb-4 px-2 sm:px-4"
          >
            <div className="w-full max-w-5xl max-h-[85vh] bg-bg-secondary border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col">
              {/* Header */}
              <div className="flex items-center justify-between px-4 sm:px-6 py-3 border-b border-white/10 shrink-0">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-neon-cyan/20 flex items-center justify-center shrink-0">
                    <Shield className="w-5 h-5 text-neon-cyan" />
                  </div>
                  <div>
                    <h2 className="font-heading text-lg text-white">Settings</h2>
                    <p className="text-xs text-gray-500">Configure your Trinetra platform</p>
                  </div>
                </div>
                <button onClick={onClose} className="p-2 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors shrink-0">
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Body */}
              <div className="flex flex-1 overflow-hidden">
                {/* Sidebar */}
                <nav className="w-36 sm:w-44 shrink-0 bg-bg-primary/30 border-r border-white/10 p-2 sm:p-3 overflow-y-auto">
                  {tabs.map(tab => (
                    <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                      className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm transition-all mb-0.5 ${
                        activeTab === tab.id
                          ? 'bg-neon-cyan/15 text-neon-cyan border border-neon-cyan/20'
                          : 'text-gray-400 hover:bg-white/5 hover:text-white'
                      }`}
                    >
                      <tab.icon className="w-4 h-4 shrink-0" />
                      <span className="truncate">{tab.label}</span>
                    </button>
                  ))}
                </nav>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-4">
                  {renderContent()}
                </div>
              </div>

              {/* Footer */}
              <div className="px-4 sm:px-6 py-3 border-t border-white/10 flex items-center justify-between shrink-0 bg-bg-primary/20">
                <div className="text-xs text-gray-600">Changes apply immediately after saving</div>
                <div className="flex gap-2">
                  <button onClick={onClose} className="px-4 py-2 text-gray-400 hover:text-white transition-colors text-sm">
                    Cancel
                  </button>
                  <button onClick={handleSave} className="flex items-center gap-2 px-5 py-2 bg-neon-cyan text-bg-primary rounded-lg font-medium hover:bg-neon-cyan/80 transition-colors text-sm">
                    <Save className="w-4 h-4" /> Save Changes
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
