const DEFAULT_API_URL = 'http://localhost:8000'

export function getApiBaseUrl() {
  return process.env.NEXT_PUBLIC_API_URL || DEFAULT_API_URL
}

export async function apiFetch(path: string, init: RequestInit = {}) {
  const baseUrl = getApiBaseUrl()
  const response = await fetch(`${baseUrl}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init.headers || {}),
    },
    ...init,
  })

  const contentType = response.headers.get('content-type') || ''
  const data = contentType.includes('application/json') ? await response.json() : await response.text()

  if (!response.ok) {
    const message = typeof data === 'string' ? data : data?.detail || 'Request failed'
    throw new Error(message)
  }

  return data
}
