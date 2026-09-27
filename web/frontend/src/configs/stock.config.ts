import type { DateRangePreset, DateRange } from '@astryxdesign/core/DateRangeInput'
import { toISODate } from '@/utils/date.util'

export const DEFAULT_MODEL = 'lstm'
export const DEFAULT_TICKER = 'BBCA.JK'

/**
 * Presets rentang tanggal riwayat historis
 */
export const HISTORY_RANGE_PRESETS: DateRangePreset[] = [
  {
    label: '1 Bulan Terakhir',
    getRange: (): DateRange => {
      const end = new Date(2026, 8, 25) // Sep 25, 2026
      const start = new Date(2026, 7, 25) // Aug 25, 2026
      return { start: toISODate(start), end: toISODate(end) }
    },
  },
  {
    label: '3 Bulan Terakhir',
    getRange: (): DateRange => {
      const end = new Date(2026, 8, 25)
      const start = new Date(2026, 5, 25)
      return { start: toISODate(start), end: toISODate(end) }
    },
  },
  {
    label: '6 Bulan Terakhir',
    getRange: (): DateRange => {
      const end = new Date(2026, 8, 25)
      const start = new Date(2026, 2, 25)
      return { start: toISODate(start), end: toISODate(end) }
    },
  },
  {
    label: '1 Tahun',
    getRange: (): DateRange => {
      const end = new Date(2026, 8, 25)
      const start = new Date(2025, 8, 25)
      return { start: toISODate(start), end: toISODate(end) }
    },
  },
  {
    label: 'Semua Riwayat',
    getRange: (): DateRange => {
      const end = new Date(2026, 8, 25)
      const start = new Date(2024, 8, 27) // Earliest data in MongoDB
      return { start: toISODate(start), end: toISODate(end) }
    },
  },
]

/**
 * Presets rentang tanggal peramalan ke depan
 */
export const FORECAST_RANGE_PRESETS: DateRangePreset[] = [
  {
    label: '7 Hari ke Depan',
    getRange: (): DateRange => {
      const start = new Date(2026, 8, 26) // Sep 26, 2026
      const end = new Date(2026, 9, 3) // Oct 3, 2026
      return { start: toISODate(start), end: toISODate(end) }
    },
  },
  {
    label: '14 Hari ke Depan',
    getRange: (): DateRange => {
      const start = new Date(2026, 8, 26)
      const end = new Date(2026, 9, 10)
      return { start: toISODate(start), end: toISODate(end) }
    },
  },
  {
    label: '30 Hari ke Depan',
    getRange: (): DateRange => {
      const start = new Date(2026, 8, 26)
      const end = new Date(2026, 9, 26)
      return { start: toISODate(start), end: toISODate(end) }
    },
  },
]
