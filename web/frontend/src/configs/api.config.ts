export const API_BASE_URL =
  (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) ||
  'https://stock-forecast-api.klikolio-creative.workers.dev'

export const API_ENDPOINTS = {
  models: `${API_BASE_URL}/api/models`,
  predict: `${API_BASE_URL}/api/predict`,
  stockHistory: (ticker: string, limit = 500, startDate?: string, endDate?: string) => {
    let url = `${API_BASE_URL}/api/stocks/${ticker}?limit=${limit}`
    if (startDate) url += `&start_date=${encodeURIComponent(startDate)}`
    if (endDate) url += `&end_date=${encodeURIComponent(endDate)}`
    return url
  },
} as const
