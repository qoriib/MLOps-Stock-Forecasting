export interface ScalerInfo {
  scaler_type: string
  ticker: string
  target_col: string
  feature_range: number[]
  data_min: number
  data_max: number
  data_range: number
  scale: number
  min: number
  n_samples_seen?: number
  train_samples?: number
  total_samples?: number
}

/**
 * Mendapatkan parameter scaler MinMaxScaler secara dinamis dari Cloudflare D1.
 * Tidak ada ticker yang di-hardcode.
 */
export async function getStockScaler(ticker: string, db?: D1Database): Promise<ScalerInfo | null> {
  const cleanTicker = ticker.trim().toUpperCase()

  if (db) {
    try {
      const row = await db
        .prepare('SELECT scaler_json FROM stock_models WHERE ticker = ?')
        .bind(cleanTicker)
        .first<{ scaler_json: string }>()

      if (row && row.scaler_json) {
        return JSON.parse(row.scaler_json) as ScalerInfo
      }
    } catch (err) {
      console.warn(`[D1 Scaler Warning] Gagal membaca scaler untuk '${cleanTicker}':`, err)
    }
  }

  return null
}
