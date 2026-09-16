export const STATIC_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env?.BASE_URL) || '/'

export const getStaticDataUrl = (ticker: string) => {
  const base = STATIC_BASE_URL.endsWith('/') ? STATIC_BASE_URL.slice(0, -1) : STATIC_BASE_URL
  return `${base}/data/${ticker}.json`
}

export const getStaticOverviewUrl = () => {
  const base = STATIC_BASE_URL.endsWith('/') ? STATIC_BASE_URL.slice(0, -1) : STATIC_BASE_URL
  return `${base}/models/overview.json`
}

export const API_BASE_URL =
  (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) ||
  'https://stock-forecast-api.klikolio-creative.workers.dev'

export const API_ENDPOINTS = {
  models: API_BASE_URL ? `${API_BASE_URL}/api/models` : getStaticOverviewUrl(),
  predict: API_BASE_URL ? `${API_BASE_URL}/api/predict` : '',
  stockHistory: (
    ticker: string,
    limit = 500,
    startDate?: string,
    endDate?: string,
  ) => {
    if (API_BASE_URL) {
      let url = `${API_BASE_URL}/api/stocks/${ticker}?limit=${limit}`
      if (startDate) url += `&start_date=${encodeURIComponent(startDate)}`
      if (endDate) url += `&end_date=${encodeURIComponent(endDate)}`
      return url
    }
    return getStaticDataUrl(ticker)
  },
} as const

