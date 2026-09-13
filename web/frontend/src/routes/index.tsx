import { createFileRoute } from '@tanstack/react-router'
import { useState, useEffect, useCallback } from 'react'
import { VStack } from '@astryxdesign/core/Stack'
import { useStock } from '@/context/StockContext'
import { useApi } from '@/hooks/useApi'
import { ForecastControls } from '@/components/forecast/ForecastControls'
import { ForecastChart } from '@/components/forecast/ForecastChart'
import { ForecastTable } from '@/components/forecast/ForecastTable'
import { ErrorAlert } from '@/components/common/ErrorAlert'
import { LoadingIndicator } from '@/components/common/LoadingIndicator'
import type { PredictResponse } from '@/types/stock'

export const Route = createFileRoute('/')({ component: ForecastPage })

export function ForecastPage() {
  const { ticker } = useStock()
  const [steps, setSteps] = useState<string>('30')
  const [predictResult, setPredictResult] = useState<PredictResponse | null>(null)
  const { request, loading, error } = useApi()

  const handlePredict = useCallback(async () => {
    if (!ticker) return
    const data = await request<PredictResponse>('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ticker, steps: parseInt(steps, 10) }),
    })
    if (data) {
      if (!data.history || data.history.length === 0) {
        try {
          const hRes = await fetch(`/api/stocks/${ticker}?limit=30`)
          if (hRes.ok) {
            const hJson = await hRes.json()
            data.history = hJson.data
          }
        } catch {
          // Fallback silently ignored
        }
      }
      setPredictResult(data)
    }
  }, [ticker, steps, request])

  useEffect(() => {
    if (ticker) {
      handlePredict()
    }
  }, [ticker, handlePredict])

  return (
    <VStack gap={5}>
      <ForecastControls
        ticker={ticker}
        steps={steps}
        onStepsChange={setSteps}
        loading={loading}
        onPredict={handlePredict}
      />
      {error && <ErrorAlert message={error} />}
      {loading && !predictResult && (
        <LoadingIndicator label="Menjalankan inferensi model..." isCard />
      )}
      {predictResult && (
        <ForecastChart
          predictions={predictResult.predictions}
          history={predictResult.history}
          ticker={ticker}
        />
      )}
      <ForecastTable items={predictResult?.predictions || []} />
    </VStack>
  )
}
