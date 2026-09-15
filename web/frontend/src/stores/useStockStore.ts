import { create } from 'zustand'
import { createAppSlice } from './slices/app.slice'
import { createForecastSlice } from './slices/forecast.slice'
import { createHistorySlice } from './slices/history.slice'
import type { StockState } from './types'

export const useStockStore = create<StockState>()((...a) => ({
  ...createAppSlice(...a),
  ...createForecastSlice(...a),
  ...createHistorySlice(...a),
}))
