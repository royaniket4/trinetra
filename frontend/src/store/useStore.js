import { create } from 'zustand'
import { v4 as uuidv4 } from 'uuid'

const useStore = create((set, get) => ({
  alerts: [],
  selectedAlertId: null,
  alertFilters: {
    severity: [],
    status: 'all',
    source_ip: '',
  },
  alertStats: {
    total: 0,
    by_severity: {},
    by_status: {},
    top_source_ips: [],
    top_mitre_techniques: [],
    alerts_per_hour: [],
  },
  logs: [],
  stats: {
    total: 0,
    active: 0,
    critical: 0,
    acknowledged: 0,
    severity_distribution: {},
  },
  simulatorStatus: { running: false, interval_seconds: 15 },
  wsConnected: false,
  dashboardStats: {
    total_alerts_24h: 0,
    active_incidents: 0,
    critical_alerts_24h: 0,
    blocked_ips_count: 0,
    unique_attack_sources: 0,
    unique_mitre_techniques: 0,
    alerts_by_severity: {},
    alerts_by_status: {},
    alerts_by_hour: [],
    top_countries: [],
    top_techniques: [],
    attack_paths: [],
    kill_chain: {},
  },
  
  // AI State
  aiSessionId: uuidv4(),
  aiHistory: [],
  aiHealth: { status: 'unknown', provider: 'ollama', model: '', latency: null, available_models: [] },
  aiPanelOpen: false,
  aiContext: { alert_id: null, workflow: 'chat' },
  
  setAlerts: (alerts) => set({ alerts }),
  prependAlert: (alert) => set((state) => ({ 
    alerts: [alert, ...state.alerts].slice(0, 100),
    alertStats: {
      ...state.alertStats,
      total: state.alertStats.total + 1,
      by_severity: {
        ...state.alertStats.by_severity,
        [`severity_${alert.severity}`]: (state.alertStats.by_severity[`severity_${alert.severity}`] || 0) + 1,
      },
    }
  })),
  
  updateAlertInList: (alertId, changes) => set((state) => ({
    alerts: state.alerts.map(a => 
      a.id === alertId ? { ...a, ...changes } : a
    ),
  })),
  
  selectAlert: (alertId) => set({ selectedAlertId: alertId }),
  
  updateFilters: (filters) => set((state) => ({
    alertFilters: { ...state.alertFilters, ...filters },
  })),
  
  clearFilters: () => set({
    alertFilters: { severity: [], status: 'all', source_ip: '' },
  }),
  
  setAlertStats: (stats) => set({ alertStats: stats }),
  
  setLogs: (logs) => set({ logs }),
  addLog: (log) => set((state) => ({ 
    logs: [log, ...state.logs].slice(0, 100) 
  })),
  
  setStats: (stats) => set({ stats }),
  setDashboardStats: (stats) => set({ dashboardStats: stats }),
  setSimulatorStatus: (status) => set({ simulatorStatus: status }),
  setWsConnected: (connected) => set({ wsConnected: connected }),
  
  // AI Actions
  setAiSessionId: (id) => set({ aiSessionId: id }),
  setAiHealth: (health) => set({ aiHealth: health }),
  toggleAiPanel: () => set((state) => { console.log('toggleAiPanel:', !state.aiPanelOpen); return { aiPanelOpen: !state.aiPanelOpen } }),
  setAiPanelOpen: (open) => { console.log('setAiPanelOpen:', open); set({ aiPanelOpen: open }) },
  setAiContext: (context) => set({ aiContext: context }),
  addToAiHistory: (message) => set((state) => ({ 
    aiHistory: [...state.aiHistory, message].slice(-20) 
  })),
  clearAiHistory: () => set({ aiHistory: [] }),
}))

export default useStore