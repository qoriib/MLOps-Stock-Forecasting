import { create } from 'zustand'
import { fetchAvailableModels, fetchStockHistoryData, fetchForecastPrediction } from '@/services/apiForecast.service'
import { extractErrorMessage } from '@/utils'
import type { StockStoreState, ThemeMode } from './types'

export const useStockStore = create<StockStoreState>()((set, get) => ({
  ticker: 'BBCA.JK',
  model: 'lstm',
  availableTickers: ['BBCA.JK', 'BBRI.JK'],
  availableModels: ['lstm', 'gru'],
  loadingOptions: true,

  // Default range tanggal:
  // History: 1 bulan sebelum akhir data di database (2026-08-25 s.d 2026-09-25)
  // Forecast: rentang hari bursa berikutnya (2026-09-26 s.d 2026-10-10)
  historyRange: { start: '2026-08-25', end: '2026-09-25' },
  forecastRange: { start: '2026-09-26', end: '2026-10-10' },

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

  initApp: async () => {
    set({ loadingOptions: true })
    try {
      const modelsData = await fetchAvailableModels()
      const tickers = modelsData.tickers?.length ? modelsData.tickers : ['BBCA.JK', 'BBRI.JK']
      const models = modelsData.models?.length ? modelsData.models : ['lstm', 'gru']

      const currentTicker = get().ticker
      const finalTicker = tickers.includes(currentTicker) ? currentTicker : tickers[0]

      const currentModel = get().model
      const finalModel = models.includes(currentModel) ? currentModel : models[0]

      set({
        availableTickers: tickers,
        availableModels: models,
        ticker: finalTicker,
        model: finalModel,
        backendHealthy: true,
        loadingOptions: false,
      })

      // Otomatis muat data pertama kali
      await get().runAnalysis({ ticker: finalTicker, model: finalModel })
    } catch (err: unknown) {
      set({
        backendHealthy: false,
        loadingOptions: false,
        error: extractErrorMessage(err, 'Gagal terhubung ke backend server'),
      })
    }
  },

  runAnalysis: async (overrideParams) => {
    const targetTicker = overrideParams?.ticker ?? get().ticker
    const targetModel = overrideParams?.model ?? get().model
    const targetHistRange = overrideParams?.historyRange ?? get().historyRange
    const targetForeRange = overrideParams?.forecastRange ?? get().forecastRange

    if (!targetTicker) {
      set({ error: 'Ticker saham wajib dipilih' })
      return
    }

    if (!targetHistRange?.start || !targetHistRange?.end) {
      set({ error: 'Rentang tanggal riwayat wajib diisi lengkap (start date & end date)' })
      return
    }

    if (!targetForeRange?.start || !targetForeRange?.end) {
      set({ error: 'Rentang tanggal prediksi wajib diisi lengkap (start date & end date)' })
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
      const errorMsg = extractErrorMessage(err, 'Terjadi kesalahan saat memuat data dan peramalan')
      set({
        error: errorMsg,
        loading: false,
      })
    }
  },
}))
