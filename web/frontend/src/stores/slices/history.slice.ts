import type { StateCreator } from 'zustand'
import { extractErrorMessage } from '@/utils'
import { fetchStockHistoryData } from '@/services/apiForecast.service'
import type { DateRange } from '@astryxdesign/core/DateRangeInput'
import type { HistorySlice, StockState } from '../types'

export const createHistorySlice: StateCreator<
  StockState,
  [],
  [],
  HistorySlice
> = (set, get) => ({
  dateRange: null,
  historyResult: null,
  historyLoading: false,
  historyError: null,

  setDateRange: (dateRange: DateRange | null) => {
    set({ dateRange })
  },

  fetchHistory: async (params) => {
    const targetTicker = params?.ticker ?? get().ticker
    const targetRange =
      params?.dateRange !== undefined ? params.dateRange : get().dateRange

    if (!targetTicker) return

    set({ historyLoading: true, historyError: null })

    try {
      const data = await fetchStockHistoryData(
        targetTicker,
        targetRange?.start,
        targetRange?.end,
      )

      set({ historyResult: data, historyLoading: false })
    } catch (err: unknown) {
      const message = extractErrorMessage(
        err,
        'Terjadi kesalahan saat memuat riwayat harga pasar',
      )
      set({ historyError: message, historyLoading: false })
    }
  },
})
