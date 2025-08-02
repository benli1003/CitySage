import React, { useEffect, useState } from 'react'
import axios from 'axios'

interface Stat {
  camera_id:   string
  events:      number
  avg_per_min: number
}

const TrafficSummary: React.FC = () => {
  const [stats,   setStats]   = useState<Stat[]>([])
  const [summary, setSummary] = useState<string>("")
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    axios
      .get('http://localhost:5050/api/traffic-summary?hours=1')
      .then((res) => {
        setSummary(res.data.summary)
        setStats(res.data.stats)
        setLoading(false)
      })
      .catch((err) => {
        console.error(err)
        setError("Could not load traffic summary")
        setLoading(false)
      })
  }, [])

  if (loading) return <p className="text-sm text-gray-500">Loading…</p>
  if (error)   return <p className="text-sm text-red-500">{error}</p>

  return (
    <div>
      <h3 className="text-lg font-semibold text-gray-700 mb-2">
        Past {stats.length > 0 ? stats[0].events : ""}-minute Traffic
      </h3>

      {/* ai summary */}
      <p className="mb-4 text-gray-600">{summary}</p>

      {/* camera breakdown */}
      <ul className="space-y-2">
        {stats.map((item) => (
          <li key={item.camera_id} className="text-sm text-gray-600">
            <span className="font-medium">{item.camera_id}</span> —{' '}
            <span>{item.events} vehicles total</span> (
            {item.avg_per_min.toFixed(1)}/min)
          </li>
        ))}
      </ul>
    </div>
  )
}

export default TrafficSummary
