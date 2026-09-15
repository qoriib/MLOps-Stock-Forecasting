import { useState, useEffect } from 'react'
import { Button, DateRangeInput, Heading, HStack, Toolbar } from '@astryxdesign/core'
import { useHistoryState } from '@/stores'
import { DATE_RANGE_PRESETS } from '@/configs'
import type { ISODateString } from '@astryxdesign/core/Calendar'
import type { DateRange } from '@astryxdesign/core/DateRangeInput'

export function HistoryControls() {
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
        <Heading level={4}>Riwayat Harga</Heading>
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
