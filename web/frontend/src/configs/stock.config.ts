import type { DateRangePreset, DateRange } from '@astryxdesign/core/DateRangeInput'
import { toISODate, getDaysAgoDate } from '@/utils/date.util'

export const DEFAULT_MODEL_TYPE = 'lstm'
export const DEFAULT_FORECAST_STEPS = '7'
export const DEFAULT_HISTORY_LIMIT = 500
export const DEFAULT_HISTORY_DISPLAY_COUNT = 30

export const MODEL_OPTIONS = [
  { value: 'lstm', label: 'Model: LSTM' },
  { value: 'gru', label: 'Model: GRU' },
]

export const STEP_OPTIONS = [
  { value: '7', label: '7 Hari' },
  { value: '14', label: '14 Hari' },
  { value: '30', label: '30 Hari' },
  { value: '60', label: '60 Hari' },
  { value: '90', label: '90 Hari' },
]

export const DATE_RANGE_PRESETS: DateRangePreset[] = [
  {
    label: '7 Hari Terakhir',
    getRange: (): DateRange => {
      const end = new Date()
      const start = getDaysAgoDate(6)
      return { start: toISODate(start), end: toISODate(end) }
    },
  },
  {
    label: '30 Hari Terakhir',
    getRange: (): DateRange => {
      const end = new Date()
      const start = getDaysAgoDate(29)
      return { start: toISODate(start), end: toISODate(end) }
    },
  },
  {
    label: '90 Hari Terakhir',
    getRange: (): DateRange => {
      const end = new Date()
      const start = getDaysAgoDate(89)
      return { start: toISODate(start), end: toISODate(end) }
    },
  },
  {
    label: '1 Tahun',
    getRange: (): DateRange => {
      const end = new Date()
      const start = new Date()
      start.setFullYear(end.getFullYear() - 1)
      return { start: toISODate(start), end: toISODate(end) }
    },
  },
  {
    label: 'Maksimal',
    getRange: (): DateRange => {
      const end = new Date()
      const start = new Date(2021, 8, 3)
      return { start: toISODate(start), end: toISODate(end) }
    },
  },
]
