import { useState } from 'react'
import { Search, Target, Zap } from 'lucide-react'
import GlassCard from '../components/common/GlassCard'
import NeonButton from '../components/common/NeonButton'
import { useStreamingAI } from '../hooks/useStreamingAI'

const presetQueries = [
  'Show failed SSH logins from the last hour',
  'Find PowerShell encoded commands',
  'List top attacking IP addresses',
  'Show all critical severity alerts',
  'Find brute force attempts',
]

export default function ThreatHunt() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState('')
  const [loading, setLoading] = useState(false)
  const { addMessage } = useStreamingAI()

  const executeHunt = async (searchQuery = query) => {
    if (!searchQuery.trim()) return
    
    setLoading(true)
    setResults('')
    addMessage('user', searchQuery)
    addMessage('assistant', '')

    try {
      const response = await fetch('/api/ai/threat-hunt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery }),
      })
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const data = await response.json()
      
      // Format the result nicely
      let formattedResult = `Explanation: ${data.explanation}\n\n`
      if (data.filters) {
        formattedResult += `Filters applied:\n`
        Object.entries(data.filters).forEach(([k, v]) => {
          if (v) formattedResult += `- ${k}: ${v}\n`
        })
      }
      
      if (data.results && data.results.length > 0) {
        formattedResult += `\nResults (${data.count}):\n`
        formattedResult += JSON.stringify(data.results.slice(0, 5), null, 2)
        if (data.count > 5) formattedResult += `\n...and ${data.count - 5} more`
      } else {
        formattedResult += `\nNo matching logs found.`
      }
      
      setResults(formattedResult)
    } catch (error) {
      console.error('Hunt failed:', error)
      setResults(`Error: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-heading font-bold text-white flex items-center gap-3">
        <Target className="text-neon-cyan" />
        Threat Hunting
      </h1>

      <GlassCard>
        <div className="flex gap-2 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && executeHunt()}
              placeholder="Enter your threat hunt query in natural language..."
              className="w-full bg-bg-primary border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan/50"
            />
          </div>
          <NeonButton onClick={() => executeHunt()} disabled={loading}>
            <Zap className="w-4 h-4 mr-1" />
            Hunt
          </NeonButton>
        </div>

        <div>
          <p className="text-xs text-gray-500 mb-2">Example queries:</p>
          <div className="flex flex-wrap gap-2">
            {presetQueries.map((preset, index) => (
              <button
                key={index}
                onClick={() => {
                  setQuery(preset)
                  executeHunt(preset)
                }}
                className="text-xs px-3 py-1.5 bg-bg-primary rounded-lg text-gray-400 hover:text-white hover:bg-bg-secondary transition-colors"
              >
                {preset}
              </button>
            ))}
          </div>
        </div>
      </GlassCard>

      <GlassCard>
        <h3 className="font-heading text-neon-cyan mb-4">Hunt Results</h3>
        
        {loading && (
          <div className="text-center py-8 text-gray-500">
            <Zap className="w-8 h-8 mx-auto mb-2 animate-spin text-neon-cyan" />
            <p>Searching through logs...</p>
          </div>
        )}

        {!loading && !results && (
          <div className="text-center py-8 text-gray-500">
            <Target className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Enter a query to start hunting</p>
          </div>
        )}

        {!loading && results && (
          <div className="text-sm text-gray-300 bg-bg-primary p-4 rounded-lg whitespace-pre-wrap font-mono">
            {results}
          </div>
        )}
      </GlassCard>
    </div>
  )
}