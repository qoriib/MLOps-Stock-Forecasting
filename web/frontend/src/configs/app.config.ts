import type { DateRangePreset, DateRange } from '@astryxdesign/core/DateRangeInput'
import { toISODate } from '@/utils/date.util'

/**
 * Konfigurasi umum aplikasi peramalan saham.
 */
export const APP_CONFIG = {
  name: 'StockForecast',
  title: 'StockForecast - Stock Price Forecasting System',
} as const

/**
 * Returns a new Date offset by the given number of days from today.
 * Negative values go into the past, positive into the future.
 */
function daysFromToday(offset: number): Date {
  const d = new Date()
  d.setDate(d.getDate() + offset)
  return d
}

/** Today's date (used as the end of historical data and start of forecast). */
const TODAY = new Date()
const TOMORROW = daysFromToday(1)

/**
 * Default date ranges: last 5 years for history, next 30 days for forecast.
 */
export const DEFAULT_HISTORY_RANGE: DateRange = {
  start: toISODate(daysFromToday(-5 * 365)),
  end: toISODate(TODAY),
}

export const DEFAULT_FORECAST_RANGE: DateRange = {
  start: toISODate(TOMORROW),
  end: toISODate(daysFromToday(31)),
}

/**
 * Builds a historical range preset where end is always today.
 */
function createHistoricalRangePreset(label: string, daysBack: number): DateRangePreset {
  return {
    label,
    getRange: (): DateRange => ({
      start: toISODate(daysFromToday(-daysBack)),
      end: toISODate(new Date()),
    }),
  }
}

/**
 * Builds a forecast range preset starting from tomorrow for N days ahead.
 */
function createForecastRangePreset(label: string, daysAhead: number): DateRangePreset {
  return {
    label,
    getRange: (): DateRange => ({
      start: toISODate(daysFromToday(1)),
      end: toISODate(daysFromToday(daysAhead)),
    }),
  }
}

/**
 * Historical date range presets — all relative to today.
 */
export const HISTORY_RANGE_PRESETS: DateRangePreset[] = [
  createHistoricalRangePreset('Last 7 Days', 7),
  createHistoricalRangePreset('Last 14 Days', 14),
  createHistoricalRangePreset('Last 30 Days', 30),
  createHistoricalRangePreset('Last 3 Months', 90),
  createHistoricalRangePreset('Last 6 Months', 180),
  createHistoricalRangePreset('Last 1 Year', 365),
  createHistoricalRangePreset('Last 5 Years', 5 * 365),
]

/**
 * Forecast range presets — all starting from tomorrow relative to today.
 */
export const FORECAST_RANGE_PRESETS: DateRangePreset[] = [
  createForecastRangePreset('Next 7 Days', 7),
  createForecastRangePreset('Next 14 Days', 14),
  createForecastRangePreset('Next 30 Days', 30),
]
