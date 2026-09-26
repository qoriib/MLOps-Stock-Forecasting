import { API_ENDPOINTS } from '@/configs'
import type { PredictResponse, HistoricalResponse } from '@/types'

/**
 * Memanggil Backend API untuk peramalan harga saham.
 * Frontend bertindak murni sebagai konsumen data — tanpa inferensi lokal di browser.
 */
export async function fetchForecastPrediction(params: {
  ticker: string
  modelType?: string
  steps?: number
  startDate?: string
  endDate?: string
  historyLimit?: number
}): Promise<PredictResponse> {
  const response = await fetch(API_ENDPOINTS.predict, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ticker: params.ticker,
      model_type: params.modelType || 'lstm',
      steps: params.steps,
      start_date: params.startDate,
      end_date: params.endDate,
      history_limit: params.historyLimit,
    }),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => null)
    throw new Error(errorData?.message || errorData?.error || `HTTP ${response.status}: Gagal memproses peramalan`)
  }

  return (await response.json()) as PredictResponse
}

/**
 * Mengambil data historis pasar saham dari Backend API.
 */
export async function fetchStockHistoryData(
  ticker: string,
  startDate?: string,
  endDate?: string,
): Promise<HistoricalResponse> {
  const cleanTicker = ticker.trim().toUpperCase()
  const endpoint = API_ENDPOINTS.stockHistory(cleanTicker, startDate, endDate)

  const response = await fetch(endpoint)

  if (!response.ok) {
    const errorData = await response.json().catch(() => null)
    throw new Error(
      errorData?.message || `Data historis pasar untuk ticker '${cleanTicker}' tidak dapat dimuat.`,
    )
  }

  return (await response.json()) as HistoricalResponse
}
