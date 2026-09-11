import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'

export default function TrendChart({ timeline }) {
  if (!timeline || timeline.length === 0) {
    return (
      <p className="text-sm text-gray-400 py-8 text-center">
        No data yet — analyze some text to see trends here.
      </p>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <AreaChart data={timeline}>
        <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
        <XAxis dataKey="date" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
        <Tooltip />
        <Legend />
        <Area type="monotone" dataKey="SAFE" stackId="1" stroke="#16a34a" fill="#86efac" />
        <Area type="monotone" dataKey="OFFENSIVE" stackId="1" stroke="#d97706" fill="#fcd34d" />
        <Area type="monotone" dataKey="HATE" stackId="1" stroke="#dc2626" fill="#fca5a5" />
      </AreaChart>
    </ResponsiveContainer>
  )
}
