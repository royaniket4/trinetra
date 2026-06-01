import { MessageSquare, AlertCircle, FileText, BookOpen, Target, FileDescription } from 'lucide-react'

const workflows = [
  { id: 'chat', label: 'Chat', icon: MessageSquare },
  { id: 'explain', label: 'Explain Alert', icon: AlertCircle },
  { id: 'playbook', label: 'Generate Playbook', icon: FileText },
  { id: 'narrative', label: 'Build Narrative', icon: BookOpen },
  { id: 'threatHunt', label: 'Threat Hunt', icon: Target },
  { id: 'incidentReport', label: 'Incident Report', icon: FileDescription },
]

export default function WorkflowSelector({ activeWorkflow, onChange, disabled }) {
  return (
    <div className="flex flex-wrap gap-2 mb-4">
      {workflows.map((workflow) => (
        <button
          key={workflow.id}
          onClick={() => onChange(workflow.id)}
          disabled={disabled}
          className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all
            ${activeWorkflow === workflow.id 
              ? 'bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/30 shadow-lg shadow-neon-cyan/10' 
              : 'bg-bg-primary text-gray-400 border border-white/10 hover:text-white hover:border-white/20'
            }
            disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          <workflow.icon className="w-4 h-4" />
          <span>{workflow.label}</span>
        </button>
      ))}
    </div>
  )
}