import { useState, useEffect } from 'react'
import Chart from 'react-apexcharts'
import type { ApexOptions } from 'apexcharts'
import { Card, Center, EmptyState, Overlay, Spinner } from '@astryxdesign/core'
import { useTheme } from '@astryxdesign/core/theme'
import { useStockStore, useShallow } from '@/stores'
import { getApexThemeOptions } from '@/configs'
import { formatCurrency } from '@/utils'

export function UnifiedStockChart() {
  const [mounted, setMounted] = useState(false)
  const { mode } = useTheme()
  const isDark = mode === 'dark'

  const { ticker, model, historyData, forecastData, loading } = useStockStore(
    useShallow((state) => ({
      ticker: state.ticker,
      model: state.model,
      historyData: state.historyData,
      forecastData: state.forecastData,
      loading: state.loading,
    })),
  )

  useEffect(() => {
    setMounted(true)
  }, [])

  const hasHistory = historyData && historyData.length > 0
  const hasForecast = forecastData && forecastData.length > 0
  const hasAnyData = hasHistory || hasForecast

  // Urutkan riwayat secara kronologis
  const sortedHistory = hasHistory
    ? [...historyData].sort((a, b) => a.date.localeCompare(b.date))
    : []

  const lastHistPoint = sortedHistory.length > 0 ? sortedHistory[sortedHistory.length - 1] : null
  const splitTimestamp = lastHistPoint ? new Date(lastHistPoint.date).getTime() : undefined

  // Series 1: Candlestick (Riwayat Pasar)
  const candleSeries = {
    name: `${ticker} (Riwayat OHLC)`,
    type: 'candlestick',
    data: sortedHistory.map((d) => ({
      x: new Date(d.date).getTime(),
      y: [d.open, d.high, d.low, d.close] as [number, number, number, number],
    })),
  }

  // Series 2: Line (Prediksi Model)
  // Menghubungkan harga penutupan terakhir riwayat ke titik prediksi pertama agar mulus
  const forecastLinePoints: { x: number; y: number }[] = []
  if (lastHistPoint && hasForecast) {
    forecastLinePoints.push({
      x: new Date(lastHistPoint.date).getTime(),
      y: lastHistPoint.close,
    })
  }
  forecastData.forEach((p) => {
    forecastLinePoints.push({
      x: new Date(p.date).getTime(),
      y: p.predicted_price,
    })
  })

  const lineSeries = {
    name: `Prediksi ${model.toUpperCase()}`,
    type: 'line',
    data: forecastLinePoints,
  }

  const series = [candleSeries, lineSeries]

  const baseOptions = getApexThemeOptions(isDark)

  const options: ApexOptions = {
    ...baseOptions,
    chart: {
      ...baseOptions.chart,
      type: 'candlestick',
      stacked: false,
      animations: {
        enabled: true,
        easing: 'easeinout',
        speed: 600,
      },
    },
    colors: ['#10b981', '#6366f1'],
    stroke: {
      width: [1, 3],
      curve: ['straight', 'smooth'],
      dashArray: [0, 4], // Garis putus-putus untuk proyeksi
    },
    plotOptions: {
      candlestick: {
        colors: {
          upward: '#10b981',
          downward: '#ef4444',
        },
        wick: {
          useFillColor: true,
        },
      },
    },
    markers: {
      size: [0, 4],
      colors: ['#6366f1'],
      strokeColors: isDark ? '#1e1e24' : '#ffffff',
      strokeWidth: 2,
      hover: {
        sizeOffset: 3,
      },
    },
    annotations: splitTimestamp
      ? {
          xaxis: [
            {
              x: splitTimestamp,
              borderColor: '#6366f1',
              borderWidth: 2,
              strokeDashArray: 5,
              label: {
                borderColor: '#6366f1',
                orientation: 'horizontal',
                style: {
                  color: '#ffffff',
                  background: '#6366f1',
                  fontFamily: 'Figtree, sans-serif',
                  fontSize: '11px',
                  fontWeight: 600,
                },
                text: 'Batas Riwayat / Awal Prediksi',
              },
            },
          ],
        }
      : undefined,
    tooltip: {
      ...baseOptions.tooltip,
      shared: true,
      custom: ({ seriesIndex, dataPointIndex, w }) => {
        const isCandle = seriesIndex === 0
        const isLine = seriesIndex === 1

        const dateTimestamp = w.globals.seriesX[seriesIndex]?.[dataPointIndex]
        const dateStr = dateTimestamp ? new Date(dateTimestamp).toLocaleDateString('id-ID', {
          weekday: 'short',
          year: 'numeric',
          month: 'short',
          day: 'numeric',
        }) : ''

        if (isCandle) {
          const o = w.globals.seriesCandleO[seriesIndex]?.[dataPointIndex]
          const h = w.globals.seriesCandleH[seriesIndex]?.[dataPointIndex]
          const l = w.globals.seriesCandleL[seriesIndex]?.[dataPointIndex]
          const c = w.globals.seriesCandleC[seriesIndex]?.[dataPointIndex]
          const isUp = c >= o
          const candleColor = isUp ? '#10b981' : '#ef4444'

          return `<div style="padding:10px 14px;font-size:12px;line-height:1.7;">
            <div style="font-weight:600;margin-bottom:4px;color:${isDark ? '#e2e8f0' : '#1e293b'}">${dateStr}</div>
            <div style="color:${candleColor};font-weight:700;font-size:14px;margin-bottom:4px;">
              Close: ${formatCurrency(c)}
            </div>
            <div>Open: <b>${formatCurrency(o)}</b></div>
            <div>High: <b style="color:#10b981">${formatCurrency(h)}</b></div>
            <div>Low: <b style="color:#ef4444">${formatCurrency(l)}</b></div>
            <div style="margin-top:4px;padding-top:4px;border-top:1px dashed ${isDark ? '#334155' : '#e2e8f0'};font-size:11px;color:#94a3b8">
              Data Riwayat Pasar IDX
            </div>
          </div>`
        }

        if (isLine) {
          const val = w.globals.series[seriesIndex]?.[dataPointIndex]
          return `<div style="padding:10px 14px;font-size:12px;line-height:1.7;">
            <div style="font-weight:600;margin-bottom:4px;color:${isDark ? '#e2e8f0' : '#1e293b'}">${dateStr}</div>
            <div style="color:#6366f1;font-weight:700;font-size:14px;">
              Proyeksi ${model.toUpperCase()}: ${formatCurrency(val)}
            </div>
            <div style="margin-top:4px;padding-top:4px;border-top:1px dashed ${isDark ? '#334155' : '#e2e8f0'};font-size:11px;color:#94a3b8">
              Prediksi Model Deep Learning
            </div>
          </div>`
        }

        return ''
      },
    },
    legend: {
      show: true,
      position: 'top',
      horizontalAlign: 'right',
      fontSize: '12px',
      markers: {
        shape: 'circle',
      },
    },
  }

  return (
    <Card variant="default" padding={4} minHeight={440}>
      {loading && !hasAnyData && (
        <Center height={400}>
          <Spinner size="lg" label="Mengambil riwayat harga dan memproses prediksi..." />
        </Center>
      )}

      {!hasAnyData && !loading && (
        <Center height={400}>
          <EmptyState
            title="Grafik Belum Dimuat"
            description="Atur rentang tanggal riwayat dan prediksi di atas, lalu klik tombol 'Jalankan Analisis'."
            headingLevel={4}
          />
        </Center>
      )}

      {hasAnyData && (
        <Overlay
          isOpen={loading}
          position="fill"
          align="center"
          scrim={isDark ? 'dark' : 'light'}
          content={<Spinner size="lg" label="Memperbarui data dan inferensi model..." />}
        >
          {mounted && (
            <Chart
              key={`${mode}-${ticker}-${model}-${sortedHistory.length}-${forecastData.length}`}
              options={options}
              series={series}
              type="candlestick"
              height={420}
              width="100%"
            />
          )}
        </Overlay>
      )}
    </Card>
  )
}
