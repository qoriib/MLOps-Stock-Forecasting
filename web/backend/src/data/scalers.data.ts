import { readAssetText } from '../utils/assets'

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
 * Mendapatkan parameter scaler MinMaxScaler secara dinamis dari file JSON di web/backend/assets.
 */
export async function getStockScaler(ticker: string): Promise<ScalerInfo | null> {
  const cleanTicker = ticker.trim().toUpperCase()
  const content = await readAssetText(`${cleanTicker}_scaler.json`)

  if (content) {
    try {
      return JSON.parse(content) as ScalerInfo
    } catch (err) {
      console.warn(`[Scaler JSON Parse Warning] Gagal parse scaler untuk '${cleanTicker}':`, err)
    }
  }

  return null
}
