export interface HistoricalItem {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface HistoricalResponse {
  ticker: string
  total_records: number
  returned_records: number
  data: HistoricalItem[]
}

export interface PredictRequest {
  ticker: string
  steps?: number
  model_type?: string
  start_date?: string
  end_date?: string
  history_limit?: number
}

export interface PredictionItem {
  date: string
  predicted_price: number
  lower_bound: number | null
  upper_bound: number | null
}

export interface ScalerMeta {
  scaler_type: string
  data_min: number
  data_max: number
  data_range: number
  scale: number
  min: number
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
  model_type: string
  model_name: string
  forecast_steps: number
  window_size?: number
  best_config?: BestConfigItem
  metrics?: ModelVariantMetrics
  last_historical_date: string
  scaler_info?: ScalerMeta
  predictions: PredictionItem[]
  history?: HistoricalItem[]
}

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
  default_ticker: string
  default_model_type: string
  available_model_types: string[]
  runtime: string
  scalers?: Record<string, ScalerMeta>
  model_metrics: Record<string, TickerMetrics>
}

/**
 * HonoEnv interface untuk typed context Hono.
 */
export interface HonoEnv {
  Variables: Record<string, unknown>
}

