import { APP_CONFIG } from '../configs/app.config'
import type { ModelsResponse, TickerMetrics } from '../types'
import { readAssetText } from '../utils/assets'
import { getAvailableTickers } from './stocks.data'

/**
 * Mengambil metadata metrik dan konfigurasi hyperparameter optimal per ticker dari JSON file di web/backend/assets.
 */
export async function getTickerMetrics(ticker: string): Promise<TickerMetrics | null> {
  const cleanTicker = ticker.trim().toUpperCase()
  const content = await readAssetText(`${cleanTicker}_metrics.json`)

  if (content) {
    try {
      return JSON.parse(content) as TickerMetrics
    } catch (err) {
      console.warn(`[Metrics JSON Parse Warning] Gagal membaca metrics untuk '${cleanTicker}':`, err)
    }
  }

  return null
}

/**
 * Mendapatkan ringkasan seluruh model yang terdaftar secara dinamis dari folder web/backend/assets.
 */
export async function getModelsOverview(): Promise<ModelsResponse> {
  const tickers = await getAvailableTickers()
  const modelMetrics: Record<string, TickerMetrics> = {}

  for (const ticker of tickers) {
    const metrics = await getTickerMetrics(ticker)
    if (metrics) {
      modelMetrics[ticker] = metrics
    }
  }

  const defaultTicker = tickers.length > 0 ? tickers[0] : APP_CONFIG.defaultTicker

  return {
    tickers,
    default_ticker: defaultTicker,
    default_model_type: APP_CONFIG.defaultModelType,
    available_model_types: [...APP_CONFIG.availableModelTypes],
    runtime: APP_CONFIG.runtime,
    model_metrics: modelMetrics,
  }
}
