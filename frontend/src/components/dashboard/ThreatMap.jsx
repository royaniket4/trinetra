import { useMemo } from 'react'
import { ComposableMap, Geographies, Geography, Marker, Line } from 'react-simple-maps'
import { motion } from 'framer-motion'

const geoUrl = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"

const sampleAttacks = [
  { from: [139.6917, 35.6895], to: [-74.006, 40.7128], country: 'Japan' },
  { from: [2.3522, 48.8566], to: [-74.006, 40.7128], country: 'France' },
  { from: [13.405, 52.52], to: [-74.006, 40.7128], country: 'Germany' },
  { from: [55.2708, 25.2048], to: [-74.006, 40.7128], country: 'UAE' },
  { from: [-99.1332, 19.4326], to: [-74.006, 40.7128], country: 'Mexico' },
  { from: [151.2093, -33.8688], to: [-74.006, 40.7128], country: 'Australia' },
  { from: [103.8198, 1.3521], to: [-74.006, 40.7128], country: 'Singapore' },
]

export default function ThreatMap({ alerts = [], attackPaths = [] }) {
  const attackData = useMemo(() => {
    if (attackPaths.length > 0) {
      return attackPaths.slice(0, 15).map((path) => ({
        from: [path.source_lon, path.source_lat],
        to: [path.dest_lon, path.dest_lat],
        severity: path.severity,
      }))
    }
    return sampleAttacks
  }, [attackPaths])

  return (
    <div className="glass-card p-4 h-[400px] relative overflow-hidden">
      <h3 className="font-heading text-sm text-neon-cyan mb-4 flex items-center gap-2">
        <span className="w-2 h-2 bg-critical rounded-full animate-pulse" />
        Global Threat Map
      </h3>
      
      <div className="absolute inset-0">
        <ComposableMap
          projection="geoMercator"
          projectionConfig={{
            scale: 100,
            center: [0, 20]
          }}
          style={{ width: '100%', height: '100%' }}
        >
          <Geographies geography={geoUrl}>
            {({ geographies }) =>
              geographies.map((geo) => (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  fill="#1a2744"
                  stroke="#2d4a7c"
                  strokeWidth={0.5}
                  style={{
                    default: { outline: 'none' },
                    hover: { fill: '#2d4a7c', outline: 'none' },
                    pressed: { outline: 'none' },
                  }}
                />
              ))
            }
          </Geographies>
          
          {attackData.map((attack, i) => {
            const severityColor = attack.severity >= 4 ? '#FF3B3B' : attack.severity >= 3 ? '#F97316' : '#00E5FF'
            return (
              <Line
                key={i}
                from={attack.from}
                to={attack.to}
                stroke={severityColor}
                strokeWidth={attack.severity >= 4 ? 2 : 1}
                strokeOpacity={attack.severity >= 4 ? 0.8 : 0.4}
                strokeLinecap="round"
              />
            )
          })}
          
          {attackData.map((attack, i) => {
            const severityColor = attack.severity >= 4 ? '#FF3B3B' : attack.severity >= 3 ? '#F97316' : '#00E5FF'
            return (
              <Marker key={`marker-${i}`} coordinates={attack.from}>
                <motion.circle
                  r={attack.severity >= 4 ? 5 : 3}
                  fill={severityColor}
                  initial={{ scale: 1 }}
                  animate={{ scale: [1, 1.5, 1] }}
                  transition={{ duration: 2, repeat: Infinity, delay: i * 0.15 }}
                />
              </Marker>
            )
          })}
          
          <Marker coordinates={[-74.006, 40.7128]}>
            <circle r={6} fill="#00E5FF" stroke="#0B1020" strokeWidth={2} />
            <circle r={10} fill="none" stroke="#00E5FF" strokeWidth={1} strokeOpacity={0.5}>
              <animate attributeName="r" from={6} to={12} dur="2s" repeatCount="indefinite" />
              <animate attributeName="opacity" from={0.5} to={0} dur="2s" repeatCount="indefinite" />
            </circle>
          </Marker>
        </ComposableMap>
      </div>
      
      <div className="absolute bottom-4 left-4 text-xs text-gray-500">
        <p>Target: New York (HQ)</p>
        <p>Active Paths: {attackData.length}</p>
      </div>
    </div>
  )
}