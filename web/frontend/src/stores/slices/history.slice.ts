import type { StateCreator } from 'zustand'
import { API_ENDPOINTS, DEFAULT_HISTORY_LIMIT } from '@/configs'
import { parseApiResponse, extractErrorMessage } from '@/utils'
import type { HistoricalResponse } from '@/types'
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
      const response = await fetch(
        API_ENDPOINTS.stockHistory(
          targetTicker,
          DEFAULT_HISTORY_LIMIT,
          targetRange?.start,
          targetRange?.end,
        ),
      )

      const data = await parseApiResponse<HistoricalResponse>(
        response,
        'Gagal memuat riwayat data pasar',
      )
      set({ historyResult: data, historyLoading: false })
    } catch (err: unknown) {
      const message = extractErrorMessage(
        err,
        'Terjadi kesalahan sistem saat memuat riwayat',
      )
      set({ historyError: message, historyLoading: false })
    }
  },
})
