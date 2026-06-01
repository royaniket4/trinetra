import { useEffect, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Shield, RefreshCw } from 'lucide-react'
import { alertsApi } from '../../services/api'
import AlertCard from './AlertCard'
import useStore from '../../store/useStore'

export default function AlertList({ onSelectAlert }) {
  const { 
    alerts, 
    setAlerts, 
    prependAlert, 
    selectedAlertId,
    alertFilters,
    setAlertStats 
  } = useStore()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchAlerts = useCallback(async () => {
    try {
      const params = {
        limit: 50,
        ...(alertFilters.severity.length > 0 && { severity: Math.min(...alertFilters.severity) }),
        ...(alertFilters.status !== 'all' && { status: alertFilters.status }),
        ...(alertFilters.source_ip && { source_ip: alertFilters.source_ip }),
      }
      
      const [alertsRes, statsRes] = await Promise.all([
        alertsApi.getAll(params),
        alertsApi.getStats(),
      ])
      
      setAlerts(alertsRes.data.alerts)
      setAlertStats(statsRes.data)
      setError(null)
    } catch (err) {
      console.error('Failed to fetch alerts:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [alertFilters, setAlerts, setAlertStats])

  useEffect(() => {
    fetchAlerts()
    const interval = setInterval(fetchAlerts, 10000)
    return () => clearInterval(interval)
  }, [fetchAlerts])

  const handleNewAlert = useCallback((alertData) => {
    prependAlert(alertData)
  }, [prependAlert])

  if (loading && alerts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-500">
        <RefreshCw className="w-8 h-8 mb-2 animate-spin text-neon-cyan" />
        <p className="text-sm">Loading alerts...</p>
      </div>
    )
  }

  if (error && alerts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-500">
        <Shield className="w-12 h-12 mb-2 opacity-50" />
        <p className="text-sm mb-2">No alerts yet</p>
        <p className="text-xs text-gray-600">Send a log to /api/logs/ingest to test</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <AnimatePresence mode="popLayout">
        {alerts.map((alert) => (
          <AlertCard
            key={alert.id}
            alert={alert}
            onClick={() => onSelectAlert(alert.id)}
            isSelected={selectedAlertId === alert.id}
          />
        ))}
      </AnimatePresence>
      
      {alerts.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <Shield className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p className="text-sm">No alerts match your filters</p>
        </div>
      )}
    </div>
  )
}