import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react'
import type { Model, ModelsResponse } from '@/types/stock'

export interface StockContextType {
  ticker: string
  setTicker: (ticker: string) => void
  modelType: string
  setModelType: (modelType: string) => void
  availableTickers: string[]
  availableModels: Model[]
  availableModelTypes: string[]
  loadingTickers: boolean
  backendHealthy: boolean | null
  checkHealth: () => Promise<void>
}

const StockContext = createContext<StockContextType | undefined>(undefined)

export function StockProvider({ children }: { children: ReactNode }) {
  const [ticker, setTicker] = useState<string>('')
  const [modelType, setModelType] = useState<string>('sarima')
  const [availableTickers, setAvailableTickers] = useState<string[]>([])
  const [availableModels, setAvailableModels] = useState<Model[]>([])
  const [availableModelTypes, setAvailableModelTypes] = useState<string[]>(['sarima', 'arima'])
  const [loadingTickers, setLoadingTickers] = useState<boolean>(true)
  const [backendHealthy, setBackendHealthy] = useState<boolean | null>(null)

  const checkHealth = useCallback(async () => {
    setLoadingTickers(true)
    try {
      const apiBase = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')
      const res = await fetch(`${apiBase}/api/models`)

      if (res.ok) {
        setBackendHealthy(true)
        const data: ModelsResponse = await res.json()
        const tickers: string[] = data.tickers || []
        setAvailableTickers(tickers)
        setAvailableModels(data.models || [])
        if (data.available_model_types && data.available_model_types.length > 0) {
          setAvailableModelTypes(data.available_model_types)
        }
        if (tickers.length > 0) {
          setTicker((prev) => (prev && tickers.includes(prev) ? prev : tickers[0]))
        }
      } else {
        setBackendHealthy(false)
      }
    } catch {
      setBackendHealthy(false)
    } finally {
      setLoadingTickers(false)
    }
  }, [])

  useEffect(() => {
    checkHealth()
  }, [checkHealth])

  return (
    <StockContext.Provider
      value={{
        ticker,
        setTicker,
        modelType,
        setModelType,
        availableTickers,
        availableModels,
        availableModelTypes,
        loadingTickers,
        backendHealthy,
        checkHealth,
      }}
    >
      {children}
    </StockContext.Provider>
  )
}

export function useStock() {
  const ctx = useContext(StockContext)
  if (!ctx) {
    throw new Error('useStock must be used within StockProvider')
  }
  return ctx
}
