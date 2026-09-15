import { DEFAULT_HISTORY_DISPLAY_COUNT } from '@/configs'
import type { HistoricalItem, HistoricalResponse } from '@/types'
import type { DateRange } from '@astryxdesign/core/DateRangeInput'
import type { StockState } from '../types'

// Referentially memoized selector cache to prevent React 19 / SSR hydration infinite loops
let lastHistoryResult: HistoricalResponse | null = null
let lastDateRange: DateRange | null = null
let cachedFilteredHistory: HistoricalItem[] = []

export const selectFilteredHistory = (state: StockState): HistoricalItem[] => {
  if (
    state.historyResult === lastHistoryResult &&
    state.dateRange === lastDateRange
  ) {
    return cachedFilteredHistory
  }

  lastHistoryResult = state.historyResult
  lastDateRange = state.dateRange

  const records = state.historyResult?.data || []
  if (!state.dateRange || !state.dateRange.start || !state.dateRange.end) {
    cachedFilteredHistory = records.slice(-DEFAULT_HISTORY_DISPLAY_COUNT)
  } else {
    cachedFilteredHistory = records.filter(
      (item) =>
        item.date >= state.dateRange!.start && item.date <= state.dateRange!.end,
    )
  }

  return cachedFilteredHistory
}

let lastMinMaxHistory: HistoricalResponse | null = null
let cachedMinMax: { minDate: string | undefined; maxDate: string | undefined } = {
  minDate: undefined,
  maxDate: undefined,
}

export const selectMinMaxDates = (state: StockState) => {
  if (state.historyResult === lastMinMaxHistory) {
    return cachedMinMax
  }

  lastMinMaxHistory = state.historyResult
  const records = state.historyResult?.data || []
  cachedMinMax = {
    minDate: records[0]?.date,
    maxDate: records.length > 0 ? records[records.length - 1]?.date : undefined,
  }
  return cachedMinMax
}
