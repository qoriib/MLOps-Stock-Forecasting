import { Card } from '@astryxdesign/core/Card'
import { Toolbar } from '@astryxdesign/core/Toolbar'
import { Heading } from '@astryxdesign/core/Heading'
import { Text } from '@astryxdesign/core/Text'
import { HStack } from '@astryxdesign/core/Stack'
import { Button } from '@astryxdesign/core/Button'
import {
  DateRangeInput,
  type DateRange,
  type DateRangePreset,
} from '@astryxdesign/core/DateRangeInput'
import type { ISODateString } from '@astryxdesign/core/Calendar'

interface HistoryControlsProps {
  ticker: string
  dateRange: DateRange | null
  onDateRangeChange: (range: DateRange | null) => void
  loading: boolean
  onReload: () => void
  minDate?: string
  maxDate?: string
}

function toISODate(d: Date): ISODateString {
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}` as ISODateString
}

// Preset rentang tanggal sesuai best practice Astryx
const PRESETS: DateRangePreset[] = [
  {
    label: '7 Hari Terakhir',
    getRange: (): DateRange => {
      const end = new Date()
      const start = new Date()
      start.setDate(end.getDate() - 6)
      return { start: toISODate(start), end: toISODate(end) }
    },
  },
  {
    label: '30 Hari Terakhir',
    getRange: (): DateRange => {
      const end = new Date()
      const start = new Date()
      start.setDate(end.getDate() - 29)
      return { start: toISODate(start), end: toISODate(end) }
    },
  },
  {
    label: '90 Hari Terakhir',
    getRange: (): DateRange => {
      const end = new Date()
      const start = new Date()
      start.setDate(end.getDate() - 89)
      return { start: toISODate(start), end: toISODate(end) }
    },
  },
  {
    label: 'Tahun Berjalan (YTD)',
    getRange: (): DateRange => {
      const end = new Date()
      const start = new Date(end.getFullYear(), 0, 1)
      return { start: toISODate(start), end: toISODate(end) }
    },
  },
  {
    label: '1 Tahun Terakhir',
    getRange: (): DateRange => {
      const end = new Date()
      const start = new Date()
      start.setFullYear(end.getFullYear() - 1)
      return { start: toISODate(start), end: toISODate(end) }
    },
  },
]

export function HistoryControls({
  ticker,
  dateRange,
  onDateRangeChange,
  loading,
  onReload,
  minDate,
  maxDate,
}: HistoryControlsProps) {
  return (
    <Card variant="default" padding={0}>
      <Toolbar
        label="Filter Riwayat Saham"
        size="sm"
        startContent={
          <HStack gap={2} align="center">
            <Heading level={4}>Riwayat Pasar</Heading>
            <Text color="secondary" size="sm">
              ({ticker || 'Memuat...'})
            </Text>
          </HStack>
        }
        endContent={
          <HStack gap={3} align="center">
            <DateRangeInput
              label="Rentang Tanggal Riwayat"
              isLabelHidden
              placeholder="Pilih rentang tanggal"
              value={dateRange}
              onChange={onDateRangeChange}
              presets={PRESETS}
              size="sm"
              width={260}
              min={minDate as ISODateString | undefined}
              max={maxDate as ISODateString | undefined}
              isDisabled={!ticker || loading}
            />

            <Button
              label="Muat Ulang"
              variant="secondary"
              size="sm"
              isLoading={loading}
              isDisabled={!ticker || loading}
              onClick={onReload}
            />
          </HStack>
        }
      />
    </Card>
  )
}
