import { useEffect, useRef } from 'react'
import * as echarts from 'echarts'
import type { ECharts, EChartsOption } from 'echarts'
import { Card, Center, EmptyState, Overlay, Spinner } from '@astryxdesign/core'
import { useTheme } from '@astryxdesign/core/theme'
import { useStockStore, useShallow } from '@/stores'
import { getEChartsThemeOptions } from '@/configs'
import { formatCurrency } from '@/utils'

export function UnifiedStockChart() {
  const chartRef = useRef<HTMLDivElement>(null)
  const chartInstance = useRef<ECharts | null>(null)
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

  const hasHistory = historyData && historyData.length > 0
  const hasForecast = forecastData && forecastData.length > 0
  const hasAnyData = hasHistory || hasForecast

  // 1. Inisialisasi ECharts dan pasang ResizeObserver
  useEffect(() => {
    if (!chartRef.current) return

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current, undefined, {
        renderer: 'canvas',
      })
    }

    const handleResize = () => {
      chartInstance.current?.resize()
    }

    window.addEventListener('resize', handleResize)
    const resizeObserver = new ResizeObserver(() => handleResize())
    resizeObserver.observe(chartRef.current)

    return () => {
      window.removeEventListener('resize', handleResize)
      resizeObserver.disconnect()
      chartInstance.current?.dispose()
      chartInstance.current = null
    }
  }, [])

  // 2. Perbarui data dan opsi saat data / tema berubah
  useEffect(() => {
    if (!chartInstance.current || !hasAnyData) return

    const sortedHistory = hasHistory
      ? [...historyData].sort((a, b) => a.date.localeCompare(b.date))
      : []

    const lastHistory = sortedHistory.length > 0 ? sortedHistory[sortedHistory.length - 1] : null
    const lastHistoryDate = lastHistory?.date

    // Gabungkan seluruh tanggal unik (riwayat + prediksi) secara kronologis
    const historyDates = sortedHistory.map((d) => d.date)
    const forecastDates = forecastData.map((d) => d.date)

    // Tanggal gabungan (hindari duplikasi)
    const allDates = Array.from(new Set([...historyDates, ...forecastDates])).sort()

    // Data Candlestick ECharts: [Open, Close, Lowest, Highest]
    // Posisikan sesuai tanggal pada allDates
    const historyMap = new Map(sortedHistory.map((d) => [d.date, d]))
    const candleData: number[][] = allDates.map((date) => {
      const item = historyMap.get(date)
      if (!item) return [NaN, NaN, NaN, NaN]
      return [item.open, item.close, item.low, item.high]
    })

    // Data Line Prediksi:
    // Hubungkan dari titik penutupan terakhir data historis ke titik-titik prediksi
    const forecastMap = new Map(forecastData.map((p) => [p.date, p.predicted_price]))
    const lineData: (number | null)[] = allDates.map((date) => {
      if (date === lastHistoryDate && lastHistory) {
        return lastHistory.close
      }
      const pred = forecastMap.get(date)
      return pred !== undefined ? pred : null
    })

    const baseTheme = getEChartsThemeOptions(isDark)

    const option: EChartsOption = {
      ...baseTheme,
      legend: {
        show: true,
        top: '2%',
        right: '4%',
        textStyle: {
          color: isDark ? '#e2e8f0' : '#334155',
          fontFamily: 'Figtree, sans-serif',
          fontSize: 12,
        },
        data: [`${ticker} (Riwayat OHLC)`, `Prediksi ${model.toUpperCase()}`],
      },
      tooltip: {
        ...baseTheme.tooltip,
        formatter: (params) => {
          if (!Array.isArray(params) || params.length === 0) return ''
          const date = params[0]?.name || ''
          let html = `<div style="font-weight:600;margin-bottom:6px;color:${isDark ? '#e2e8f0' : '#1e293b'}">${date}</div>`

          for (const p of params) {
            if (p.seriesType === 'candlestick' && Array.isArray(p.value)) {
              // ECharts Candlestick value format: [index, open, close, lowest, highest]
              const [, open, close, low, high] = p.value as number[]
              const isUp = close >= open
              const candleColor = isUp ? '#10b981' : '#ef4444'

              html += `<div style="color:${candleColor};font-weight:700;font-size:13px;margin-bottom:4px;">`
              html += `Close: ${formatCurrency(close)}`
              html += `</div>`
              html += `<div style="font-size:11px;line-height:1.6;color:${isDark ? '#cbd5e1' : '#475569'}">`
              html += `Open: <b>${formatCurrency(open)}</b><br/>`
              html += `High: <b style="color:#10b981">${formatCurrency(high)}</b> | Low: <b style="color:#ef4444">${formatCurrency(low)}</b>`
              html += `</div>`
            } else if (p.seriesType === 'line' && typeof p.value === 'number') {
              html += `<div style="color:#6366f1;font-weight:700;font-size:13px;margin-top:6px;">`
              html += `Prediksi ${model.toUpperCase()}: ${formatCurrency(p.value)}`
              html += `</div>`
            }
          }
          return html
        },
      },
      xAxis: {
        ...baseTheme.xAxis,
        data: allDates,
      },
      series: [
        {
          name: `${ticker} (Riwayat OHLC)`,
          type: 'candlestick',
          data: candleData,
          itemStyle: {
            color: '#10b981', // Upward fill
            color0: '#ef4444', // Downward fill
            borderColor: '#10b981', // Upward border
            borderColor0: '#ef4444', // Downward border
          },
        },
        {
          name: `Prediksi ${model.toUpperCase()}`,
          type: 'line',
          data: lineData,
          smooth: true,
          showSymbol: true,
          symbolSize: 6,
          itemStyle: {
            color: '#6366f1',
          },
          lineStyle: {
            color: '#6366f1',
            width: 2.5,
            type: 'dashed',
          },
          markLine: lastHistoryDate
            ? {
                symbol: ['none', 'none'],
                data: [
                  {
                    xAxis: lastHistoryDate,
                    label: {
                      show: true,
                      formatter: 'Batas Riwayat / Awal Prediksi',
                      position: 'insideEndTop',
                      color: '#6366f1',
                      fontSize: 11,
                      fontWeight: 'bold',
                    },
                    lineStyle: {
                      color: '#6366f1',
                      type: 'dashed',
                      width: 2,
                    },
                  },
                ],
              }
            : undefined,
        },
      ],
    }

    chartInstance.current.setOption(option, true)
  }, [hasHistory, hasForecast, hasAnyData, historyData, forecastData, ticker, model, isDark])

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
          <div
            ref={chartRef}
            className="echarts-unified-container"
            style={{ width: '100%', height: '440px' }}
          />
        </Overlay>
      )}
    </Card>
  )
}
