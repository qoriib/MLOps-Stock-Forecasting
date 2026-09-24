import type { HistoricalItem } from './stock.type'

export interface PredictionItem extends Record<string, unknown> {
  date: string
  predicted_price: number
  lower_bound: number | null
  upper_bound: number | null
}

export interface PredictRequest {
  ticker: string
  steps: number
  model_type?: string
}

export interface ScalerMeta {
  scaler_type: string
  data_min: number
  data_max: number
  data_range: number
  scale: number
  min: number
  train_samples?: number
  total_samples?: number
}

export interface BestConfigItem {
  model: string
  time_steps: number
  optimizer: string
  batch_size: number
  learning_rate: number
  MSE: number
  RMSE: number
  MAPE: number
  R2?: number
}

export interface ModelVariantMetrics {
  MSE?: number
  RMSE: number
  MAPE: number
  R2?: number
  time_steps?: number
  optimizer?: string
  batch_size?: number
  learning_rate?: number
}

export interface PredictResponse {
  ticker: string
  model_type?: string
  model_name: string
  forecast_steps: number
  window_size?: number
  best_config?: BestConfigItem
  metrics?: ModelVariantMetrics
  last_historical_date: string | null
  scaler_info?: ScalerMeta
  predictions: PredictionItem[]
  history?: HistoricalItem[]
}
