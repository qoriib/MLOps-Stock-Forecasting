import { API_ENDPOINTS, getStaticDataUrl } from '@/configs'
import type { PredictResponse, HistoricalResponse, HistoricalItem } from '@/types'

/**
 * Memanggil Cloudflare Worker API Edge Inference untuk peramalan harga saham.
 * Frontend bertindak murni sebagai konsumen data tanpa inferensi lokal di browser.
 */
export async function fetchForecastPrediction(params: {
  ticker: string
  modelType?: string
  steps?: number
  startDate?: string
  endDate?: string
  historyLimit?: number
}): Promise<PredictResponse> {
  const endpoint = API_ENDPOINTS.predict

  if (!endpoint) {
    throw new Error('Konfigurasi endpoint peramalan (API_ENDPOINTS.predict) belum disetel.')
  }

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
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
    const errorMsg =
      errorData?.message || errorData?.error || `HTTP ${response.status}: Gagal memproses peramalan`
    throw new Error(errorMsg)
  }

  return (await response.json()) as PredictResponse
}

/**
 * Mengambil data historis pasar saham dari Cloudflare Worker Backend API
 * dengan fallback ke aset statis lokal jika server tidak dapat dijangkau.
 */
export async function fetchStockHistoryData(
  ticker: string,
  limit = 500,
  startDate?: string,
  endDate?: string,
): Promise<HistoricalResponse> {
  const cleanTicker = ticker.trim().toUpperCase()
  const endpoint = API_ENDPOINTS.stockHistory(cleanTicker, limit, startDate, endDate)

  try {
    const response = await fetch(endpoint)
    if (response.ok) {
      const result = await response.json()
      // Jika respons berbentuk HistoricalResponse dari backend
      if (result && Array.isArray(result.data)) {
        return result as HistoricalResponse
      }
      // Jika respons berupa array langsung dari JSON statis
      if (Array.isArray(result)) {
        const sliced = result.slice(-limit)
        return {
          ticker: cleanTicker,
          total_records: result.length,
          returned_records: sliced.length,
          data: sliced,
        }
      }
    }
  } catch (err) {
    console.warn('Backend API tidak dapat dijangkau, mencoba fallback aset statis:', err)
  }

  // Fallback membaca data JSON statis lokal
  try {
    const fallbackRes = await fetch(getStaticDataUrl(cleanTicker))
    if (fallbackRes.ok) {
      const items: HistoricalItem[] = await fallbackRes.json()
      let filtered = [...items]
      if (startDate) filtered = filtered.filter((d) => d.date >= startDate)
      if (endDate) filtered = filtered.filter((d) => d.date <= endDate)
      const sliced = filtered.slice(-limit)
      return {
        ticker: cleanTicker,
        total_records: filtered.length,
        returned_records: sliced.length,
        data: sliced,
      }
    }
  } catch {
    // Fallback gagal
  }

  throw new Error(`Data historis pasar untuk ticker '${cleanTicker}' tidak dapat dimuat.`)
}
