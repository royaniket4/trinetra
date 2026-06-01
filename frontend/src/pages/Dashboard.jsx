import { useEffect, useState } from 'react'
import { Shield, AlertTriangle, Ban, Zap, Globe, Target, Activity } from 'lucide-react'
import { motion } from 'framer-motion'
import useStore from '../store/useStore'
import { alertsApi, simulatorApi, statsApi } from '../services/api'
import StatCard from '../components/dashboard/StatCard'
import LiveFeed from '../components/dashboard/LiveFeed'
import ThreatMap from '../components/dashboard/ThreatMap'
import SeverityChart from '../components/dashboard/SeverityChart'
import MitreHeatmap from '../components/dashboard/MitreHeatmap'
import KillChain from '../components/dashboard/KillChain'
import GlassCard from '../components/common/GlassCard'
import NeonButton from '../components/common/NeonButton'

export default function Dashboard() {
  const { alerts, stats, simulatorStatus, dashboardStats, setAlerts, setSimulatorStatus, setDashboardStats } = useStore()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [alertsRes, statsRes, simStatus, dashStats] = await Promise.all([
          alertsApi.getAll({ limit: 50 }),
          alertsApi.getStats(),
          simulatorApi.getStatus(),
          statsApi.getDashboard(),
        ])
        setAlerts(alertsRes.data.alerts || alertsRes.data)
        setSimulatorStatus(simStatus.data)
        setDashboardStats(dashStats.data || dashStats)
      } catch (error) {
        console.error('Failed to fetch data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [])

  const toggleSimulator = async () => {
    try {
      const response = await simulatorApi.toggle()
      setSimulatorStatus({ 
        ...simulatorStatus, 
        is_running: response.data.status === 'running' 
      })
    } catch (error) {
      console.error('Failed to toggle simulator:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-500">Loading dashboard...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6 relative">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-heading font-bold text-white flex items-center gap-3">
          <Shield className="text-neon-cyan" />
          Security Operations Center
        </h1>
        <NeonButton 
          onClick={toggleSimulator}
          variant={simulatorStatus.is_running ? 'danger' : 'success'}
          size="sm"
        >
          <Zap className="w-4 h-4 mr-1" />
          {simulatorStatus.is_running ? 'Stop Generator' : 'Start Generator'}
        </NeonButton>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          title="Total Alerts (24h)" 
          value={dashboardStats.total_alerts_24h || 0} 
          icon={AlertTriangle}
          color="cyan"
        />
        <StatCard 
          title="Active Incidents" 
          value={dashboardStats.active_incidents || 0} 
          icon={Shield}
          color="red"
        />
        <StatCard 
          title="Blocked IPs" 
          value={dashboardStats.blocked_ips_count || 0} 
          icon={Ban}
          color="orange"
        />
        <StatCard 
          title="Critical Alerts (24h)" 
          value={dashboardStats.critical_alerts_24h || 0} 
          icon={Zap}
          color="red"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ThreatMap alerts={alerts} attackPaths={dashboardStats.attack_paths || []} />
        <LiveFeed alerts={alerts} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <SeverityChart distribution={dashboardStats.alerts_by_severity || {}} />
        <MitreHeatmap alerts={alerts} />
        <KillChain alerts={alerts} />
      </div>

    </div>
  )
}