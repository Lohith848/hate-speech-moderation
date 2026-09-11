import { useState } from 'react'
import AnalyzeForm from '../components/AnalyzeForm.jsx'
import ResultCard from '../components/ResultCard.jsx'
import { moderateText } from '../api/client.js'

export default function AnalyzePage() {
  const [result, setResult] = useState(null)
  const [originalText, setOriginalText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (text) => {
    setLoading(true)
    setError('')
    try {
      const data = await moderateText(text)
      setResult(data)
      setOriginalText(text)
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          'Could not reach the API. Is the backend running at the URL in your .env?'
      )
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="text-xl font-semibold text-gray-900 mb-1">Content Moderation Demo</h1>
      <p className="text-sm text-gray-500 mb-6">
        Type a post or comment below to see how the model classifies it.
      </p>
      <AnalyzeForm onSubmit={handleSubmit} loading={loading} />
      {error && <p className="text-red-600 text-sm mt-4">{error}</p>}
      <ResultCard result={result} originalText={originalText} />
    </div>
  )
}
