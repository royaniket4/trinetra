import { useState, useCallback, useRef } from 'react'
import { streamSSE } from '../utils/sseClient'

const WORKFLOW_ENDPOINTS = {
  explain: '/api/ai/explain-alert',
  playbook: '/api/ai/playbook',
  narrative: '/api/ai/narrative',
  threatHunt: '/api/ai/threat-hunt',
  incidentReport: '/api/ai/incident-report',
  chat: '/api/ai/chat',
}

export function useAIWorkflow(workflowName) {
  const [content, setContent] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState(null)
  const abortRef = useRef(null)

  const run = useCallback(async (payload) => {
    const endpoint = WORKFLOW_ENDPOINTS[workflowName]
    if (!endpoint) {
      setError(`Unknown workflow: ${workflowName}`)
      return
    }

    setIsStreaming(true)
    setError(null)
    setContent('')

    try {
      abortRef.current = streamSSE(
        endpoint,
        payload,
        (token) => {
          setContent(prev => prev + token)
        },
        () => {
          setIsStreaming(false)
        },
        (err) => {
          setError(err.message)
          setIsStreaming(false)
        }
      )
    } catch (err) {
      setError(err.message)
      setIsStreaming(false)
    }
  }, [workflowName])

  const reset = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort()
    }
    setContent('')
    setError(null)
    setIsStreaming(false)
  }, [])

  const abort = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort()
      setIsStreaming(false)
    }
  }, [])

  return {
    run,
    content,
    isStreaming,
    error,
    reset,
    abort,
  }
}