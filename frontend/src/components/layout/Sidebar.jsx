import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  ShieldAlert, 
  AlertTriangle, 
  Target, 
  Bot, 
  Siren,
  Activity,
  Brain,
  Search,
  Shield,
  Crosshair,
  Globe,
  Menu
} from 'lucide-react'
import { useState } from 'react'

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/alerts', icon: ShieldAlert, label: 'Alerts' },
  { path: '/incidents', icon: AlertTriangle, label: 'Incidents' },
  { path: '/logs', icon: Search, label: 'Log Explorer' },
  { path: '/detection', icon: Brain, label: 'Advanced Detection' },
  { path: '/mitre', icon: Crosshair, label: 'MITRE ATT&CK' },
  { path: '/threat-hunt', icon: Target, label: 'Threat Hunt' },
  { path: '/soar', icon: Siren, label: 'SOAR' },
  { path: '/compliance', icon: Shield, label: 'Compliance' },
  { path: '/ai-assistant', icon: Bot, label: 'TrinetraMind' },
]

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <aside 
      className={`fixed left-0 top-0 h-full bg-bg-secondary/90 backdrop-blur-md border-r border-white/10 transition-all duration-300 z-40 ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      <div className="flex flex-col h-full">
        <div className="p-4 flex items-center justify-between border-b border-white/10">
          {!collapsed && (
            <div className="flex items-center gap-2">
              <Activity className="w-8 h-8 text-neon-cyan" />
              <span className="font-heading text-xl font-bold neon-text">
                TRINETRA
              </span>
            </div>
          )}
          <button 
            onClick={() => setCollapsed(!collapsed)}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <Menu className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        <nav className="flex-1 py-4 px-2 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-3 rounded-lg transition-all ${
                  isActive
                    ? 'bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/30'
                    : 'text-gray-400 hover:bg-white/5 hover:text-white'
                }`
              }
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {!collapsed && <span className="font-medium">{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-white/10">
          {!collapsed && (
            <div className="text-xs text-gray-500 text-center">
              <div className="font-heading">v2.0.0</div>
              <div className="mt-1">Enterprise SIEM</div>
            </div>
          )}
        </div>
      </div>
    </aside>
  )
}
