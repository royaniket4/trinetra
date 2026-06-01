import { useEffect, useRef, useCallback } from 'react'
import useStore from '../store/useStore'

export function useWebSocket() {
  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)
  const { prependAlert, addLog, setStats, setWsConnected } = useStore()
  
  const connect = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws`
    
    wsRef.current = new WebSocket(wsUrl)
    
    wsRef.current.onopen = () => {
      console.log('WebSocket connected')
      setWsConnected(true)
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }
    }
    
    wsRef.current.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        
        switch (message.type) {
          case 'alert':
            prependAlert(message.data)
            break
          case 'log':
            addLog(message.data)
            break
          case 'stats':
            setStats(message.data)
            break
          default:
            break
        }
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }
    
    wsRef.current.onclose = () => {
      console.log('WebSocket disconnected')
      setWsConnected(false)
      reconnectTimeoutRef.current = setTimeout(() => {
        connect()
      }, 3000)
    }
    
    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }, [prependAlert, addLog, setStats, setWsConnected])
  
  useEffect(() => {
    connect()
    
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [connect])
  
  return wsRef.current
}