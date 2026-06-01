import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { Search, Filter, Clock, Download, ChevronDown, Loader, X, Terminal } from 'lucide-react'
import GlassCard from '../components/common/GlassCard'
import api from '../services/api'

export default function LogExplorer() {
  const [query, setQuery] = useState('source_ip=*')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [history, setHistory] = useState([])
  const [showHistory, setShowHistory] = useState(false)
  const inputRef = useRef(null)
  const [suggestions, setSuggestions] = useState([])

  const searchExamples = [
    { label: 'All logs', query: 'source_ip=*' },
    { label: 'Failed logins', query: 'event_type:LOGIN_FAILED' },
    { label: 'From specific IP', query: 'source_ip=192.168.1.*' },
    { label: 'Critical alerts', query: 'severity:5' },
    { label: 'Powershell activity', query: 'powershell' },
    { label: 'By username', query: 'username=admin' },
  ]

  const executeSearch = async (searchQuery) => {
    setQuery(searchQuery)
    setLoading(true)
    setError(null)
    try {
      const res = await api.get('/search/logs', {
        params: { query: searchQuery, limit: 100, earliest: '-24h' },
      })
      setResults(res.data)
      setHistory(prev => {
        const updated = [searchQuery, ...prev.filter(q => q !== searchQuery)].slice(0, 10)
        return updated
      })
    } catch (err) {
      setError(err.response?.data?.detail || 'Search failed')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') executeSearch(query)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-neon-cyan/20 flex items-center justify-center">
            <Search className="w-6 h-6 text-neon-cyan" />
          </div>
          <div>
            <h1 className="text-2xl font-heading font-bold text-white">Log Explorer</h1>
            <p className="text-sm text-gray-500">Search logs with field:value syntax</p>
          </div>
        </div>
      </div>

      <div className="relative">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">
              <Terminal className="w-4 h-4" />
            </div>
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => setShowHistory(true)}
              placeholder='Search... e.g., source_ip=192.168.* event_type:LOGIN_FAILED | top source_ip'
              className="w-full bg-bg-secondary border border-white/10 rounded-xl pl-10 pr-4 py-3 text-sm text-white font-mono placeholder-gray-600 focus:outline-none focus:border-neon-cyan/50"
            />
          </div>
          <button
            onClick={() => executeSearch(query)}
            disabled={loading || !query}
            className="px-6 py-3 bg-gradient-to-r from-neon-cyan to-electric-blue rounded-xl text-white font-medium hover:opacity-90 disabled:opacity-50 transition-all flex items-center gap-2"
          >
            {loading ? <Loader className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
            Search
          </button>
        </div>

        <div className="flex flex-wrap gap-2 mt-3">
          {searchExamples.map((ex, idx) => (
            <button key={idx} onClick={() => executeSearch(ex.query)}
              className="px-2.5 py-1 text-xs rounded-full bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white transition-colors border border-white/10">
              {ex.label}
            </button>
          ))}
        </div>

        {history.length > 0 && showHistory && (
          <div className="absolute top-full left-0 right-20 mt-1 bg-bg-secondary border border-white/10 rounded-xl shadow-2xl z-10 p-2">
            {history.map((h, idx) => (
              <button key={idx} onClick={() => { executeSearch(h); setShowHistory(false) }}
                className="w-full text-left px-3 py-2 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors font-mono">
                {h}
              </button>
            ))}
          </div>
        )}
      </div>

      {error && (
        <div className="p-4 bg-critical/10 border border-critical/30 rounded-xl text-critical text-sm">{error}</div>
      )}

      {results && (
        <div className="space-y-4">
          <div className="flex items-center justify-between px-1">
            <div className="flex items-center gap-4 text-sm text-gray-500">
              <span className="text-white font-medium">{results.total}</span> results in {results.took_ms || '< 1'}s
              <span className="text-gray-600">|</span>
              Showing {results.returned} events
            </div>
            <button onClick={() => { const a = document.createElement('a'); a.href = '/api/enterprise/reports/alerts-csv'; a.download = 'alerts.csv'; a.click(); }} className="flex items-center gap-1 text-xs text-neon-cyan hover:underline">
              <Download className="w-3 h-3" /> Export CSV
            </button>
          </div>

          <div className="space-y-1">
            {results.results?.length > 0 ? (
              results.results.map((log, idx) => (
                <motion.div
                  key={log.id || idx}
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.02 }}
                  className="p-3 bg-bg-primary/50 rounded-lg hover:bg-bg-primary/70 transition-colors border border-white/5"
                >
                  <div className="flex items-center gap-3 text-xs text-gray-500 mb-1">
                    <Clock className="w-3 h-3" />
                    <span>{log.timestamp ? new Date(log.timestamp).toLocaleString() : 'N/A'}</span>
                    <span className="px-1.5 py-0.5 rounded bg-white/5">{log.event_type || 'unknown'}</span>
                    {log.sourcetype && <span className="text-gray-600">{log.sourcetype}</span>}
                  </div>
                  <div className="flex items-center gap-4 text-xs text-gray-400 font-mono mb-1">
                    {log.source_ip && <span>src: <span className="text-neon-cyan">{log.source_ip}</span></span>}
                    {log.dest_ip && <span>dst: <span className="text-electric-blue">{log.dest_ip}</span></span>}
                    {log.username && <span>user: <span className="text-purple-400">{log.username}</span></span>}
                  </div>
                  <div className="text-xs text-gray-500 font-mono line-clamp-2">{log.raw_log}</div>
                </motion.div>
              ))
            ) : (
              <div className="text-center py-12 text-gray-500">
                <Search className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>No results found</p>
                <p className="text-xs mt-1">Try broadening your search</p>
              </div>
            )}
          </div>
        </div>
      )}

      {!results && !error && (
        <div className="text-center py-16 text-gray-500">
          <Terminal className="w-16 h-16 mx-auto mb-4 opacity-30" />
          <p className="text-lg text-gray-400">Search your log data</p>
          <p className="text-sm mt-2">Use field:value syntax like <code className="text-neon-cyan bg-white/5 px-2 py-0.5 rounded font-mono">source_ip=192.168.*</code></p>
          <div className="mt-6 grid grid-cols-2 max-w-xl mx-auto gap-4 text-left">
            <div className="p-3 bg-bg-primary/50 rounded-lg border border-white/10">
              <p className="text-xs text-gray-400 font-medium mb-2">Field Filters</p>
              <code className="text-xs text-gray-500 block">source_ip=value</code>
              <code className="text-xs text-gray-500 block">event_type:LOGIN_FAILED</code>
              <code className="text-xs text-gray-500 block">username=admin</code>
              <code className="text-xs text-gray-500 block">{'severity>=4'}</code>
            </div>
            <div className="p-3 bg-bg-primary/50 rounded-lg border border-white/10">
              <p className="text-xs text-gray-400 font-medium mb-2">Pipeline Commands</p>
              <code className="text-xs text-gray-500 block">| top source_ip</code>
              <code className="text-xs text-gray-500 block">| stats count by username</code>
              <code className="text-xs text-gray-500 block">| sort -timestamp</code>
              <code className="text-xs text-gray-500 block">| head 10</code>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
