export const LABEL_STYLES = {
  SAFE: {
    bg: 'bg-green-50',
    border: 'border-green-300',
    text: 'text-green-700',
    bar: 'bg-green-500',
    dot: 'bg-green-500',
    emoji: '🟢',
  },
  OFFENSIVE: {
    bg: 'bg-amber-50',
    border: 'border-amber-300',
    text: 'text-amber-700',
    bar: 'bg-amber-500',
    dot: 'bg-amber-500',
    emoji: '🟠',
  },
  HATE: {
    bg: 'bg-red-50',
    border: 'border-red-300',
    text: 'text-red-700',
    bar: 'bg-red-500',
    dot: 'bg-red-500',
    emoji: '🔴',
  },
}

export const styleFor = (label) => LABEL_STYLES[label] || LABEL_STYLES.SAFE
