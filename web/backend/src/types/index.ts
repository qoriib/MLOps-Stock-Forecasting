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

export interface PredictResponse {
  ticker: string
  model_type: string
  model_name: string
  forecast_steps: number
  last_historical_date: string
  scaler_info?: ScalerMeta
  predictions: PredictionItem[]
  history?: HistoricalItem[]
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
  default_ticker: string
  default_model_type: string
  available_model_types: string[]
  runtime: string
  scalers?: Record<string, ScalerMeta>
  model_metrics: Record<string, TickerMetrics>
}

/**
 * HonoEnv menggunakan context Variables (bukan Bindings) agar tidak terikat
 * ke platform Cloudflare secara langsung. D1 di-inject oleh middleware Nitro
 * dari event.req.runtime.cloudflare.env, bukan dari c.env.
 */
export interface HonoEnv {
  Variables: {
    db?: D1Database
  }
}
