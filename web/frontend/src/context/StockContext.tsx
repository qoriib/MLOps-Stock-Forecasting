import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react'
import type { ModelInfo, ModelsResponse } from '@/types/stock'

export interface StockContextType {
  ticker: string
  setTicker: (ticker: string) => void
  availableTickers: string[]
  availableModels: ModelInfo[]
  loadingTickers: boolean
  backendHealthy: boolean | null
  checkHealth: () => Promise<void>
}

const StockContext = createContext<StockContextType | undefined>(undefined)

export function StockProvider({ children }: { children: ReactNode }) {
  const [ticker, setTicker] = useState<string>('')
  const [availableTickers, setAvailableTickers] = useState<string[]>([])
  const [availableModels, setAvailableModels] = useState<ModelInfo[]>([])
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
        if (tickers.length > 0) {
          setTicker((prev) => (prev && tickers.includes(prev) ? prev : tickers[0]))
        }
      } else {
        // Fallback coba ke /health
        const healthRes = await fetch(`${apiBase}/health`)
        if (healthRes.ok) {
          setBackendHealthy(true)
          const json = await healthRes.json()
          const tickers: string[] = json.available_tickers || []
          setAvailableTickers(tickers)
          if (tickers.length > 0) {
            setTicker((prev) => (prev && tickers.includes(prev) ? prev : tickers[0]))
          }
        } else {
          setBackendHealthy(false)
        }
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
        availableTickers,
        availableModels,
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
