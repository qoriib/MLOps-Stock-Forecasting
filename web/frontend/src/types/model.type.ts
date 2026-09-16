import type { ScalerMeta } from './prediction.type'

export interface Model {
  ticker: string
  variant?: string
  filename: string
  model_type: string
  file_size_bytes: number
  last_modified: string
}

export interface ModelVariantMetrics {
  RMSE: number
  MAPE: number
  R2: number
}

export interface TickerMetrics {
  ticker: string
  target_col?: string
  window_size?: number
  batch_size?: number
  epochs?: number
  learning_rate?: number
  train_size_ratio?: number
  best_model?: string
  best_variant?: string
  metrics: {
    LSTM?: ModelVariantMetrics
    GRU?: ModelVariantMetrics
    [key: string]: ModelVariantMetrics | undefined
  }
}

export interface ModelsResponse {
  tickers: string[]
  default_ticker?: string
  default_model_type?: string
  available_model_types?: string[]
  runtime?: string
  scalers?: Record<string, ScalerMeta>
  model_metrics?: Record<string, TickerMetrics>
  models?: Model[]
}
