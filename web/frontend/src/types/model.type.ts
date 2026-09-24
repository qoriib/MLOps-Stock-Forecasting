import type { ScalerMeta, BestConfigItem, ModelVariantMetrics } from './prediction.type'

export interface Model {
  ticker: string
  variant?: string
  filename: string
  model_type: string
  file_size_bytes: number
  last_modified: string
}

export type { ModelVariantMetrics, BestConfigItem }

export interface TickerMetrics {
  ticker: string
  target_col?: string
  train_size?: number
  train_size_ratio?: number
  random_state?: number
  epochs?: number
  best_model?: string
  best_variant?: string
  best_configs?: Record<string, BestConfigItem>
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
