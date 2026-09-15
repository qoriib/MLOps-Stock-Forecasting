export interface Model {
  ticker: string
  variant?: string
  filename: string
  model_type: string
  file_size_bytes: number
  last_modified: string
}

export interface ModelsResponse {
  tickers: string[]
  available_model_types?: string[]
  models: Model[]
}
