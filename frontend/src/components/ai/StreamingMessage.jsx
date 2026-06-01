import { useState } from 'react'
import { motion } from 'framer-motion'
import { Brain, Copy, RefreshCw, ThumbsUp, ThumbsDown } from 'lucide-react'
import MarkdownRenderer from './MarkdownRenderer'

export default function StreamingMessage({ content, isStreaming, onRegenerate }) {
  const [copied, setCopied] = useState(false)
  const [feedback, setFeedback] = useState(null)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleFeedback = (value) => {
    setFeedback(value)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex gap-3"
    >
      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-neon-cyan/30 to-electric-blue/30 flex items-center justify-center flex-shrink-0">
        <Brain className="w-5 h-5 text-neon-cyan" />
      </div>
      
      <div className="flex-1 max-w-[85%] rounded-xl p-4 bg-bg-primary text-gray-200 border border-white/10">
        <div className="prose prose-invert max-w-none">
          <MarkdownRenderer content={content} />
        </div>
        
        {isStreaming && (
          <span className="inline-block w-2 h-4 bg-neon-cyan animate-pulse ml-1" />
        )}
        
        {!isStreaming && content && (
          <div className="flex items-center gap-2 mt-4 pt-3 border-t border-white/10">
            <button
              onClick={handleCopy}
              className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
              title="Copy to clipboard"
            >
              {copied ? (
                <span className="text-xs text-green-400">Copied!</span>
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </button>
            
            {onRegenerate && (
              <button
                onClick={onRegenerate}
                className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
                title="Regenerate response"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            )}
            
            <div className="flex items-center gap-1 ml-auto">
              <span className="text-xs text-gray-500 mr-2">Was this helpful?</span>
              <button
                onClick={() => handleFeedback('up')}
                className={`p-1 rounded hover:bg-white/10 transition-colors ${
                  feedback === 'up' ? 'text-green-400' : 'text-gray-400'
                }`}
              >
                <ThumbsUp className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleFeedback('down')}
                className={`p-1 rounded hover:bg-white/10 transition-colors ${
                  feedback === 'down' ? 'text-red-400' : 'text-gray-400'
                }`}
              >
                <ThumbsDown className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}