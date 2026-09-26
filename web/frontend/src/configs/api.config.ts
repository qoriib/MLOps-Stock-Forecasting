export const API_BASE_URL =
  (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) ||
  'http://localhost:8000'

export const API_ENDPOINTS = {
  models: `${API_BASE_URL}/api/models`,
  predict: `${API_BASE_URL}/api/models/predict`,
  stockHistory: (ticker: string, startDate?: string, endDate?: string) => {
    let url = `${API_BASE_URL}/api/stocks/${ticker}`
    const queryParameters: string[] = []
    if (startDate) queryParameters.push(`start_date=${encodeURIComponent(startDate)}`)
    if (endDate) queryParameters.push(`end_date=${encodeURIComponent(endDate)}`)
    if (queryParameters.length > 0) {
      url += `?${queryParameters.join('&')}`
    }
    return url
  },
} as const
