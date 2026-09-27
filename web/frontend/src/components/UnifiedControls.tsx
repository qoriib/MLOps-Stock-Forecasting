import { useState, useEffect } from 'react'
import {
  Button,
  DateRangeInput,
  HStack,
  Selector,
  Text,
  VStack,
  Card,
  Badge,
} from '@astryxdesign/core'
import type { DateRange } from '@astryxdesign/core/DateRangeInput'
import { useStockStore, useShallow } from '@/stores'
import { HISTORY_RANGE_PRESETS, FORECAST_RANGE_PRESETS } from '@/configs'

export function UnifiedControls() {
  const {
    ticker,
    model,
    availableTickers,
    availableModels,
    loadingOptions,
    historyRange,
    forecastRange,
    loading,
    setTicker,
    setModel,
    setHistoryRange,
    setForecastRange,
    runAnalysis,
  } = useStockStore(
    useShallow((state) => ({
      ticker: state.ticker,
      model: state.model,
      availableTickers: state.availableTickers,
      availableModels: state.availableModels,
      loadingOptions: state.loadingOptions,
      historyRange: state.historyRange,
      forecastRange: state.forecastRange,
      loading: state.loading,
      setTicker: state.setTicker,
      setModel: state.setModel,
      setHistoryRange: state.setHistoryRange,
      setForecastRange: state.setForecastRange,
      runAnalysis: state.runAnalysis,
    })),
  )

  const [draftTicker, setDraftTicker] = useState(ticker)
  const [draftModel, setDraftModel] = useState(model)
  const [draftHistRange, setDraftHistRange] = useState<DateRange | null>(historyRange)
  const [draftForeRange, setDraftForeRange] = useState<DateRange | null>(forecastRange)

  useEffect(() => {
    setDraftTicker(ticker)
  }, [ticker])

  useEffect(() => {
    setDraftModel(model)
  }, [model])

  useEffect(() => {
    setDraftHistRange(historyRange)
  }, [historyRange])

  useEffect(() => {
    setDraftForeRange(forecastRange)
  }, [forecastRange])

  const tickerOptions = availableTickers.map((t) => ({
    value: t,
    label: t,
  }))

  const modelOptions = availableModels.map((m) => ({
    value: m,
    label: `Model: ${m.toUpperCase()}`,
  }))

  const handleApply = () => {
    setTicker(draftTicker)
    setModel(draftModel)
    setHistoryRange(draftHistRange)
    setForecastRange(draftForeRange)

    runAnalysis({
      ticker: draftTicker,
      model: draftModel,
      historyRange: draftHistRange,
      forecastRange: draftForeRange,
    })
  }

  return (
    <Card variant="default">
      <div style={{ padding: '20px 24px' }}>
        <VStack gap={4}>
          {/* Header Controls Bar */}
          <HStack justify="between" align="center" wrap="wrap" gap={3}>
            <HStack align="center" gap={2}>
              <Text weight="semibold" size="lg">
                Konfigurasi Parameter Analisis
              </Text>
              <Badge variant="neutral" label="Single Page Live Forecast" />
            </HStack>

            <Button
              label={loading ? 'Memproses...' : 'Jalankan Analisis'}
              variant="primary"
              isLoading={loading}
              isDisabled={loading || !draftTicker || !draftHistRange?.start || !draftForeRange?.start}
              onClick={handleApply}
            />
          </HStack>

          {/* Controls Form Grid */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: '16px',
              alignItems: 'end',
            }}
          >
            {/* Ticker Selector */}
            <VStack gap={1}>
              <Text size="sm" weight="medium" color="secondary">
                Emiten Saham (Ticker)
              </Text>
              <Selector
                isLabelHidden
                label="Pilih Saham"
                placeholder={loadingOptions ? 'Memuat ticker...' : 'Pilih Saham'}
                options={tickerOptions}
                value={draftTicker}
                onChange={setDraftTicker}
                isDisabled={loading || loadingOptions || tickerOptions.length === 0}
              />
            </VStack>

            {/* Model Architecture Selector */}
            <VStack gap={1}>
              <Text size="sm" weight="medium" color="secondary">
                Model Deep Learning
              </Text>
              <Selector
                isLabelHidden
                label="Pilih Arsitektur Model"
                placeholder={loadingOptions ? 'Memuat model...' : 'Pilih Model'}
                options={modelOptions}
                value={draftModel}
                onChange={setDraftModel}
                isDisabled={loading || loadingOptions || modelOptions.length === 0}
              />
            </VStack>

            {/* Date Range: Riwayat Pasar */}
            <VStack gap={1}>
              <Text size="sm" weight="medium" color="secondary">
                Rentang Riwayat Pasar (OHLC)
              </Text>
              <DateRangeInput
                label="Rentang Riwayat"
                isLabelHidden
                placeholder="Pilih rentang riwayat"
                value={draftHistRange}
                onChange={setDraftHistRange}
                presets={HISTORY_RANGE_PRESETS}
                isDisabled={loading}
              />
            </VStack>

            {/* Date Range: Prediksi */}
            <VStack gap={1}>
              <Text size="sm" weight="medium" color="secondary">
                Rentang Target Prediksi
              </Text>
              <DateRangeInput
                label="Rentang Prediksi"
                isLabelHidden
                placeholder="Pilih rentang prediksi"
                value={draftForeRange}
                onChange={setDraftForeRange}
                presets={FORECAST_RANGE_PRESETS}
                isDisabled={loading}
              />
            </VStack>
          </div>
        </VStack>
      </div>
    </Card>
  )
}
