import { create } from 'zustand'
import { fetchAvailableModels, fetchStockHistoryData, fetchForecastPrediction } from '@/services'
import { extractErrorMessage } from '@/utils'
import { DEFAULT_HISTORY_RANGE, DEFAULT_FORECAST_RANGE } from '@/configs'
import type { StockStoreState, ThemeMode } from './types'

export const useStockStore = create<StockStoreState>()((set, get) => ({
  ticker: '',
  model: '',
  availableTickers: [],
  availableModels: [],
  loadingOptions: true,

  historyRange: DEFAULT_HISTORY_RANGE,
  forecastRange: DEFAULT_FORECAST_RANGE,

  historyData: [],
  forecastData: [],

  loading: false,
  error: null,
  backendHealthy: null,
  themeMode: 'dark',

  setTicker: (ticker: string) => {
    set({ ticker })
  },

  setModel: (model: string) => {
    set({ model })
  },

  setHistoryRange: (historyRange) => {
    set({ historyRange })
  },

  setForecastRange: (forecastRange) => {
    set({ forecastRange })
  },

  setThemeMode: (mode: ThemeMode) => {
    set({ themeMode: mode })
  },

  toggleThemeMode: () => {
    set((state) => ({
      themeMode: state.themeMode === 'light' ? 'dark' : 'light',
    }))
  },

  initApp: async () => {
    set({ loadingOptions: true })
    try {
      const modelsData = await fetchAvailableModels()
      const tickers = modelsData.tickers ?? []
      const models = modelsData.models ?? []

      const firstTicker = tickers[0] ?? ''
      const firstModel = models[0] ?? ''

      set({
        availableTickers: tickers,
        availableModels: models,
        ticker: firstTicker,
        model: firstModel,
        backendHealthy: true,
        loadingOptions: false,
      })

      // Auto-run analysis with the first available ticker & model
      if (firstTicker && firstModel) {
        await get().runAnalysis({ ticker: firstTicker, model: firstModel })
      }
    } catch (err: unknown) {
      set({
        backendHealthy: false,
        loadingOptions: false,
        error: extractErrorMessage(err, 'Failed to connect to backend server'),
      })
    }
  },

  runAnalysis: async (overrideParams) => {
    const targetTicker = overrideParams?.ticker ?? get().ticker
    const targetModel = overrideParams?.model ?? get().model
    const targetHistRange = overrideParams?.historyRange ?? get().historyRange
    const targetForeRange = overrideParams?.forecastRange ?? get().forecastRange

    if (!targetTicker) {
      set({ error: 'Stock ticker is required' })
      return
    }

    if (!targetHistRange?.start || !targetHistRange?.end) {
      set({ error: 'Historical date range is required (both start and end dates)' })
      return
    }

    if (!targetForeRange?.start || !targetForeRange?.end) {
      set({ error: 'Forecast date range is required (both start and end dates)' })
      return
    }

    set({ loading: true, error: null })

    try {
      const [histRes, foreRes] = await Promise.all([
        fetchStockHistoryData(targetTicker, targetHistRange.start, targetHistRange.end),
        fetchForecastPrediction({
          ticker: targetTicker,
          model: targetModel,
          startDate: targetForeRange.start,
          endDate: targetForeRange.end,
        }),
      ])

      set({
        historyData: histRes.data ?? [],
        forecastData: foreRes.predictions ?? [],
        loading: false,
        backendHealthy: true,
      })
    } catch (err: unknown) {
      const errorMsg = extractErrorMessage(err, 'An error occurred while loading market data and forecast')
      set({
        error: errorMsg,
        loading: false,
      })
    }
  },
}))
