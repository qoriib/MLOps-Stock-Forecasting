import { useState, useEffect } from 'react'
import {
  Button,
  DateRangeInput,
  Heading,
  HStack,
  Selector,
  Text,
  Toolbar,
} from '@astryxdesign/core'
import type { DateRange } from '@astryxdesign/core/DateRangeInput'
import { useForecastState } from '@/stores'
import { DATE_RANGE_PRESETS, MODEL_OPTIONS, STEP_OPTIONS } from '@/configs'

export function ForecastControls() {
  const {
    ticker,
    modelType,
    setModelType,
    steps,
    setSteps,
    forecastDateRange,
    setForecastDateRange,
    loading,
    fetchForecast,
  } = useForecastState()

  const [draftModelType, setDraftModelType] = useState<string>(modelType)
  const [draftSteps, setDraftSteps] = useState<string>(steps)
  const [draftDateRange, setDraftDateRange] = useState<DateRange | null>(
    forecastDateRange,
  )

  useEffect(() => {
    setDraftModelType(modelType)
  }, [modelType])

  useEffect(() => {
    setDraftSteps(steps)
  }, [steps])

  useEffect(() => {
    setDraftDateRange(forecastDateRange)
  }, [forecastDateRange])

  const handleSubmit = () => {
    setModelType(draftModelType)
    setSteps(draftSteps)
    setForecastDateRange(draftDateRange)
    fetchForecast({
      ticker,
      modelType: draftModelType,
      steps: draftSteps,
      dateRange: draftDateRange,
    })
  }

  return (
    <Toolbar
      label="Konfigurasi Peramalan"
      startContent={
        <HStack gap={2} align="center">
          <Heading level={4}>Peramalan Saham</Heading>
          <Text color="secondary">
            ({ticker || 'Memuat...'})
          </Text>
        </HStack>
      }
      endContent={
        <HStack gap={3} align="center" wrap="wrap">
          <DateRangeInput
            width={260}
            label="Rentang Tanggal Riwayat"
            isLabelHidden
            placeholder="Rentang riwayat historis"
            value={draftDateRange}
            onChange={setDraftDateRange}
            presets={DATE_RANGE_PRESETS}
            isDisabled={!ticker || loading}
          />
          <Selector
            label="Pilihan Model"
            isLabelHidden
            options={MODEL_OPTIONS}
            value={draftModelType}
            onChange={setDraftModelType}
            width={180}
            isDisabled={!ticker || loading}
          />
          <Selector
            label="Horizon"
            isLabelHidden
            options={STEP_OPTIONS}
            value={draftSteps}
            onChange={setDraftSteps}
            width={130}
            isDisabled={!ticker || loading}
          />
          <Button
            label="Jalankan Inferensi"
            variant="primary"
            isLoading={loading}
            isDisabled={!ticker || loading}
            onClick={handleSubmit}
          />
        </HStack>
      }
    />
  )
}
