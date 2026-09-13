export interface PredictionItem extends Record<string, unknown> {
  date: string
  predicted_price: number
  lower_bound: number | null
  upper_bound: number | null
}

export interface PredictResponse {
  ticker: string
  model_name: string
  forecast_steps: number
  last_historical_date: string | null
  predictions: PredictionItem[]
  history?: HistoricalItem[]
}

export type StockDataPoint = HistoricalItem

export interface HistoricalItem extends Record<string, unknown> {
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

export interface ModelInfo {
  ticker: string
  filename: string
  model_type: string
  file_size_bytes: number
  last_modified: string
}

export interface ModelsResponse {
  tickers: string[]
  models: ModelInfo[]
}
