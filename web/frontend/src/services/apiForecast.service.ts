import { API_ENDPOINTS } from '@/configs'
import type { PredictResponse, StockHistoryResponse, ModelsResponse, PredictRequest } from '@/types'

/**
 * Mengambil daftar ticker dan model yang tersedia dari backend.
 */
export async function fetchAvailableModels(): Promise<ModelsResponse> {
  const response = await fetch(API_ENDPOINTS.models)
  if (!response.ok) {
    const errorData = await response.json().catch(() => null)
    throw new Error(errorData?.detail || `HTTP ${response.status}: Gagal memuat daftar model`)
  }
  return (await response.json()) as ModelsResponse
}

/**
 * Mengambil data historis pasar saham (candlestick OHLC) dari backend.
 */
export async function fetchStockHistoryData(
  ticker: string,
  startDate: string,
  endDate: string,
): Promise<StockHistoryResponse> {
  const cleanTicker = ticker.trim().toUpperCase()
  const endpoint = API_ENDPOINTS.stockHistory(cleanTicker, startDate, endDate)
  const response = await fetch(endpoint)

  if (!response.ok) {
    const errorData = await response.json().catch(() => null)
    throw new Error(
      errorData?.detail || `Data historis pasar untuk ticker '${cleanTicker}' tidak dapat dimuat.`,
    )
  }

  return (await response.json()) as StockHistoryResponse
}

/**
 * Mengirim permintaan inferensi peramalan harga saham ke backend.
 */
export async function fetchForecastPrediction(params: {
  ticker: string
  model: string
  startDate: string
  endDate: string
}): Promise<PredictResponse> {
  const payload: PredictRequest = {
    ticker: params.ticker,
    model: params.model,
    start_date: params.startDate,
    end_date: params.endDate,
  }

  const response = await fetch(API_ENDPOINTS.predict, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => null)
    throw new Error(
      errorData?.detail || `HTTP ${response.status}: Gagal memproses peramalan`,
    )
  }

  return (await response.json()) as PredictResponse
}
