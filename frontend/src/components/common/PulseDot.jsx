export default function PulseDot({ 
  severity = 1, 
  size = 'md',
  className = ''
}) {
  const colors = {
    1: 'bg-gray-400',
    2: 'bg-electric-blue',
    3: 'bg-warning',
    4: 'bg-orange-500',
    5: 'bg-critical',
  }

  const sizes = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4',
  }

  return (
    <span className={`relative inline-flex ${sizes[size]} ${className}`}>
      <span className={`absolute inline-flex h-full w-full rounded-full ${colors[severity]} opacity-75 animate-ping`} />
      <span className={`relative inline-flex rounded-full h-full w-full ${colors[severity]}`} />
    </span>
  )
}