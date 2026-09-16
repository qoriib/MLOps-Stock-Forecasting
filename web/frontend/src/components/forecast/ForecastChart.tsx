import { useState, useEffect } from 'react'
import Chart from 'react-apexcharts'
import { Card, Center, EmptyState, Overlay, Spinner } from '@astryxdesign/core'
import { Layout, LayoutHeader, LayoutContent } from '@astryxdesign/core/Layout'
import { useTheme } from '@astryxdesign/core/theme'
import { useStockStore, useShallow } from '@/stores'
import { getApexThemeOptions } from '@/configs'
import { ForecastControls } from './ForecastControls'
import type { ApexOptions } from 'apexcharts'
import { formatCurrency } from '@/utils'

export function ForecastChart() {
  const [mounted, setMounted] = useState(false)
  const { mode } = useTheme()
  const isDark = mode === 'dark'

  const { predictResult, loading } = useStockStore(
    useShallow((state) => ({
      predictResult: state.predictResult,
      loading: state.forecastLoading,
    })),
  )

  useEffect(() => {
    setMounted(true)
  }, [])

  const history = predictResult?.history ?? []
  const predictions = predictResult?.predictions ?? []
  const hasData = predictions.length > 0

  const histSorted = [...history].sort((a, b) => a.date.localeCompare(b.date))
  const lastHist = histSorted[histSorted.length - 1]
  const lastHistDate = lastHist?.date

  // Gabungkan data historis dan prediksi ke dalam satu deret data kontinu
  const combinedData: { x: string; y: number; isForecast?: boolean }[] = [
    ...histSorted.map((d) => ({
      x: d.date,
      y: d.close,
      isForecast: false,
    })),
    ...predictions.map((d) => ({
      x: d.date,
      y: d.predicted_price,
      isForecast: true,
    })),
  ]

  const series = [
    {
      name: 'Harga',
      data: combinedData.map((d) => ({ x: d.x, y: d.y })),
    },
  ]

  const baseOptions = getApexThemeOptions(isDark)
  const splitTimestamp = lastHistDate ? new Date(lastHistDate).getTime() : undefined

  const options: ApexOptions = {
    ...baseOptions,
    chart: {
      ...baseOptions.chart,
      type: 'line',
    },
    colors: ['#3b82f6'],
    stroke: {
      curve: 'smooth',
      width: 2.5,
    },
    markers: {
      size: 0,
      hover: { sizeOffset: 3 },
      strokeColors: isDark ? '#18181b' : '#ffffff',
      strokeWidth: 2,
    },
    annotations: splitTimestamp
      ? {
          xaxis: [
            {
              x: splitTimestamp,
              borderColor: isDark ? '#38bdf8' : '#2563eb',
              borderWidth: 2,
              strokeDashArray: 4,
              label: {
                borderColor: isDark ? '#38bdf8' : '#2563eb',
                orientation: 'horizontal',
                style: {
                  color: '#ffffff',
                  background: isDark ? '#0284c7' : '#2563eb',
                  fontFamily: 'Figtree, sans-serif',
                  fontSize: '11px',
                  fontWeight: 600,
                },
                text: 'Awal Prediksi',
              },
            },
          ],
        }
      : undefined,
    tooltip: {
      ...baseOptions.tooltip,
      y: {
        formatter: (val) => formatCurrency(val),
        title: {
          formatter: (_seriesName, opts) => {
            const index = opts?.dataPointIndex ?? -1
            const pt = index >= 0 ? combinedData[index] : undefined
            if (pt?.isForecast) {
              return 'Harga Prediksi: '
            }
            return 'Harga Historis: '
          },
        },
      },
    },
    legend: {
      show: false,
    },
  }

  return (
    <Card variant="default">
      <Layout
        defaultHasDividers
        header={
          <LayoutHeader>
            <ForecastControls />
          </LayoutHeader>
        }
        content={
          <LayoutContent>
            {loading && !hasData && (
              <Center height={320}>
                <Spinner size="lg" label="Menjalankan inferensi model..." />
              </Center>
            )}
            {!hasData && !loading && (
              <Center height={320}>
                <EmptyState
                  title="Siap Melakukan Peramalan"
                  description="Tentukan parameter dan rentang riwayat di atas, lalu klik tombol 'Jalankan Inferensi'."
                  headingLevel={4}
                />
              </Center>
            )}
            {hasData && (
              <Overlay
                isOpen={loading}
                position="fill"
                align="center"
                scrim={isDark ? 'dark' : 'light'}
                content={<Spinner size="lg" label="Menjalankan inferensi model..." />}
              >
                {mounted && (
                  <Chart
                    key={mode}
                    options={options}
                    series={series}
                    type="line"
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

