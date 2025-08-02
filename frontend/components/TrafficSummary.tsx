// src/components/TrafficSummary.tsx
import React, { useEffect, useState } from 'react'
import axios from 'axios'

interface Stat {  
  camera_id: string  
  events:    number  
  avg_per_min: number  
}

interface TrafficSummaryProps {
  hours?: number  
  title?: string  
}

const TrafficSummary: React.FC<TrafficSummaryProps> = ({
  hours = 1,  
  title  = `Last ${hours} Hour${hours>1?"s":""} Summary`
}) => {
  const [stats, setStats] = useState<Stat[]>([])  
  const [summary, setSummary] = useState<string>("")  
  const [loading, setLoading] = useState(true)  
  const [error, setError] = useState<string|null>(null)  

  useEffect(() => {
    setLoading(true)
    axios
      .get(`http://localhost:5050/api/traffic-summary?hours=${hours}`)
      .then((res) => {
        setSummary(res.data.summary)
        setStats(res.data.stats)
      })
      .catch((err) => {
        console.error(err)
        setError("Could not load traffic summary")
      })
      .finally(() => {
        setLoading(false)
      })
  }, [hours])

  if (loading) return <p className="text-sm text-gray-500">Loading…</p>
  if (error)   return <p className="text-sm text-red-500">{error}</p>

  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-6">
      <h3 className="text-lg font-semibold text-gray-700 mb-2">{title}</h3>
      <p className="mb-4">{summary}</p>
      <ul className="space-y-1">
        {stats.map((item) => (
          <li key={item.camera_id} className="text-sm text-gray-600">
            <span className="font-medium">{item.camera_id}</span>:&nbsp;
            {item.events} total crossings (avg {item.avg_per_min.toFixed(1)}/min)
          </li>
        ))}
      </ul>
    </div>
  )
}

export default TrafficSummary
