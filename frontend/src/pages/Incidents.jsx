import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Plus, FileText, RefreshCw } from 'lucide-react'
import GlassCard from '../components/common/GlassCard'
import NeonButton from '../components/common/NeonButton'
import { incidentsApi } from '../services/api'

const statusColors = {
  open: 'text-warning',
  investigating: 'text-electric-blue',
  contained: 'text-purple',
  closed: 'text-success',
}

const severityLabels = ['Info', 'Low', 'Medium', 'High', 'Critical']

export default function Incidents() {
  const [incidents, setIncidents] = useState([])
  const [loading, setLoading] = useState(true)

  const fetchIncidents = async () => {
    setLoading(true)
    try {
      const response = await incidentsApi.getAll({ limit: 50 })
      setIncidents(response.data)
    } catch (error) {
      console.error('Failed to fetch incidents:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchIncidents()
  }, [])

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-heading font-bold text-white flex items-center gap-3">
          <FileText className="text-neon-cyan" />
          Incidents
        </h1>
        <NeonButton onClick={fetchIncidents}>
          <RefreshCw className="w-4 h-4 mr-1" />
          Refresh
        </NeonButton>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading incidents...</div>
      ) : incidents.length === 0 ? (
        <GlassCard>
          <div className="text-center py-12 text-gray-500">
            <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No incidents found</p>
            <p className="text-xs mt-2">Create an incident from the Alerts page</p>
          </div>
        </GlassCard>
      ) : (
        <div className="space-y-3">
          {incidents.map((incident, index) => (
            <motion.div
              key={incident.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.03 }}
            >
              <GlassCard hover className="flex items-center gap-4">
                <div className={`
                  w-10 h-10 rounded-lg flex items-center justify-center font-heading font-bold
                  ${incident.severity >= 4 ? 'bg-critical/20 text-critical' :
                    incident.severity >= 3 ? 'bg-warning/20 text-warning' :
                    'bg-electric-blue/20 text-electric-blue'}
                `}>
                  {incident.severity}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-mono text-neon-cyan">
                      {incident.incident_id}
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded ${statusColors[incident.status]} bg-white/5`}>
                      {incident.status}
                    </span>
                  </div>
                  <p className="text-white mt-1">{incident.title}</p>
                  <div className="flex items-center gap-4 mt-1 text-xs text-gray-500">
                    <span>{incident.alert_count} alerts</span>
                    <span>Created: {new Date(incident.created_at).toLocaleString()}</span>
                    {incident.assigned_to && (
                      <span>Assigned: {incident.assigned_to}</span>
                    )}
                  </div>
                </div>
                <NeonButton variant="secondary" size="sm">
                  View Details
                </NeonButton>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}