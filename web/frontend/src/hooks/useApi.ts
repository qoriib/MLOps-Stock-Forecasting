import { useState, useCallback } from 'react'
import { useToast } from '@astryxdesign/core/Toast'

export function useApi() {
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const toast = useToast()

  const apiBase = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

  const request = useCallback(
    async <T>(endpoint: string, options?: RequestInit): Promise<T | null> => {
      setLoading(true)
      setError(null)

      try {
        const url = endpoint.startsWith('http') ? endpoint : `${apiBase}${endpoint}`
        const res = await fetch(url, options)

        if (!res.ok) {
          const errData = await res.json().catch(() => ({ detail: null }))
          const msg = errData?.detail || `HTTP ${res.status}: Gagal memproses permintaan`
          throw new Error(msg)
        }

        const data: T = await res.json()
        return data
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Terjadi kesalahan sistem yang tidak terduga'
        setError(msg)
        toast({ body: msg, type: 'error' })
        return null
      } finally {
        setLoading(false)
      }
    },
    [apiBase, toast],
  )

  return { request, loading, error, setError, toast }
}
