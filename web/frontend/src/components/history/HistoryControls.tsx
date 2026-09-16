import { useState, useEffect } from 'react'
import {
  Button,
  DateRangeInput,
  Heading,
  HStack,
  Toolbar,
  SegmentedControl,
  SegmentedControlItem,
} from '@astryxdesign/core'
import { useHistoryState } from '@/stores'
import { DATE_RANGE_PRESETS } from '@/configs'
import type { ISODateString } from '@astryxdesign/core/Calendar'
import type { DateRange } from '@astryxdesign/core/DateRangeInput'

export type ChartType = 'candlestick' | 'line'
export type PriceField = 'close' | 'open' | 'high' | 'low'

interface HistoryControlsProps {
  chartType: ChartType
  onChartTypeChange: (type: ChartType) => void
  priceField: PriceField
  onPriceFieldChange: (field: PriceField) => void
}

export function HistoryControls({
  chartType,
  onChartTypeChange,
  priceField,
  onPriceFieldChange,
}: HistoryControlsProps) {
  const {
    ticker,
    dateRange,
    setDateRange,
    loading,
    fetchHistory,
    minDate,
    maxDate,
  } = useHistoryState()

  const [draftRange, setDraftRange] = useState<DateRange | null>(dateRange)

  useEffect(() => {
    setDraftRange(dateRange)
  }, [dateRange])

  const handleSubmit = () => {
    setDateRange(draftRange)
    fetchHistory({ ticker, dateRange: draftRange })
  }

  return (
    <Toolbar
      label="Filter Riwayat Saham"
      startContent={
        <HStack gap={3} align="center">
          <Heading level={4}>Riwayat Harga</Heading>

          {/* Toggle: Candlestick vs Line */}
          <SegmentedControl
            value={chartType}
            onChange={(val) => onChartTypeChange(val as ChartType)}
            label="Tipe Grafik"
            size="sm"
          >
            <SegmentedControlItem value="candlestick" label="Candlestick" />
            <SegmentedControlItem value="line" label="Line" />
          </SegmentedControl>

          {/* Toggle kolom harga — hanya tampil saat mode line */}
          {chartType === 'line' && (
            <SegmentedControl
              value={priceField}
              onChange={(val) => onPriceFieldChange(val as PriceField)}
              label="Kolom Harga"
              size="sm"
            >
              <SegmentedControlItem value="close" label="Close" />
              <SegmentedControlItem value="open" label="Open" />
              <SegmentedControlItem value="high" label="High" />
              <SegmentedControlItem value="low" label="Low" />
            </SegmentedControl>
          )}
        </HStack>
      }
      endContent={
        <HStack gap={3} align="center">
          <DateRangeInput
            width={280}
            label="Rentang Tanggal Riwayat"
            isLabelHidden
            placeholder="Pilih rentang tanggal"
            value={draftRange}
            onChange={setDraftRange}
            presets={DATE_RANGE_PRESETS}
            min={minDate as ISODateString | undefined}
            max={maxDate as ISODateString | undefined}
            isDisabled={!ticker || loading}
          />
          <Button
            label="Tampilkan Riwayat"
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
