import type { StateCreator } from 'zustand'
import { API_ENDPOINTS, DEFAULT_MODEL_TYPE } from '@/configs'
import type { ModelsResponse } from '@/types'
import type { AppSlice, StockState, ThemeMode } from '../types'

const getInitialThemeMode = (): ThemeMode => {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem('theme-mode')
    if (saved === 'light' || saved === 'dark') return saved
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark'
    }
  }
  return 'light'
}

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
  themeMode: getInitialThemeMode(),

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
    try {
      const response = await fetch(API_ENDPOINTS.models)
      if (response.ok) {
        const data: ModelsResponse = await response.json()
        const tickers = data.tickers || []
        const currentTicker = get().ticker
        const nextTicker =
          currentTicker && tickers.includes(currentTicker)
            ? currentTicker
            : (tickers[0] || '')

        set({
          backendHealthy: true,
          availableTickers: tickers,
          ticker: nextTicker,
          loadingTickers: false,
        })
        return
      }
    } catch {
      // Fallback status offline
    }
    set({ backendHealthy: false, loadingTickers: false })
  },
})
