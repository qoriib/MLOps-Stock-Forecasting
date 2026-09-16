import Chart from 'react-apexcharts'
import { useState, useEffect } from 'react'
import { useTheme } from '@astryxdesign/core/theme'
import { Card, Center, Heading, Overlay, Spinner, Text, VStack } from '@astryxdesign/core'
import { Layout, LayoutHeader, LayoutContent } from '@astryxdesign/core/Layout'
import { useStockStore, selectFilteredHistory, useShallow } from '@/stores'
import { getApexThemeOptions } from '@/configs'
import { HistoryControls } from './HistoryControls'
import type { ChartType, PriceField } from './HistoryControls'
import type { ApexOptions } from 'apexcharts'

const PRICE_FIELD_LABELS: Record<PriceField, string> = {
  close: 'Harga Penutupan',
  open: 'Harga Pembukaan',
  high: 'Harga Tertinggi',
  low: 'Harga Terendah',
}

const PRICE_FIELD_COLORS: Record<PriceField, string> = {
  close: '#3b82f6',
  open: '#8b5cf6',
  high: '#10b981',
  low: '#f59e0b',
}

export function HistoryChart() {
  const { items, loading, ticker, dateRange, fetchHistory } = useStockStore(
    useShallow((state) => ({
      items: selectFilteredHistory(state),
      loading: state.historyLoading,
      ticker: state.ticker,
      dateRange: state.dateRange,
      fetchHistory: state.fetchHistory,
    })),
  )
  const [mounted, setMounted] = useState(false)
  const [chartType, setChartType] = useState<ChartType>('candlestick')
  const [priceField, setPriceField] = useState<PriceField>('close')
  const { mode } = useTheme()
  const isDark = mode === 'dark'

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (ticker && (!items || items.length === 0) && !loading) {
      fetchHistory({ ticker, dateRange })
    }
  }, [ticker, items, loading, fetchHistory, dateRange])

  const hasData = items && items.length > 0
  const sortedData = hasData ? [...items].sort((a, b) => a.date.localeCompare(b.date)) : []

  const baseOptions = getApexThemeOptions(isDark)

  // --- Candlestick series & options ---
  const candlestickSeries = [
    {
      name: ticker ?? 'Saham',
      data: sortedData.map((d) => ({
        x: d.date,
        y: [d.open, d.high, d.low, d.close] as [number, number, number, number],
      })),
    },
  ]

  const candlestickOptions: ApexOptions = {
    ...baseOptions,
    chart: {
      ...baseOptions.chart,
      type: 'candlestick',
    },
    tooltip: {
      ...baseOptions.tooltip,
      custom: ({ seriesIndex, dataPointIndex, w }) => {
        const o = w.globals.seriesCandleO[seriesIndex]?.[dataPointIndex]
        const h = w.globals.seriesCandleH[seriesIndex]?.[dataPointIndex]
        const l = w.globals.seriesCandleL[seriesIndex]?.[dataPointIndex]
        const c = w.globals.seriesCandleC[seriesIndex]?.[dataPointIndex]
        const date = sortedData[dataPointIndex]?.date ?? ''
        const fmt = (v: number) => v?.toLocaleString('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 })
        const isUp = c >= o
        const color = isUp ? '#10b981' : '#ef4444'
        return `<div style="padding:10px 14px;font-size:12px;line-height:1.7;">
          <div style="font-weight:600;margin-bottom:4px;">${date}</div>
          <div style="color:${color};font-weight:700;font-size:14px;">${fmt(c)}</div>
          <div>Open: <b>${fmt(o)}</b></div>
          <div>High: <b style="color:#10b981">${fmt(h)}</b></div>
          <div>Low: <b style="color:#ef4444">${fmt(l)}</b></div>
          <div>Close: <b>${fmt(c)}</b></div>
        </div>`
      },
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
  }

  // --- Line series & options ---
  const color = PRICE_FIELD_COLORS[priceField]
  const lineSeries = [
    {
      name: PRICE_FIELD_LABELS[priceField],
      data: sortedData.map((d) => ({
        x: d.date,
        y: d[priceField],
      })),
    },
  ]

  const lineOptions: ApexOptions = {
    ...baseOptions,
    chart: {
      ...baseOptions.chart,
      type: 'area',
    },
    colors: [color],
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

  const isCandlestick = chartType === 'candlestick'

  return (
    <Card variant="default">
      <Layout
        defaultHasDividers
        header={
          <LayoutHeader>
            <HistoryControls
              chartType={chartType}
              onChartTypeChange={setChartType}
              priceField={priceField}
              onPriceFieldChange={setPriceField}
            />
          </LayoutHeader>
        }
        content={
          <LayoutContent>
            {loading && !hasData && (
              <Center height={360}>
                <Spinner size="lg" label="Mengambil riwayat data pasar..." />
              </Center>
            )}
            {!hasData && !loading && (
              <Center height={360}>
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
                {mounted && isCandlestick && (
                  <Chart
                    key={`candlestick-${mode}`}
                    options={candlestickOptions}
                    series={candlestickSeries}
                    type="candlestick"
                    height={360}
                    width="100%"
                  />
                )}
                {mounted && !isCandlestick && (
                  <Chart
                    key={`line-${mode}-${priceField}`}
                    options={lineOptions}
                    series={lineSeries}
                    type="area"
                    height={360}
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
