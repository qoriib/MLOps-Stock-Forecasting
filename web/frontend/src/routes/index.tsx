import { createFileRoute } from '@tanstack/react-router'
import { useState, useEffect, useCallback } from 'react'

import { Layout, LayoutHeader, LayoutContent, LayoutFooter } from '@astryxdesign/core/Layout'
import { Section } from '@astryxdesign/core/Section'
import { HStack, VStack } from '@astryxdesign/core/Stack'
import { Heading } from '@astryxdesign/core/Heading'
import { Text } from '@astryxdesign/core/Text'
import { Button } from '@astryxdesign/core/Button'
import { Selector } from '@astryxdesign/core/Selector'
import { SegmentedControl, SegmentedControlItem } from '@astryxdesign/core/SegmentedControl'
import { Table, proportional, pixel } from '@astryxdesign/core/Table'
import type { TableColumn } from '@astryxdesign/core/Table'
import { StatusDot } from '@astryxdesign/core/StatusDot'
import { Token } from '@astryxdesign/core/Token'
import { Spinner } from '@astryxdesign/core/Spinner'

export const Route = createFileRoute('/')({ component: StockDashboard })

interface PredictionItem extends Record<string, unknown> {
  date: string
  predicted_price: number
  lower_bound: number | null
  upper_bound: number | null
}

interface PredictResponse {
  ticker: string
  model_name: string
  forecast_steps: number
  last_historical_date: string | null
  predictions: PredictionItem[]
}

