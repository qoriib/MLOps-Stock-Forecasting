import { APP_CONFIG } from '../configs/app.config'
import type { ModelsResponse, TickerMetrics } from '../types'

/**
 * Mendapatkan ringkasan seluruh model yang terdaftar secara dinamis dari Cloudflare D1.
 * Tidak ada ticker yang di-hardcode.
 */
export async function getModelsOverview(db?: D1Database): Promise<ModelsResponse> {
  const modelMetrics: Record<string, TickerMetrics> = {}
  let tickers: string[] = []

  if (db) {
    try {
      const { results } = await db
        .prepare('SELECT ticker, metrics_json FROM stock_models ORDER BY ticker ASC')
        .all<{ ticker: string; metrics_json: string }>()

      if (results && results.length > 0) {
        for (const row of results) {
          tickers.push(row.ticker)
          if (row.metrics_json) {
            try {
              modelMetrics[row.ticker] = JSON.parse(row.metrics_json)
            } catch {
              // Abaikan kegagalan parsing parsial
            }
          }
        }
      }

      // Jika tabel stock_models kosong, ambil daftar ticker dari stock_prices
      if (tickers.length === 0) {
        const pricesTickers = await db
          .prepare('SELECT DISTINCT ticker FROM stock_prices ORDER BY ticker ASC')
          .all<{ ticker: string }>()
        if (pricesTickers && pricesTickers.results) {
          tickers = pricesTickers.results.map((r) => r.ticker)
        }
      }
    } catch (err) {
      console.warn('[D1 Models Warning] Gagal mengambil data model:', err)
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
