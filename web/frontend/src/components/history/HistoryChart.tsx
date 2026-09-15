import Chart from 'react-apexcharts'
import { useState, useEffect } from 'react'
import { useTheme } from '@astryxdesign/core/theme'
import { Card, Center, Heading, Overlay, Spinner, Text, VStack } from '@astryxdesign/core'
import { Layout, LayoutHeader, LayoutContent } from '@astryxdesign/core/Layout'
import { useStockStore, selectFilteredHistory, useShallow } from '@/stores'
import { getApexThemeOptions } from '@/configs'
import { HistoryControls } from './HistoryControls'
import type { ApexOptions } from 'apexcharts'

export function HistoryChart() {
  const { items, loading } = useStockStore(
    useShallow((state) => ({
      items: selectFilteredHistory(state),
      loading: state.historyLoading,
    })),
  )
  const [mounted, setMounted] = useState(false)
  const { mode } = useTheme()
  const isDark = mode === 'dark'

  useEffect(() => {
    setMounted(true)
  }, [])

  const hasData = items && items.length > 0
  const sortedData = hasData ? [...items].sort((a, b) => a.date.localeCompare(b.date)) : []

  const series = [
    {
      name: 'Harga Penutupan',
      data: sortedData.map((d) => ({
        x: d.date,
        y: d.close,
      })),
    },
  ]

  const baseOptions = getApexThemeOptions(isDark)

  const options: ApexOptions = {
    ...baseOptions,
    chart: {
      ...baseOptions.chart,
      type: 'area',
    },
    colors: ['#3b82f6'],
    dataLabels: { enabled: false },
    stroke: { curve: 'smooth', width: 2 },
    markers: {
      size: 0,
      hover: { sizeOffset: 3 },
      strokeColors: isDark ? '#18181b' : '#ffffff',
      strokeWidth: 2,
    },
    fill: {
      type: 'gradient',
      gradient: {
        shade: isDark ? 'dark' : 'light',
        type: 'vertical',
        shadeIntensity: 0.5,
        opacityFrom: isDark ? 0.45 : 0.35,
        opacityTo: 0.05,
      },
    },
  }

  return (
    <Card variant="default">
      <Layout
        defaultHasDividers
        header={
          <LayoutHeader>
            <HistoryControls />
          </LayoutHeader>
        }
        content={
          <LayoutContent>
            {loading && !hasData && (
              <Center height={320}>
                <Spinner size="lg" label="Mengambil riwayat data pasar..." />
              </Center>
            )}
            {!hasData && !loading && (
              <Center height={320}>
                <VStack align="center" gap={2}>
                  <Heading level={5}>Data Riwayat Belum Dimuat</Heading>
                  <Text color="secondary">
                    Tentukan rentang tanggal di atas, lalu klik "Tampilkan Riwayat".
                  </Text>
                </VStack>
              </Center>
            )}
            {hasData && (
              <Overlay
                isOpen={loading}
                position="fill"
                align="center"
                scrim={isDark ? 'dark' : 'light'}
                content={<Spinner size="lg" label="Mengambil riwayat data pasar..." />}
              >
                {mounted && (
                  <Chart
                    key={mode}
                    options={options}
                    series={series}
                    type="area"
                    height={320}
                    width="100%"
                  />
                )}
              </Overlay>
            )}
          </LayoutContent>
        }
      />
    </Card>
  )
}
