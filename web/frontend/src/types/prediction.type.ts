export interface PredictionItem {
  date: string
  predicted_price: number
}

export interface PredictRequest {
  ticker: string
  model: string
  start_date: string
  end_date: string
}

export interface PredictResponse {
  ticker: string
  model: string
  predictions: PredictionItem[]
}

