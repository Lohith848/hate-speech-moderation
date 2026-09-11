import { styleFor } from '../labelStyles.js'

export default function ActivityTable({ recent }) {
  if (!recent || recent.length === 0) {
    return (
      <p className="text-sm text-gray-400 py-8 text-center">
        Nothing analyzed yet.
      </p>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-xs text-gray-500 border-b border-gray-200">
            <th className="py-2 pr-4">Time</th>
            <th className="py-2 pr-4">Text</th>
            <th className="py-2 pr-4">Label</th>
            <th className="py-2 pr-4">Confidence</th>
          </tr>
        </thead>
        <tbody>
          {recent.map((row) => {
            const style = styleFor(row.label)
            return (
              <tr key={row.id} className="border-b border-gray-100 last:border-0">
                <td className="py-2 pr-4 text-gray-400 whitespace-nowrap">
                  {new Date(row.created_at).toLocaleTimeString()}
                </td>
                <td className="py-2 pr-4 text-gray-700 max-w-xs truncate">{row.text}</td>
                <td className="py-2 pr-4">
                  <span
                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${style.bg} ${style.text}`}
                  >
                    <span className={`w-1.5 h-1.5 rounded-full ${style.dot}`} />
                    {row.label}
                  </span>
                </td>
                <td className="py-2 pr-4 text-gray-500">
                  {Math.round(row.confidence * 100)}%
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
