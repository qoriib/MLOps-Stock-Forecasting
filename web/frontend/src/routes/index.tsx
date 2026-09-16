import { createFileRoute } from '@tanstack/react-router'
import { Banner, VStack } from '@astryxdesign/core'
import { useStockStore } from '@/stores'
import { ForecastChart } from '@/components/forecast/ForecastChart'
import { ForecastTable } from '@/components/forecast/ForecastTable'

export const Route = createFileRoute('/')({ component: ForecastPage })

function ForecastPage() {
  const error = useStockStore((state) => state.forecastError)

  return (
    <VStack gap={5}>
      {error && (
        <Banner
          status="error"
          title="Terjadi Kesalahan"
          description={error}
        />
      )}
      <ForecastChart />
      <ForecastTable />
    </VStack>
  )
}
