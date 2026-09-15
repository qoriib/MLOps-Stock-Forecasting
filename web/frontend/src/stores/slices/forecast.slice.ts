import type { StateCreator } from 'zustand'
import {
  API_ENDPOINTS,
  DEFAULT_FORECAST_STEPS,
  DEFAULT_HISTORY_DISPLAY_COUNT,
} from '@/configs'
import { parseApiResponse, extractErrorMessage } from '@/utils'
import type { PredictResponse } from '@/types'
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
      const payload: Record<string, unknown> = {
        ticker: targetTicker,
        steps: parseInt(targetSteps, 10),
        model_type: targetModel,
      }

      if (targetRange?.start && targetRange?.end) {
        payload.start_date = targetRange.start
        payload.end_date = targetRange.end
      }

      const response = await fetch(API_ENDPOINTS.predict, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      const data = await parseApiResponse<PredictResponse>(
        response,
        'Gagal memproses peramalan saham',
      )

      // Fallback data historis jika belum terlampir pada respons
      if (!data.history || data.history.length === 0) {
        try {
          const historyResponse = await fetch(
            API_ENDPOINTS.stockHistory(
              targetTicker,
              DEFAULT_HISTORY_DISPLAY_COUNT,
              targetRange?.start,
              targetRange?.end,
            ),
          )
          if (historyResponse.ok) {
            const historyJson = await historyResponse.json()
            data.history = historyJson.data
          }
        } catch {
          // Abaikan fallback jika gagal
        }
      }

      set({ predictResult: data, forecastLoading: false })
    } catch (err: unknown) {
      const message = extractErrorMessage(
        err,
        'Terjadi kesalahan sistem saat peramalan',
      )
      set({ forecastError: message, forecastLoading: false })
    }
  },
})