interface HistoricalItem extends Record<string, unknown> {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

const API_BASE = '' // Uses Vite proxy in development; relative in prod

export function StockDashboard() {
  const [ticker, setTicker] = useState<string>('BBCA.JK')
  const [steps, setSteps] = useState<string>('30')
  const [activeTab, setActiveTab] = useState<string>('forecast')

  const [backendHealthy, setBackendHealthy] = useState<boolean | null>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  const [predictResult, setPredictResult] = useState<PredictResponse | null>(null)
  const [historicalData, setHistoricalData] = useState<HistoricalItem[]>([])
  const [loadingHistory, setLoadingHistory] = useState<boolean>(false)

  // Check backend health
  const checkHealth = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/health`)
      if (res.ok) {
        setBackendHealthy(true)
      } else {
        setBackendHealthy(false)
      }
    } catch {
      setBackendHealthy(false)
    }
  }, [])

  useEffect(() => {
    checkHealth()
  }, [checkHealth])

  // Run prediction
  const handlePredict = useCallback(async () => {
    setLoading(true)
    setErrorMsg(null)
    try {
      const res = await fetch(`${API_BASE}/api/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticker,
          steps: parseInt(steps, 10),
        }),
      })

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Gagal memuat inferensi' }))
        throw new Error(err.detail || `HTTP error ${res.status}`)
      }

      const data: PredictResponse = await res.json()
      setPredictResult(data)
      setBackendHealthy(true)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Terjadi kesalahan saat inferensi'
      setErrorMsg(msg)
    } finally {
      setLoading(false)
    }
  }, [ticker, steps])

  // Load historical data when ticker changes or view switched
  const loadHistory = useCallback(async () => {
    setLoadingHistory(true)
    try {
      const res = await fetch(`${API_BASE}/api/stocks/${ticker}?limit=20`)
      if (res.ok) {
        const json = await res.json()
        setHistoricalData(json.data || [])
      }
    } catch {
      // Historical fetch optional
    } finally {
      setLoadingHistory(false)
    }
  }, [ticker])

  useEffect(() => {
    handlePredict()
    loadHistory()
  }, [handlePredict, loadHistory])

  // Prediction columns definition
  const forecastColumns: TableColumn<PredictionItem>[] = [
    {
      key: 'date',
      header: 'Tanggal Bursa',
      width: proportional(1),
      renderCell: (row) => <Text weight="medium">{String(row.date)}</Text>,
    },
    {
      key: 'predicted_price',
      header: 'Prediksi Harga',
      width: proportional(1),
      renderCell: (row) => (
        <Text weight="semibold">
          Rp {Number(row.predicted_price).toLocaleString('id-ID', { minimumFractionDigits: 2 })}
        </Text>
      ),
    },
    {
      key: 'lower_bound',
      header: 'Batas Bawah (95% CI)',
      width: proportional(1),
      renderCell: (row) => (
        <Text color="secondary">
          {row.lower_bound != null
            ? `Rp ${Number(row.lower_bound).toLocaleString('id-ID', { minimumFractionDigits: 2 })}`
            : '—'}
        </Text>
      ),
    },
    {
      key: 'upper_bound',
      header: 'Batas Atas (95% CI)',
      width: proportional(1),
      renderCell: (row) => (
        <Text color="secondary">
          {row.upper_bound != null
            ? `Rp ${Number(row.upper_bound).toLocaleString('id-ID', { minimumFractionDigits: 2 })}`
            : '—'}
        </Text>
      ),
    },
  ]

  // Historical columns definition
  const historyColumns: TableColumn<HistoricalItem>[] = [
    {
      key: 'date',
      header: 'Tanggal',
      width: proportional(1),
      renderCell: (row) => <Text weight="medium">{String(row.date)}</Text>,
    },
    {
      key: 'open',
      header: 'Open',
      width: proportional(1),
      renderCell: (row) => `Rp ${Number(row.open).toLocaleString('id-ID')}`,
    },
    {
      key: 'high',
      header: 'High',
      width: proportional(1),
      renderCell: (row) => `Rp ${Number(row.high).toLocaleString('id-ID')}`,
    },
    {
      key: 'low',
      header: 'Low',
      width: proportional(1),
      renderCell: (row) => `Rp ${Number(row.low).toLocaleString('id-ID')}`,
    },
    {
      key: 'close',
      header: 'Close',
      width: proportional(1),
      renderCell: (row) => (
        <Text weight="semibold">Rp {Number(row.close).toLocaleString('id-ID')}</Text>
      ),
    },
    {
      key: 'volume',
      header: 'Volume',
      width: pixel(140),
      renderCell: (row) => Number(row.volume).toLocaleString('id-ID'),
    },
  ]

  return (
    <Layout
      contentWidth={1040}
      defaultHasDividers
      header={
        <LayoutHeader hasDivider>
          <HStack justify="space-between" align="center">
            <VStack gap={1}>
              <Heading level={2}>Sistem Peramalan Saham IDX</Heading>
              <Text color="secondary">
                MLOps Inference Dashboard · Time-Series Forecasting
              </Text>
            </VStack>
            <HStack gap={2} align="center">
              <StatusDot
                variant={backendHealthy ? 'success' : backendHealthy === false ? 'error' : 'neutral'}
                label={backendHealthy ? 'Backend Terhubung' : 'Backend Terputus'}
                isPulsing={backendHealthy === true}
              />
              <Text color={backendHealthy ? 'default' : 'secondary'} weight="medium">
                {backendHealthy ? 'Backend Aktif (Cloud Run / Local)' : 'Backend Offline'}
              </Text>
            </HStack>
          </HStack>
        </LayoutHeader>
      }
      content={
        <LayoutContent>
          <VStack gap={5}>
            {/* Control Panel Section */}
            <Section variant="section" padding={4} dividers={['bottom']}>
              <HStack gap={4} align="end">
                <Selector
                  label="Simbol Saham IDX"
                  options={[
                    { value: 'BBCA.JK', label: 'BBCA.JK — Bank Central Asia' },
                    { value: 'BBRI.JK', label: 'BBRI.JK — Bank Rakyat Indonesia' },
                  ]}
                  value={ticker}
                  onChange={(val) => setTicker(val)}
                  width={280}
                />
                <Selector
                  label="Horizon Peramalan"
                  options={[
                    { value: '7', label: '7 Hari Kerja (1 Pekan)' },
                    { value: '14', label: '14 Hari Kerja (2 Pekan)' },
                    { value: '30', label: '30 Hari Kerja (1 Bulan)' },
                    { value: '60', label: '60 Hari Kerja (2 Bulan)' },
                    { value: '90', label: '90 Hari Kerja (1 Triwulan)' },
                  ]}
                  value={steps}
                  onChange={(val) => setSteps(val)}
                  width={240}
                />
                <Button
                  label="Jalankan Inferensi"
                  variant="primary"
                  isLoading={loading}
                  onClick={handlePredict}
                />
              </HStack>
            </Section>

            {/* Error Notification */}
            {errorMsg && (
              <Section variant="muted" padding={3}>
                <HStack gap={2} align="center">
                  <StatusDot variant="error" label="Error" />
                  <Text color="error">{errorMsg}</Text>
                </HStack>
              </Section>
            )}

            {/* Metadata Summary Banner */}
            {predictResult && (
              <Section variant="muted" padding={3}>
                <HStack justify="space-between" align="center">
                  <HStack gap={2} align="center">
                    <Token label={predictResult.ticker} />
                    <Token label={`Model: ${predictResult.model_name}`} />
                    <Token label={`Horizon: ${predictResult.forecast_steps} Hari`} />
                    {predictResult.last_historical_date && (
                      <Token label={`Basis Data: ${predictResult.last_historical_date}`} />
                    )}
                  </HStack>
                  <Text color="secondary">
                    {predictResult.predictions.length} estimasi titik peramalan
                  </Text>
                </HStack>
              </Section>
            )}

            {/* View Switcher */}
            <HStack justify="space-between" align="center">
              <SegmentedControl
                label="Pilih Tampilan Data"
                value={activeTab}
                onChange={setActiveTab}
              >
                <SegmentedControlItem value="forecast" label="Hasil Peramalan" />
                <SegmentedControlItem value="history" label="Histori Terkini (20 Hari)" />
              </SegmentedControl>
              {(loading || loadingHistory) && <Spinner label="Memuat data..." />}
            </HStack>

            {/* Table Area */}
            <Section variant="section" padding={0}>
              {activeTab === 'forecast' ? (
                <Table
                  data={predictResult?.predictions || []}
                  columns={forecastColumns}
                  idKey="date"
                  hasHover
                  density="compact"
                />
              ) : (
                <Table
                  data={historicalData}
                  columns={historyColumns}
                  idKey="date"
                  hasHover
                  density="compact"
                />
              )}
            </Section>
          </VStack>
        </LayoutContent>
      }
      footer={
        <LayoutFooter hasDivider>
          <HStack justify="space-between" align="center">
            <Text color="secondary">
              MLOps Pipeline · DVC Data Versioning · FastAPI Backend · Astryx Design System
            </Text>
            <Button
              label="Periksa Status"
              size="sm"
              variant="ghost"
              onClick={checkHealth}
            />
          </HStack>
        </LayoutFooter>
      }
    />
  )
}
