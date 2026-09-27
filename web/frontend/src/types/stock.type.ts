export interface StockDataPoint {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export type HistoricalItem = StockDataPoint

export interface StockHistoryResponse {
  ticker: string
  data: StockDataPoint[]
}

export type HistoricalResponse = StockHistoryResponse
