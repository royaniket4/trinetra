import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'

const severityColors = {
  1: '#6B7280',
  2: '#3B82F6',
  3: '#FFB020',
  4: '#F97316',
  5: '#FF3B3B',
}

const severityLabels = {
  1: 'Info',
  2: 'Low',
  3: 'Medium',
  4: 'High',
  5: 'Critical',
}

export default function SeverityChart({ distribution = {} }) {
  const data = Object.entries(distribution).map(([key, value]) => ({
    name: severityLabels[parseInt(key.replace('severity_', ''))] || key,
    value: value,
    severity: parseInt(key.replace('severity_', '')),
  }))

  if (data.length === 0 || data.every(d => d.value === 0)) {
    data.push(
      { name: 'Info', value: 1, severity: 1 },
      { name: 'Low', value: 0, severity: 2 },
      { name: 'Medium', value: 0, severity: 3 },
      { name: 'High', value: 0, severity: 4 },
      { name: 'Critical', value: 0, severity: 5 },
    )
  }

  return (
    <div className="glass-card p-4">
      <h3 className="font-heading text-sm text-neon-cyan mb-4">
        Severity Distribution
      </h3>
      <div className="h-[200px]">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={50}
              outerRadius={80}
              paddingAngle={2}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={severityColors[entry.severity]}
                  stroke="transparent"
                />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: '#111827',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '8px',
              }}
              itemStyle={{ color: '#fff' }}
            />
            <Legend 
              verticalAlign="bottom"
              height={36}
              formatter={(value) => <span className="text-xs text-gray-400">{value}</span>}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}