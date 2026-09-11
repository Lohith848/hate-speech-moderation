import { styleFor } from '../labelStyles.js'

function HighlightedText({ text, explanation }) {
  const weightByToken = {}
  explanation.forEach((e) => {
    weightByToken[e.token.toLowerCase()] = e.weight
  })
  const maxWeight = Math.max(0.0001, ...explanation.map((e) => e.weight))

  return (
    <p className="text-sm leading-relaxed text-gray-700">
      {text.split(' ').map((word, i) => {
        const clean = word.toLowerCase().replace(/[.,!?;:]/g, '')
        const weight = weightByToken[clean]
        if (!weight) {
          return <span key={i}>{word} </span>
        }
        const intensity = Math.min(1, weight / maxWeight)
        return (
          <span
            key={i}
            className="rounded px-0.5"
            style={{ backgroundColor: `rgba(220, 38, 38, ${0.15 + intensity * 0.35})` }}
          >
            {word}{' '}
          </span>
        )
      })}
    </p>
  )
}

export default function ResultCard({ result, originalText }) {
  if (!result) return null
  const style = styleFor(result.label)
  const confidencePct = Math.round((result.confidence[result.label] || 0) * 100)

  return (
    <div className={`mt-6 rounded-xl border ${style.border} ${style.bg} p-5`}>
      <div className="flex items-center justify-between mb-3">
        <span className={`font-semibold ${style.text}`}>
          {style.emoji} {result.label}{' '}
          <span className="font-normal">({confidencePct}% confident)</span>
        </span>
      </div>

      <div className="w-full bg-white/60 rounded-full h-2.5 mb-4">
        <div
          className={`${style.bar} h-2.5 rounded-full transition-all`}
          style={{ width: `${confidencePct}%` }}
        />
      </div>

      <div className="grid grid-cols-3 gap-2 mb-4 text-xs text-gray-600">
        {Object.entries(result.confidence).map(([label, value]) => (
          <div key={label} className="flex justify-between bg-white/60 rounded px-2 py-1">
            <span>{label}</span>
            <span className="font-medium">{Math.round(value * 100)}%</span>
          </div>
        ))}
      </div>

      {result.explanation && result.explanation.length > 0 && (
        <div>
          <p className="text-xs font-medium text-gray-500 mb-1">Why:</p>
          <HighlightedText text={originalText} explanation={result.explanation} />
        </div>
      )}
    </div>
  )
}
