import type { StateCreator } from 'zustand'
import { API_ENDPOINTS, DEFAULT_MODEL_TYPE } from '@/configs'
import type { ModelsResponse } from '@/types'
import type { AppSlice, StockState, ThemeMode } from '../types'

export const createAppSlice: StateCreator<
  StockState,
  [],
  [],
  AppSlice
> = (set, get) => ({
  ticker: '',
  modelType: DEFAULT_MODEL_TYPE,
  availableTickers: [],
  loadingTickers: true,
  backendHealthy: null,
  themeMode: 'dark',
  modelMetrics: {},

  setTicker: (ticker: string) => {
    set({ ticker, predictResult: null, historyResult: null })
  },

  setModelType: (modelType: string) => {
    set({ modelType })
  },

  setThemeMode: (mode: ThemeMode) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('theme-mode', mode)
    }
    set({ themeMode: mode })
  },

  toggleThemeMode: () => {
    const nextMode = get().themeMode === 'light' ? 'dark' : 'light'
    if (typeof window !== 'undefined') {
      localStorage.setItem('theme-mode', nextMode)
    }
    set({ themeMode: nextMode })
  },

  checkHealth: async () => {
    set({ loadingTickers: true })
    const defaultTickers = ['BBCA.JK', 'BBRI.JK']

    try {
      const response = await fetch(API_ENDPOINTS.models)
      if (response.ok) {
        const data: ModelsResponse = await response.json()
        const tickers = data.tickers && data.tickers.length > 0 ? data.tickers : defaultTickers
        const currentTicker = get().ticker
        const nextTicker =
          currentTicker && tickers.includes(currentTicker)
            ? currentTicker
            : (data.default_ticker && tickers.includes(data.default_ticker)
                ? data.default_ticker
                : tickers[0])

        set({
          backendHealthy: true,
          availableTickers: tickers,
          ticker: nextTicker,
          modelType: get().modelType || data.default_model_type || DEFAULT_MODEL_TYPE,
          modelMetrics: data.model_metrics || {},
          loadingTickers: false,
        })
        return
      }
    } catch {
      // Fallback ke inferensi in-browser mandiri
    }

    const currentTicker = get().ticker
    const nextTicker =
      currentTicker && defaultTickers.includes(currentTicker)
        ? currentTicker
        : defaultTickers[0]

    set({
      backendHealthy: true,
      availableTickers: defaultTickers,
      ticker: nextTicker,
      modelMetrics: {},
      loadingTickers: false,
    })
  },
})
