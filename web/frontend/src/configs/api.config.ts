export const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export const API_ENDPOINTS = {
  models: `${API_BASE_URL}/api/models`,
  predict: `${API_BASE_URL}/api/predict`,
  stockHistory: (
    ticker: string,
    limit = 500,
    startDate?: string,
    endDate?: string,
  ) => {
    let url = `${API_BASE_URL}/api/stocks/${ticker}?limit=${limit}`
    if (startDate) url += `&start_date=${encodeURIComponent(startDate)}`
    if (endDate) url += `&end_date=${encodeURIComponent(endDate)}`
    return url
  },
} as const
