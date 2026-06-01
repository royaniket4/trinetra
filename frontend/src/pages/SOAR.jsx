import { Shield, Activity } from 'lucide-react'
import PlaybookEngine from '../components/soar/PlaybookEngine'
import ApprovalQueue from '../components/soar/ApprovalQueue'
import ActionHistory from '../components/soar/ActionHistory'
import ResponseActions from '../components/soar/ResponseActions'

export default function SOAR() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-neon-cyan/20 flex items-center justify-center">
          <Shield className="w-6 h-6 text-neon-cyan" />
        </div>
        <div>
          <h1 className="text-2xl font-heading font-bold text-white">SOAR Automation</h1>
          <p className="text-sm text-gray-500">Automated incident response playbooks and actions</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <PlaybookEngine />
          <ActionHistory />
        </div>
        <div className="space-y-6">
          <ApprovalQueue />
          <ResponseActions />
        </div>
      </div>
    </div>
  )
}
