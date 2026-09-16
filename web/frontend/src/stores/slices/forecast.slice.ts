import type { StateCreator } from 'zustand'
import { DEFAULT_FORECAST_STEPS } from '@/configs'
import { extractErrorMessage } from '@/utils'
import { fetchForecastPrediction } from '@/services/apiForecast.service'
import type { ForecastSlice, StockState } from '../types'

export const createForecastSlice: StateCreator<
  StockState,
  [],
  [],
  ForecastSlice
> = (set, get) => ({
  steps: DEFAULT_FORECAST_STEPS,
  forecastDateRange: null,
  predictResult: null,
  forecastLoading: false,
  forecastError: null,

  setSteps: (steps: string) => {
    set({ steps })
  },

  setForecastDateRange: (range) => {
    set({ forecastDateRange: range })
  },

  fetchForecast: async (params) => {
    const targetTicker = params?.ticker ?? get().ticker
    const targetModel = params?.modelType ?? get().modelType
    const targetSteps = params?.steps ?? get().steps
    const targetRange =
      params?.dateRange !== undefined ? params.dateRange : get().forecastDateRange

    if (!targetTicker) return

    set({ forecastLoading: true, forecastError: null })

    try {
      // Eksekusi inferensi peramalan harga saham via Cloudflare Worker Edge API
      const data = await fetchForecastPrediction({
        ticker: targetTicker,
        modelType: targetModel,
        steps: parseInt(targetSteps, 10),
        startDate: targetRange?.start,
        endDate: targetRange?.end,
      })

      set({ predictResult: data, forecastLoading: false })
    } catch (err: unknown) {
      const message = extractErrorMessage(
        err,
        'Terjadi kesalahan saat memproses peramalan harga saham',
      )
      set({ forecastError: message, forecastLoading: false })
    }
  },
})
