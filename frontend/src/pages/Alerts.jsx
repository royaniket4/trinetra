import { useEffect } from 'react'
import { Shield, AlertTriangle, Zap } from 'lucide-react'
import { AnimatePresence } from 'framer-motion'
import useStore from '../store/useStore'
import AlertList from '../components/alerts/AlertList'
import AlertFilters from '../components/alerts/AlertFilters'
import AlertDetail from '../components/alerts/AlertDetail'
import GlassCard from '../components/common/GlassCard'

export default function Alerts() {
  const { 
    selectedAlertId, 
    selectAlert, 
    alertFilters, 
    updateFilters, 
    clearFilters,
    alertStats 
  } = useStore()

  return (
    <div className="relative">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-heading font-bold text-white flex items-center gap-3">
          <AlertTriangle className="text-neon-cyan" />
          Alerts
        </h1>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <GlassCard className="p-3 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-neon-cyan/20 flex items-center justify-center">
            <Shield className="w-5 h-5 text-neon-cyan" />
          </div>
          <div>
            <div className="text-2xl font-heading font-bold text-white">
              {alertStats.total || 0}
            </div>
            <div className="text-xs text-gray-500">Total Alerts</div>
          </div>
        </GlassCard>
        
        <GlassCard className="p-3 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-critical/20 flex items-center justify-center">
            <Zap className="w-5 h-5 text-critical" />
          </div>
          <div>
            <div className="text-2xl font-heading font-bold text-critical">
              {alertStats.by_severity?.severity_5 || 0}
            </div>
            <div className="text-xs text-gray-500">Critical</div>
          </div>
        </GlassCard>
        
        <GlassCard className="p-3 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-warning/20 flex items-center justify-center">
            <AlertTriangle className="w-5 h-5 text-warning" />
          </div>
          <div>
            <div className="text-2xl font-heading font-bold text-warning">
              {alertStats.by_status?.open || 0}
            </div>
            <div className="text-xs text-gray-500">Open</div>
          </div>
        </GlassCard>
      </div>

      <AlertFilters 
        filters={alertFilters}
        onFilterChange={updateFilters}
        onClear={clearFilters}
      />

      <div className="flex gap-4">
        <div className="flex-1">
          <AlertList onSelectAlert={selectAlert} />
        </div>
      </div>

      <AnimatePresence>
        {selectedAlertId && (
          <AlertDetail 
            alertId={selectedAlertId} 
            onClose={() => selectAlert(null)} 
          />
        )}
      </AnimatePresence>
    </div>
  )
}