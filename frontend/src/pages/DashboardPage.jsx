import { useEffect, useState } from 'react'
import StatsCard from '../components/StatsCard.jsx'
import TrendChart from '../components/TrendChart.jsx'
import ActivityTable from '../components/ActivityTable.jsx'
import { getStats } from '../api/client.js'

const RANGES = [
  { label: 'Last 7 days', value: '7d' },
  { label: 'Last 30 days', value: '30d' },
]

export default function DashboardPage() {
  const [range, setRange] = useState('7d')
  const [stats, setStats] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    getStats(range)
      .then((data) => {
        if (!cancelled) setStats(data)
      })
      .catch(() => {
        if (!cancelled) setError('Could not load dashboard stats. Is the backend running?')
      })
    return () => {
      cancelled = true
    }
  }, [range])

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-semibold text-gray-900">Dashboard</h1>
        <select
          value={range}
          onChange={(e) => setRange(e.target.value)}
          className="text-sm border border-gray-300 rounded-lg px-3 py-1.5"
        >
          {RANGES.map((r) => (
            <option key={r.value} value={r.value}>
              {r.label}
            </option>
          ))}
        </select>
      </div>

      {error && <p className="text-red-600 text-sm mb-4">{error}</p>}

      {stats && (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
            <StatsCard label="Total analyzed" value={stats.total} />
            <StatsCard label="Safe" value={stats.by_label.SAFE ?? 0} colorClass="text-green-600" />
            <StatsCard label="Offensive" value={stats.by_label.OFFENSIVE ?? 0} colorClass="text-amber-600" />
            <StatsCard label="Hate" value={stats.by_label.HATE ?? 0} colorClass="text-red-600" />
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6">
            <TrendChart timeline={stats.timeline} />
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <p className="text-sm font-medium text-gray-700 mb-3">Recent activity</p>
            <ActivityTable recent={stats.recent} />
          </div>
        </>
      )}
    </div>
  )
}
