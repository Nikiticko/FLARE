export function resolveMediaUrl(url) {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://')) return url

  let normalized = url
  if (!normalized.startsWith('/')) {
    normalized = normalized.startsWith('media/')
      ? `/${normalized}`
      : `/media/${normalized}`
  }

  if (import.meta.env.DEV) {
    const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'
    try {
      const origin = new URL(apiBase, window.location.origin).origin
      return `${origin}${normalized}`
    } catch {
      return normalized
    }
  }

  return normalized
}
