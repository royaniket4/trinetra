import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, User, Loader, X, FileText } from 'lucide-react'
import GlassCard from '../common/GlassCard'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { streamSSE } from '../../utils/sseClient'
import { aiApi } from '../../services/api'
import useStore from '../../store/useStore'

const workflows = [
  { id: 'explain', label: 'Explain Alert', icon: '🔍', requires: 'alert' },
  { id: 'playbook', label: 'Remediation Playbook', icon: '📋', requires: 'alert' },
  { id: 'narrative', label: 'Attack Narrative', icon: '📖', requires: 'alerts' },
  { id: 'threatHunt', label: 'Threat Hunt', icon: '🎯', requires: 'none' },
  { id: 'incidentReport', label: 'Incident Report', icon: '📄', requires: 'incident' },
  { id: 'chat', label: 'General Chat', icon: '💬', requires: 'none' },
]

export default function TrinetraMind() {
  const [input, setInput] = useState('')
  const [activeWorkflow, setActiveWorkflow] = useState('chat')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const messagesEndRef = useRef(null)
  const abortRef = useRef(null)
  
  const { aiSessionId, aiHealth, aiContext, setAiHealth, setAiContext } = useStore()
  const [selectedModel, setSelectedModel] = useState('')
  // Track which (alert_id + workflow) we last auto-triggered so re-clicks always work
  const lastTriggeredRef = useRef(null)

  useEffect(() => {
    if (!aiContext?.workflow || aiContext?.workflow === 'chat' || !aiContext?.alert_id) return

    const triggerKey = `${aiContext.alert_id}-${aiContext.workflow}`
    if (lastTriggeredRef.current === triggerKey) return  // already triggered for this exact combo
    lastTriggeredRef.current = triggerKey

    console.log('Auto-triggering workflow:', aiContext.workflow, 'for alert_id:', aiContext.alert_id)
    setActiveWorkflow(aiContext.workflow)

    const endpoint = aiContext.workflow === 'explain' ? '/api/ai/explain-alert' : '/api/ai/playbook'
    const userMessage = aiContext.workflow === 'explain'
      ? `Explain alert #${aiContext.alert_id}`
      : `Generate playbook for alert #${aiContext.alert_id}`

    // Clear old messages and start fresh for this request
    setMessages([
      { role: 'user', content: userMessage, timestamp: Date.now() },
      { role: 'assistant', content: '', timestamp: Date.now() },
    ])
    setError(null)
    setLoading(true)

    abortRef.current = streamSSE(
      endpoint,
      { alert_id: aiContext.alert_id },
      (token_chunk) => {
        setMessages(prev => {
          const newMsgs = [...prev]
          const last = newMsgs[newMsgs.length - 1]
          newMsgs[newMsgs.length - 1] = { ...last, content: last.content + token_chunk }
          return newMsgs
        })
      },
      () => {
        console.log('AI request completed successfully')
        setLoading(false)
      },
      (err) => {
        console.error('AI request failed:', err.message)
        setError(err.message)
        setLoading(false)
      }
    )
  }, [aiContext])

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await aiApi.getHealth()
        setAiHealth(res.data)
        if (res.data.available_models?.length > 0 && !selectedModel) {
          setSelectedModel(res.data.available_models[0])
        }
      } catch {
        setAiHealth({ status: 'unavailable', provider: 'ollama', model: 'llama3.2:3b', latency: null, available_models: [] })
      }
    }
    checkHealth()
    const interval = setInterval(checkHealth, 30000)
    return () => clearInterval(interval)
  }, [setAiHealth])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const stripMarkdown = (text) => {
    return text
      .replace(/#{1,6}\s/g, '')
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/\*(.*?)\*/g, '$1')
      .replace(/__(.*?)__/g, '$1')
      .replace(/~~(.*?)~~/g, '$1')
      .replace(/`{1,3}[^`]*`{1,3}/g, '')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/^>\s/gm, '')
      .replace(/^\s*[-*+]\s/gm, '  - ')
      .trim()
  }

  const addMessage = (role, content) => {
    setMessages(prev => [...prev, { role, content, timestamp: Date.now() }])
  }

  const updateLastMessage = (updateFn) => {
    setMessages(prev => {
      const newMsgs = [...prev]
      if (newMsgs.length > 0) {
        const lastIdx = newMsgs.length - 1
        newMsgs[lastIdx] = { 
          ...newMsgs[lastIdx], 
          content: typeof updateFn === 'function' ? updateFn(newMsgs[lastIdx].content) : updateFn 
        }
      }
      return newMsgs
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setError(null)
    addMessage('user', userMessage)
    addMessage('assistant', '')
    setLoading(true)

    try {
      let endpoint = '/api/ai/chat'
      let body = { session_id: aiSessionId, message: userMessage }

      if (activeWorkflow === 'threatHunt') {
        endpoint = '/api/ai/threat-hunt'
        body = { query: userMessage }
      } else if (activeWorkflow === 'explain' && aiContext?.alert_id) {
        endpoint = '/api/ai/explain-alert'
        body = { alert_id: aiContext.alert_id }
      } else if (activeWorkflow === 'playbook' && aiContext?.alert_id) {
        endpoint = '/api/ai/playbook'
        body = { alert_id: aiContext.alert_id }
      } else if (activeWorkflow === 'narrative' && aiContext?.alert_ids) {
        endpoint = '/api/ai/narrative'
        body = { alert_ids: aiContext.alert_ids }
      } else if (activeWorkflow === 'incidentReport' && aiContext?.incident_id) {
        endpoint = '/api/ai/incident-report'
        body = { incident_id: aiContext.incident_id }
      }

      if (activeWorkflow === 'threatHunt') {
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        })
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        const data = await response.json()
        
        updateLastMessage(prev => prev + formatThreatHuntResponse(data))
      } else {
        abortRef.current = streamSSE(
          endpoint,
          body,
          (token) => {
            updateLastMessage(prev => prev + token)
          },
          () => {
            setLoading(false)
          },
          (err) => {
            setError(err.message)
            setLoading(false)
          }
        )
      }
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  const formatThreatHuntResponse = (data) => {
    let response = `\n\n**Search Analysis:**\n${data.explanation || 'No explanation'}\n`
    
    if (data.filters) {
      const f = data.filters
      response += `\n**Filters Applied:**\n`
      if (f.event_type) response += `- Event Type: ${f.event_type.join(', ')}\n`
      if (f.severity_min) response += `- Min Severity: ${f.severity_min}\n`
      if (f.source_ip_pattern) response += `- Source IP: ${f.source_ip_pattern}\n`
      if (f.username_pattern) response += `- Username: ${f.username_pattern}\n`
      if (f.mitre_technique) response += `- MITRE Technique: ${f.mitre_technique}\n`
      if (f.time_window_hours) response += `- Time Window: ${f.time_window_hours}h\n`
    }
    
    if (data.results && data.results.length > 0) {
      response += `\n**Found ${data.count} matching logs**\n`
      response += `\n\`\`\`json\n${JSON.stringify(data.results.slice(0, 3), null, 2)}\n\`\`\`\n`
      if (data.results.length > 3) response += `*...and ${data.results.length - 3} more*`
    } else {
      response += `\n*No logs matched these filters.*\n`
    }
    
    return response
  }

  const handleClear = () => {
    if (abortRef.current) {
      abortRef.current.abort()
    }
    setMessages([])
    setError(null)
  }

  const getPlaceholder = () => {
    switch (activeWorkflow) {
      case 'threatHunt':
        return 'Search logs (e.g., "failed SSH logins from Russia")'
      case 'explain':
        return aiContext?.alert_id ? `Explaining alert #${aiContext.alert_id}...` : 'Select an alert first'
      case 'playbook':
        return aiContext?.alert_id ? `Generating playbook for alert #${aiContext.alert_id}...` : 'Select an alert first'
      case 'narrative':
        return aiContext?.alert_ids?.length ? `Building narrative from ${aiContext.alert_ids.length} alerts...` : 'Select alerts first'
      case 'incidentReport':
        return aiContext?.incident_id ? `Generating report for incident #${aiContext.incident_id}...` : 'Select an incident first'
      default:
        return 'Ask about threats, alerts, or search logs...'
    }
  }

  const getWorkflowDescription = () => {
    switch (activeWorkflow) {
      case 'explain':
        return 'Get detailed analysis of a security alert'
      case 'playbook':
        return 'Create incident response playbook for an alert'
      case 'narrative':
        return 'Create chronological attack story from multiple alerts'
      case 'threatHunt':
        return 'Convert natural language to search queries'
      case 'incidentReport':
        return 'Generate professional incident report'
      case 'chat':
        return 'General conversation with AI assistant'
      default:
        return ''
    }
  }

  return (
    <div className="flex flex-col lg:flex-row gap-4 xl:gap-6 h-full">
      <GlassCard className="w-full lg:w-1/4 xl:w-1/5 shrink-0 flex flex-col min-h-0">
        <div className="flex items-center justify-between mb-3 shrink-0">
          <h3 className="font-heading text-neon-cyan text-sm">Workflows</h3>
          {aiHealth.status === 'healthy' ? (
            <span className="text-[10px] text-green-400">● {aiHealth.latency}ms</span>
          ) : (
            <span className="text-[10px] text-red-400">● Offline</span>
          )}
        </div>
        {aiHealth.available_models?.length > 0 && (
          <div className="mb-2">
            <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)}
              className="w-full text-[10px] bg-bg-primary border border-white/10 rounded px-1.5 py-1 text-gray-300 focus:outline-none focus:border-neon-cyan/50"
            >
              {aiHealth.available_models.map(m => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </div>
        )}
        <div className="space-y-1">
          {workflows.map(workflow => (
            <button key={workflow.id} onClick={() => setActiveWorkflow(workflow.id)}
              className={`w-full text-left px-2.5 py-2 rounded-lg text-xs transition-all flex items-center gap-2 ${
                activeWorkflow === workflow.id
                  ? 'bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/30'
                  : 'bg-bg-primary text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <span>{workflow.icon}</span>
              <span>{workflow.label}</span>
            </button>
          ))}
        </div>
        <div className="mt-3 pt-3 border-t border-white/10 shrink-0">
          <p className="text-[10px] text-gray-500 mb-1">Context</p>
          <div className="text-[10px] text-gray-400 leading-tight">
            {aiContext?.alert_id && <p>📍 Alert #{aiContext.alert_id}</p>}
            {aiContext?.alert_ids?.length && <p>📍 {aiContext.alert_ids.length} alerts</p>}
            {aiContext?.incident_id && <p>📍 Incident #{aiContext.incident_id}</p>}
            {!aiContext?.alert_id && !aiContext?.alert_ids?.length && !aiContext?.incident_id && (
              <p className="text-gray-600">No context</p>
            )}
            {selectedModel && <p className="mt-1 text-gray-600">Model: {selectedModel}</p>}
          </div>
        </div>
      </GlassCard>

      <GlassCard className="flex-1 flex flex-col min-h-0">
        <div className="flex items-center justify-between pb-3 border-b border-white/10 shrink-0">
          <div>
            <span className="font-heading text-neon-cyan text-sm">TrinetraMind</span>
            <p className="text-[10px] text-gray-500">{getWorkflowDescription()}</p>
          </div>
          <button onClick={handleClear} className="text-[10px] text-gray-500 hover:text-white px-2 py-1 rounded hover:bg-white/10 shrink-0">Clear</button>
        </div>

        <div className="flex-1 overflow-y-auto min-h-0 space-y-3 py-3 px-1">
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 py-6">
              <Bot className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-xs">Ask me anything</p>
              <div className="mt-2 text-[10px] text-gray-600 space-y-0.5">
                <p>• "Show critical alerts"</p>
                <p>• "Explain alert #5"</p>
                <p>• "Search failed SSH logins"</p>
              </div>
            </div>
          ) : (
            <AnimatePresence>
              {messages.map((msg, index) => (
                <motion.div key={index} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                  className={`flex gap-2 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {msg.role === 'assistant' && (
                    <div className="w-6 h-6 rounded-full bg-gradient-to-br from-neon-cyan/30 to-electric-blue/30 flex items-center justify-center shrink-0 mt-1">
                      <Bot className="w-3 h-3 text-neon-cyan" />
                    </div>
                  )}
                  <div className={`max-w-[85%] rounded-xl px-4 py-3 text-xs leading-relaxed ${
                    msg.role === 'user' ? 'bg-electric-blue/20 text-white border border-electric-blue/30' : 'bg-bg-primary text-gray-200 border border-white/10 shadow-lg shadow-neon-cyan/5'
                  }`}>
                    {msg.role === 'assistant' ? (
                      <ReactMarkdown 
                        remarkPlugins={[remarkGfm]}
                        components={{
                          code({node, inline, className, children, ...props}) {
                            const match = /language-(\w+)/.exec(className || '')
                            return !inline && match ? (
                              <SyntaxHighlighter
                                style={atomDark}
                                language={match[1]}
                                PreTag="div"
                                className="rounded-md my-2"
                                {...props}
                              >
                                {String(children).replace(/\n$/, '')}
                              </SyntaxHighlighter>
                            ) : (
                              <code className={`${className} bg-white/10 px-1 rounded`} {...props}>
                                {children}
                              </code>
                            )
                          },
                          p: ({children}) => <p className="mb-2 last:mb-0">{children}</p>,
                          ul: ({children}) => <ul className="list-disc pl-4 mb-2">{children}</ul>,
                          ol: ({children}) => <ol className="list-decimal pl-4 mb-2">{children}</ol>,
                        }}
                      >
                        {msg.content}
                      </ReactMarkdown>
                    ) : (
                      <div className="whitespace-pre-wrap">{msg.content}</div>
                    )}
                    {msg.role === 'assistant' && loading && index === messages.length - 1 && (
                      <div className="flex items-center gap-2 mt-2 pt-2 border-t border-white/5">
                        <Loader className="w-3 h-3 animate-spin text-neon-cyan" />
                        <span className="text-[10px] text-gray-500 italic">Thinking...</span>
                      </div>
                    )}
                  </div>
                  {msg.role === 'user' && (
                    <div className="w-6 h-6 rounded-full bg-electric-blue/20 flex items-center justify-center shrink-0 mt-1">
                      <User className="w-3 h-3 text-electric-blue" />
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
          )}
          {error && <div className="text-xs text-critical bg-critical/10 p-2 rounded-lg">{error}</div>}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="pt-3 border-t border-white/10 shrink-0">
          <div className="flex gap-2">
            <input type="text" value={input} onChange={(e) => setInput(e.target.value)}
              placeholder={getPlaceholder()}
              className="flex-1 bg-bg-primary border border-white/10 rounded-lg px-3 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan/50"
              disabled={loading} />
            <button type="submit" disabled={loading || !input.trim()}
              className="px-3 py-2 bg-gradient-to-r from-neon-cyan/30 to-electric-blue/30 rounded-lg text-neon-cyan disabled:opacity-50 transition-all shrink-0">
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>
      </GlassCard>
    </div>
  )
}