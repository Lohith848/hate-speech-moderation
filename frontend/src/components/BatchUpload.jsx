import { useState } from 'react'
import { styleFor } from '../labelStyles.js'
import { moderateBatch } from '../api/client.js'

function resultsToCsv(results) {
  const header = 'text,label,SAFE,OFFENSIVE,HATE\n'
  const rows = results
    .map((r) => {
      const text = `"${(r.text || '').replace(/"/g, '""')}"`
      return `${text},${r.label},${r.confidence.SAFE ?? ''},${r.confidence.OFFENSIVE ?? ''},${r.confidence.HATE ?? ''}`
    })
    .join('\n')
  return header + rows
}

export default function BatchUpload() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [results, setResults] = useState(null)

  const handleUpload = async () => {
    if (!file) {
      setError('Choose a CSV file with a "text" column first.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const data = await moderateBatch(file)
      setResults(data.results)
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Upload failed. Check the CSV has a "text" column.'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = () => {
    if (!results) return
    const csv = resultsToCsv(
      results.map((r, i) => ({ ...r, text: r.text || '' }))
    )
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'moderation-results.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div>
      <h1 className="text-xl font-semibold text-gray-900 mb-1">Batch Analyze</h1>
      <p className="text-sm text-gray-500 mb-6">
        Upload a CSV with a <code className="bg-gray-100 px-1 rounded">text</code> column to
        run many predictions at once — useful for your own test matrix.
      </p>

      <div className="flex items-center gap-3">
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="text-sm"
        />
        <button
          onClick={handleUpload}
          disabled={loading}
          className="bg-gray-900 text-white text-sm font-medium px-5 py-2 rounded-lg hover:bg-gray-700 disabled:opacity-50"
        >
          {loading ? 'Processing...' : 'Upload & Analyze'}
        </button>
      </div>

      {error && <p className="text-red-600 text-sm mt-3">{error}</p>}

      {results && (
        <div className="mt-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-500">{results.length} rows analyzed</p>
            <button
              onClick={handleDownload}
              className="text-sm text-gray-700 underline hover:text-gray-900"
            >
              Download results CSV
            </button>
          </div>
          <div className="overflow-x-auto bg-white rounded-lg border border-gray-200">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-gray-500 border-b border-gray-200">
                  <th className="py-2 px-3">Text</th>
                  <th className="py-2 px-3">Label</th>
                </tr>
              </thead>
              <tbody>
                {results.map((r) => {
                  const style = styleFor(r.label)
                  return (
                    <tr key={r.id} className="border-b border-gray-100 last:border-0">
                      <td className="py-2 px-3 text-gray-700 max-w-md truncate">{r.text}</td>
                      <td className="py-2 px-3">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${style.bg} ${style.text}`}>
                          {r.label}
                        </span>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
