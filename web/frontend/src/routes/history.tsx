import { createFileRoute } from '@tanstack/react-router'
import { Banner, VStack } from '@astryxdesign/core'
import { useStockStore, useShallow } from '@/stores'
import { HistoryChart } from '@/components/history/HistoryChart'
import { HistoryTable } from '@/components/history/HistoryTable'

export const Route = createFileRoute('/history')({ component: HistoryPage })

function HistoryPage() {
  const { error, hasData } = useStockStore(
    useShallow((state) => ({
      error: state.historyError,
      hasData: (state.historyResult?.data.length ?? 0) > 0,
    })),
  )

  return (
    <VStack gap={5}>
      {error && (
        <Banner
          status="error"
          title="Terjadi Kesalahan"
          description={error}
        />
      )}
      <HistoryChart />
      {hasData && <HistoryTable />}
    </VStack>
  )
}

