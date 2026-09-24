import type { DateRange } from '@astryxdesign/core/DateRangeInput'
import type { HistoricalResponse, PredictResponse, TickerMetrics } from '@/types'

export type ThemeMode = 'light' | 'dark'

export interface AppSlice {
  ticker: string
  modelType: string
  availableTickers: string[]
  loadingTickers: boolean
  backendHealthy: boolean | null
  themeMode: ThemeMode
  modelMetrics: Record<string, TickerMetrics>
  setTicker: (ticker: string) => void
  setModelType: (modelType: string) => void
  setThemeMode: (mode: ThemeMode) => void
  toggleThemeMode: () => void
  checkHealth: () => Promise<void>
}

export interface ForecastSlice {
  steps: string
  forecastDateRange: DateRange | null
  predictResult: PredictResponse | null
  forecastLoading: boolean
  forecastError: string | null
  setSteps: (steps: string) => void
  setForecastDateRange: (range: DateRange | null) => void
  fetchForecast: (params?: {
    ticker?: string
    modelType?: string
    steps?: string
    dateRange?: DateRange | null
  }) => Promise<void>
}

export interface HistorySlice {
  dateRange: DateRange | null
  historyResult: HistoricalResponse | null
  historyLoading: boolean
  historyError: string | null
  setDateRange: (range: DateRange | null) => void
  fetchHistory: (params?: {
    ticker?: string
    dateRange?: DateRange | null
  }) => Promise<void>
}

export type StockState = AppSlice & ForecastSlice & HistorySlice
