import { createFileRoute } from '@tanstack/react-router'
import { useState, useEffect, useCallback, useMemo } from 'react'
import { VStack } from '@astryxdesign/core/Stack'
import { useStock } from '@/context/StockContext'
import { useApi } from '@/hooks/useApi'
import { HistoryControls } from '@/components/history/HistoryControls'
import { HistoryChart } from '@/components/history/HistoryChart'
import { HistoryTable } from '@/components/history/HistoryTable'
import { ErrorAlert } from '@/components/common/ErrorAlert'
import { LoadingIndicator } from '@/components/common/LoadingIndicator'
import type { HistoricalResponse } from '@/types/stock'
import type { DateRange } from '@astryxdesign/core/DateRangeInput'

export const Route = createFileRoute('/history')({ component: HistoryPage })

export function HistoryPage() {
  const { ticker } = useStock()
  const [dateRange, setDateRange] = useState<DateRange | null>(null)
  const [historyResult, setHistoryResult] = useState<HistoricalResponse | null>(null)
  const { request, loading, error } = useApi()

  // Ambil dataset historis yang cukup besar agar filter DateRangeInput fleksibel
  const loadHistory = useCallback(async () => {
    if (!ticker) return
    const data = await request<HistoricalResponse>(`/api/stocks/${ticker}?limit=500`)
    if (data) {
      setHistoryResult(data)
    }
  }, [ticker, request])

  useEffect(() => {
    if (ticker) {
      loadHistory()
    }
  }, [ticker, loadHistory])

  // Hitung batas tanggal minimum dan maksimum dari data yang tersedia
  const { minDate, maxDate } = useMemo(() => {
    const records = historyResult?.data || []
    if (records.length === 0) return { minDate: undefined, maxDate: undefined }
    return {
      minDate: records[0]?.date,
      maxDate: records[records.length - 1]?.date,
    }
  }, [historyResult])

  // Filter data berdasarkan rentang tanggal yang dipilih di DateRangeInput
  const filteredData = useMemo(() => {
    const records = historyResult?.data || []
    if (!dateRange || !dateRange.start || !dateRange.end) {
      // Jika filter kosong/dibersihkan, tampilkan 30 data terbaru secara default
      return records.slice(-30)
    }
    return records.filter(
      (item) => item.date >= dateRange.start && item.date <= dateRange.end
    )
  }, [historyResult, dateRange])

  return (
    <VStack gap={5}>
      <HistoryControls
        ticker={ticker}
        dateRange={dateRange}
        onDateRangeChange={setDateRange}
        minDate={minDate}
        maxDate={maxDate}
        loading={loading}
        onReload={loadHistory}
      />
      {error && <ErrorAlert message={error} />}
      {loading && !historyResult && (
        <LoadingIndicator label="Mengambil riwayat data pasar..." isCard />
      )}
      {filteredData.length > 0 && (
        <HistoryChart items={filteredData} ticker={ticker} />
      )}
      <HistoryTable items={filteredData} />
    </VStack>
  )
}
