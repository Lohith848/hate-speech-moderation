import { useState } from 'react'

export default function AnalyzeForm({ onSubmit, loading }) {
  const [text, setText] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    const trimmed = text.trim()
    if (!trimmed) {
      setError('Please enter some text to analyze.')
      return
    }
    if (trimmed.length > 1000) {
      setError('Text must be 1000 characters or fewer.')
      return
    }
    setError('')
    onSubmit(trimmed)
  }

  return (
    <form onSubmit={handleSubmit}>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Type or paste a post/comment..."
        rows={4}
        className="w-full rounded-lg border border-gray-300 p-3 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-900"
      />
      <div className="flex items-center justify-between mt-2">
        <span className="text-xs text-gray-400">{text.length}/1000</span>
        <button
          type="submit"
          disabled={loading}
          className="bg-gray-900 text-white text-sm font-medium px-5 py-2 rounded-lg hover:bg-gray-700 disabled:opacity-50"
        >
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </div>
      {error && <p className="text-red-600 text-sm mt-2">{error}</p>}
    </form>
  )
}
