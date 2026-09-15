export interface HistoricalItem extends Record<string, unknown> {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export type StockDataPoint = HistoricalItem

export interface HistoricalResponse {
  ticker: string
  total_records: number
  returned_records: number
  data: HistoricalItem[]
}
