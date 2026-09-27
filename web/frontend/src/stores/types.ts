import type { DateRange } from '@astryxdesign/core/DateRangeInput'
import type { StockDataPoint, PredictionItem } from '@/types'

export type ThemeMode = 'light' | 'dark'

export interface StockStoreState {
  // Config & Selection
  ticker: string
  model: string
  availableTickers: string[]
  availableModels: string[]
  loadingOptions: boolean

  // Date ranges
  historyRange: DateRange | null
  forecastRange: DateRange | null

  // Data
  historyData: StockDataPoint[]
  forecastData: PredictionItem[]

  // Status
  loading: boolean
  error: string | null
  backendHealthy: boolean | null
  themeMode: ThemeMode

  // Actions
  setTicker: (ticker: string) => void
  setModel: (model: string) => void
  setHistoryRange: (range: DateRange | null) => void
  setForecastRange: (range: DateRange | null) => void
  setThemeMode: (mode: ThemeMode) => void
  toggleThemeMode: () => void
  initApp: () => Promise<void>
  runAnalysis: (overrideParams?: {
    ticker?: string
    model?: string
    historyRange?: DateRange | null
    forecastRange?: DateRange | null
  }) => Promise<void>
}
