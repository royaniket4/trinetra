import axios from 'axios'

const API_BASE = '/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Auto-attach JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('trinetra_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const logsApi = {
  ingest: (data) => api.post('/logs/ingest', data),
  ingestBulk: (logs) => api.post('/logs/ingest/bulk', { logs }),
  getAll: (params) => api.get('/logs', { params }),
  getById: (id) => api.get(`/logs/${id}`),
}

export const alertsApi = {
  getAll: (params) => api.get('/alerts', { params }),
  getStats: () => api.get('/alerts/stats/summary'),
  getById: (id) => api.get(`/alerts/${id}`),
  update: (id, data) => api.patch(`/alerts/${id}`, data),
  delete: (id) => api.delete(`/alerts/${id}`),
}

export const incidentsApi = {
  getAll: (params) => api.get('/incidents', { params }),
  getById: (id) => api.get(`/incidents/${id}`),
  create: (data) => api.post('/incidents', data),
  update: (id, data) => api.patch(`/incidents/${id}`, data),
  getAlerts: (id) => api.get(`/incidents/${id}/alerts`),
}

export const aiApi = {
  suggestActions: (id) => `${API_BASE}/ai/suggest-actions/${id}`,
  getHealth: () => api.get('/ai/health'),
  getWorkflows: () => api.get('/ai/workflows'),
  explainAlert: (alertId) => api.post('/ai/explain-alert', { alert_id: alertId }),
  generatePlaybook: (alertId) => api.post('/ai/playbook', { alert_id: alertId }),
  buildNarrative: (alertIds) => api.post('/ai/narrative', { alert_ids: alertIds }),
  threatHunt: (query) => api.post('/ai/threat-hunt', { query }),
  generateReport: (incidentId) => api.post('/ai/incident-report', { incident_id: incidentId }),
  chat: (sessionId, message) => api.post('/ai/chat', { session_id: sessionId, message }),
  getHistory: (sessionId) => api.get(`/ai/chat/${sessionId}/history`),
  clearChat: (sessionId) => api.delete(`/ai/chat/${sessionId}`),
  newSession: () => api.post('/ai/chat/new-session'),
}

export const soarApi = {
  getActions: (params) => api.get('/soar/actions', { params }),
  executeAction: (data) => api.post('/soar/actions', data),
  getBlockedIps: () => api.get('/soar/blocked-ips'),
  getDisabledUsers: () => api.get('/soar/disabled-users'),
}

export const playbookApi = {
  getPlaybooks: () => api.get('/soar/playbooks'),
  getPlaybook: (id) => api.get(`/soar/playbooks/${id}`),
  trigger: (alertId) => api.post('/soar/playbooks/trigger', { alert_id: alertId }),
  getExecutions: (limit = 20) => api.get('/soar/playbooks/executions', { params: { limit } }),
  getExecution: (executionId) => api.get(`/soar/playbooks/executions/${executionId}`),
  getPendingApprovals: () => api.get('/soar/approvals/pending'),
  respondApproval: (stepId, approved) => api.post('/soar/approvals/respond', { step_id: stepId, approved }),
}

export const simulatorApi = {
  getStatus: () => api.get('/simulator/status'),
  toggle: () => api.post('/simulator/toggle'),
  trigger: () => api.post('/simulator/burst', { count: 20 }),
  start: () => api.post('/simulator/start'),
  stop: () => api.post('/simulator/stop'),
  burst: (count) => api.post('/simulator/burst', { count }),
  getConfig: () => api.get('/simulator/config'),
}

export const statsApi = {
  getDashboard: (forceRefresh = false) => api.get('/stats/dashboard', { params: { force_refresh: forceRefresh } }),
  getAttackPaths: (limit = 30) => api.get('/stats/attack-paths', { params: { limit } }),
  getKillChain: () => api.get('/stats/kill-chain'),
  getTimeline: (hours = 24) => api.get('/stats/timeline', { params: { hours } }),
}

export const detectionApi = {
  getCorrelationRules: () => api.get('/detection/correlation/rules'),
  runCorrelation: () => api.post('/detection/correlation/run'),
  getCorrelationResults: (hours = 24) => api.get('/detection/correlation/results', { params: { hours } }),
  getUserRiskScores: () => api.get('/detection/user-analytics/risk-scores'),
  getUserAnalytics: (username) => api.get(`/detection/user-analytics/${username}`),
  getAnomalies: () => api.get('/detection/anomalies'),
  checkVolumeAnomaly: () => api.post('/detection/anomalies/check-volume'),
  getRules: (params) => api.get('/detection/rules', { params }),
  createRule: (data) => api.post('/detection/rules', data),
  updateRule: (ruleId, data) => api.put(`/detection/rules/${ruleId}`, data),
  deleteRule: (ruleId) => api.delete(`/detection/rules/${ruleId}`),
}

export const authApi = {
  login: (username, password) => api.post('/auth/login', { username, password }),
  register: (data) => api.post('/auth/register', data),
  getProfile: () => api.get('/auth/me'),
  updateProfile: (data) => api.put('/auth/me', data),
  listUsers: () => api.get('/auth/users'),
  updateUserRole: (userId, data) => api.put(`/auth/users/${userId}/role`, data),
  getAuditLogs: (limit = 50) => api.get('/auth/audit-logs', { params: { limit } }),
}

export const reportsApi = {
  getIncidentReport: (id) => `${API_BASE}/reports/incidents/${id}`,
  getAlertReport: (id) => `${API_BASE}/reports/alerts/${id}`,
}

export const AI_ENDPOINTS = {
  explain: '/api/ai/explain-alert',
  playbook: '/api/ai/playbook',
  narrative: '/api/ai/narrative',
  threatHunt: '/api/ai/threat-hunt',
  report: '/api/ai/incident-report',
  chat: '/api/ai/chat',
  health: '/api/ai/health',
  workflows: '/api/ai/workflows',
}

export default api