/**
 * URL dasar untuk komunikasi dengan Backend FastAPI.
 * Mengambil nilai dari environment variable VITE_API_URL jika tersedia.
 */
const defaultBackendUrl = 'http://localhost:8000'
const environmentApiUrl = import.meta.env?.VITE_API_URL

export const API_BASE_URL = environmentApiUrl || defaultBackendUrl

/**
 * Endpoint katalog API backend yang digunakan oleh frontend.
 */
export const API_ENDPOINTS = {
  models: `${API_BASE_URL}/api/models`,
  predict: `${API_BASE_URL}/api/models/predict`,

  /**
   * Menghasilkan URL lengkap untuk mengambil riwayat harga saham dengan parameter rentang tanggal.
   */
  stockHistory: (
    tickerSymbol: string,
    startDate?: string,
    endDate?: string,
  ): string => {
    const encodedTicker = encodeURIComponent(tickerSymbol.trim().toUpperCase())
    const baseUrl = `${API_BASE_URL}/api/stocks/${encodedTicker}`
    const queryParameters: string[] = []

    if (startDate) {
      const encodedStartDate = encodeURIComponent(startDate)
      queryParameters.push(`start_date=${encodedStartDate}`)
    }

    if (endDate) {
      const encodedEndDate = encodeURIComponent(endDate)
      queryParameters.push(`end_date=${encodedEndDate}`)
    }

    if (queryParameters.length > 0) {
      const queryString = queryParameters.join('&')
      return `${baseUrl}?${queryString}`
    }

    return baseUrl
  },
} as const
