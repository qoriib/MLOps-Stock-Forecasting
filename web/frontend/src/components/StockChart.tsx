import { useEffect, useRef } from 'react'
import * as echarts from 'echarts'
import type { ECharts, EChartsOption } from 'echarts'
import { Card, Center, EmptyState, Overlay, Spinner } from '@astryxdesign/core'
import { useStockStore, useShallow } from '@/stores'
import { getEChartsThemeOptions } from '@/configs'
import { formatCurrency } from '@/utils'

/**
 * Reads a CSS custom property from the Astryx theme element.
 * Since ECharts renders to SVG (DOM), CSS vars are accessible from the theme scope.
 */
function cssVar(name: string): string {
  const el = document.querySelector('[data-astryx-theme]') ?? document.documentElement
  return getComputedStyle(el).getPropertyValue(name).trim()
}

export function StockChart() {
  const containerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<ECharts | null>(null)

  const { ticker, model, historyData, forecastData, loading } = useStockStore(
    useShallow((state) => ({
      ticker: state.ticker,
      model: state.model,
      historyData: state.historyData,
      forecastData: state.forecastData,
      loading: state.loading,
    })),
  )

  const hasHistoricalData = historyData && historyData.length > 0
  const hasForecastData = forecastData && forecastData.length > 0
  const hasAnyData = hasHistoricalData || hasForecastData

  // Initialize ECharts with SVG renderer and handle resize
  useEffect(() => {
    const el = containerRef.current
    if (!el) return

    chartRef.current = echarts.init(el, undefined, { renderer: 'svg' })

    const onResize = () => chartRef.current?.resize()
    window.addEventListener('resize', onResize)
    const ro = new ResizeObserver(onResize)
    ro.observe(el)

    return () => {
      window.removeEventListener('resize', onResize)
      ro.disconnect()
      chartRef.current?.dispose()
      chartRef.current = null
    }
  }, [])

  // Render/update chart when data or theme changes
  useEffect(() => {
    const el = containerRef.current
    if (!el || !hasAnyData) return

    if (!chartRef.current) {
      chartRef.current = echarts.init(el, undefined, { renderer: 'svg' })
    }

    const instance = chartRef.current

    // Sort historical data chronologically
    const sortedHistory = hasHistoricalData
      ? [...historyData].sort((a, b) => a.date.localeCompare(b.date))
      : []

    const lastHistorical = sortedHistory.at(-1) ?? null
    const boundaryDate = lastHistorical?.date

    // Build unified date axis
    const allDates = Array.from(
      new Set([
        ...sortedHistory.map((d) => d.date),
        ...forecastData.map((d) => d.date),
      ]),
    ).sort()

    // Candlestick data: [Open, Close, Low, High]
    const histMap = new Map(sortedHistory.map((d) => [d.date, d]))
    const candlestickData = allDates.map((date) => {
      const h = histMap.get(date)
      return h ? [h.open, h.close, h.low, h.high] : [NaN, NaN, NaN, NaN]
    })

    const isFuture = forecastData.some((d) =>
      lastHistorical ? d.date > lastHistorical.date : false,
    )

    // Line series: connect to last historical close for future forecasts
    const forecastMap = new Map(forecastData.map((d) => [d.date, d.predicted_price]))
    const lineData = allDates.map((date) => {
      const predicted = forecastMap.get(date)
      if (predicted !== undefined) return predicted
      if (isFuture && date === boundaryDate && lastHistorical) return lastHistorical.close
      return null
    })

    // Read Astryx color tokens — works because SVG is in the DOM tree
    const colorGreen = cssVar('--color-text-green')
    const colorRed = cssVar('--color-text-red')
    const colorBlue = cssVar('--color-text-blue')
    const textPrimary = cssVar('--color-text-primary')
    const textSecondary = cssVar('--color-text-secondary')
    const fontMono = cssVar('--font-family-code')

    const option: EChartsOption = {
      ...getEChartsThemeOptions(),
      legend: {
        show: true,
        top: '2%',
        right: '4%',
        textStyle: { color: textPrimary, fontSize: 12 },
        data: [`${ticker} OHLC`, `Forecast (${model.toUpperCase()})`],
      },
      tooltip: {
        ...getEChartsThemeOptions().tooltip,
        formatter: (params) => {
          if (!Array.isArray(params) || params.length === 0) return ''
          const date = params[0]?.name ?? ''
          let html = `<div style="font-weight:600;margin-bottom:6px;color:${textPrimary}">${date}</div>`

          for (const p of params) {
            if (p.seriesType === 'candlestick' && Array.isArray(p.value)) {
              const [, open, close, low, high] = p.value as number[]
              if (!Number.isNaN(close)) {
                const color = close >= open ? colorGreen : colorRed
                html += `<div style="color:${color};font-weight:700;font-size:13px;margin-bottom:4px;font-family:${fontMono}">Close: ${formatCurrency(close)}</div>`
                html += `<div style="font-size:11px;line-height:1.6;color:${textSecondary};font-family:${fontMono}">`
                html += `Open: <b>${formatCurrency(open)}</b><br/>`
                html += `High: <b style="color:${colorGreen}">${formatCurrency(high)}</b> | Low: <b style="color:${colorRed}">${formatCurrency(low)}</b>`
                html += `</div>`
              }
            } else if (p.seriesType === 'line' && typeof p.value === 'number') {
              html += `<div style="color:${colorBlue};font-weight:700;font-size:13px;margin-top:6px;font-family:${fontMono}">`
              html += `Forecast ${model.toUpperCase()}: ${formatCurrency(p.value)}`
              html += `</div>`
            }
          }
          return html
        },
      },
      xAxis: {
        ...getEChartsThemeOptions().xAxis,
        data: allDates,
      },
      series: [
        {
          name: `${ticker} OHLC`,
          type: 'candlestick',
          data: candlestickData,
          itemStyle: {
            color: colorGreen,
            color0: colorRed,
            borderColor: colorGreen,
            borderColor0: colorRed,
          },
        },
        {
          name: `Forecast (${model.toUpperCase()})`,
          type: 'line',
          data: lineData,
          itemStyle: { color: colorBlue },
          lineStyle: { color: colorBlue, width: 2, type: 'dashed' },
          showSymbol: false,
          markLine: isFuture && boundaryDate
            ? {
              symbol: ['none', 'none'],
              data: [
                {
                  xAxis: boundaryDate,
                  label: {
                    show: true,
                    formatter: 'Forecast Start',
                    position: 'insideEndTop',
                    color: colorBlue,
                    fontSize: 11,
                    fontWeight: 'bold',
                  },
                  lineStyle: { color: colorBlue, type: 'dashed', width: 1.5 },
                },
              ],
            }
            : undefined,
        },
      ],
    }

    instance.setOption(option, true)
    requestAnimationFrame(() => instance.resize())
  }, [hasHistoricalData, hasForecastData, hasAnyData, historyData, forecastData, ticker, model])

  return (
    <Card variant="default" minHeight={480}>
      <Overlay
        isOpen={loading}
        position="fill"
        align="center"
        content={<Spinner label="Loading market data..." />}
      >
        {!hasAnyData && !loading ? (
          <Center height={440}>
            <EmptyState
              title="Chart Not Loaded"
              description="Configure the date ranges above, then click 'Run Analysis'."
              headingLevel={4}
            />
          </Center>
        ) : (
          <div
            ref={containerRef}
            style={{ width: '100%', height: '440px', minHeight: '440px' }}
          />
        )}
      </Overlay>
    </Card>
  )
}
