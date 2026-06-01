import { useState, useCallback, useRef } from 'react'

export function useStreamingAI() {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const abortControllerRef = useRef(null)
  
  const streamFromEndpoint = useCallback(async (url) => {
    setLoading(true)
    abortControllerRef.current = new AbortController()
    
    try {
      const response = await fetch(url, {
        signal: abortControllerRef.current.signal,
      })
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      
      let result = ''
      
      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break
        
        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data && data !== '[DONE]') {
              result += data
            }
          }
        }
      }
      
      return result
    } catch (error) {
      if (error.name === 'AbortError') {
        return ''
      }
      throw error
    } finally {
      setLoading(false)
      abortControllerRef.current = null
    }
  }, [])
  
  const addMessage = useCallback((role, content) => {
    setMessages((prev) => [...prev, { role, content, timestamp: Date.now() }])
  }, [])
  
  const clearMessages = useCallback(() => {
    setMessages([])
  }, [])
  
  const cancelStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
  }, [])
  
  return {
    messages,
    loading,
    streamFromEndpoint,
    addMessage,
    clearMessages,
    cancelStream,
  }
}