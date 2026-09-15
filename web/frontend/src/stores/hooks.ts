import { useShallow } from 'zustand/react/shallow'
import { useStockStore } from './useStockStore'

export const useForecastState = () =>
  useStockStore(
    useShallow((state) => ({
      ticker: state.ticker,
      modelType: state.modelType,
      steps: state.steps,
      forecastDateRange: state.forecastDateRange,
      predictResult: state.predictResult,
      loading: state.forecastLoading,
      error: state.forecastError,
      setSteps: state.setSteps,
      setModelType: state.setModelType,
      setForecastDateRange: state.setForecastDateRange,
      fetchForecast: state.fetchForecast,
    })),
  )

export const useHistoryState = () =>
  useStockStore(
    useShallow((state) => {
      const records = state.historyResult?.data || []
      return {
        ticker: state.ticker,
        dateRange: state.dateRange,
        historyResult: state.historyResult,
        loading: state.historyLoading,
        error: state.historyError,
        minDate: records[0]?.date,
        maxDate: records.length > 0 ? records[records.length - 1]?.date : undefined,
        setDateRange: state.setDateRange,
        fetchHistory: state.fetchHistory,
      }
    }),
  )

export const useHeaderState = () =>
  useStockStore(
    useShallow((state) => ({
      ticker: state.ticker,
      setTicker: state.setTicker,
      availableTickers: state.availableTickers,
      loadingTickers: state.loadingTickers,
    })),
  )
