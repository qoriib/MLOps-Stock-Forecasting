import { Card } from '@astryxdesign/core/Card'
import { VStack, HStack } from '@astryxdesign/core/Stack'
import { Text } from '@astryxdesign/core/Text'
import { Badge } from '@astryxdesign/core/Badge'
import { useTheme } from '@astryxdesign/core/theme'
import type { PredictionItem, HistoricalItem } from '@/types/stock'

interface ForecastChartProps {
  predictions: PredictionItem[]
  history?: HistoricalItem[]
  ticker: string
  modelType?: string
  modelName?: string
}

export function ForecastChart({
  predictions,
  history = [],
  ticker,
  modelType,
  modelName,
}: ForecastChartProps) {
  const { token } = useTheme()
  const accent = token('--color-accent') || '#3b82f6'
  const textMuted = token('--color-text-secondary') || '#6b7280'
  const gridColor = token('--color-border') || 'rgba(0,0,0,0.08)'

  if (!predictions || predictions.length === 0) return null

  const histSorted = [...history].sort((a, b) => a.date.localeCompare(b.date))
  const allPrices = [
    ...histSorted.map((d) => d.close),
    ...predictions.flatMap((d) => [d.predicted_price, d.lower_bound ?? d.predicted_price, d.upper_bound ?? d.predicted_price]),
  ]
  const minVal = Math.min(...allPrices)
  const maxVal = Math.max(...allPrices)
  const range = maxVal - minVal || 1

  const width = 800
  const height = 220
  const padTop = 20
  const padBottom = 30
  const padLeft = 65
  const padRight = 20

  const plotW = width - padLeft - padRight
  const plotH = height - padTop - padBottom
  const totalCount = histSorted.length + predictions.length

  const getX = (index: number) => padLeft + (index / (totalCount - 1 || 1)) * plotW
  const getY = (val: number) => padTop + plotH - ((val - minVal) / range) * plotH

  const histPoints = histSorted.map((d, i) => `${getX(i)},${getY(d.close)}`)
  const histPath = histPoints.length ? `M ${histPoints.join(' L ')}` : ''

  const bridgeIndex = histSorted.length > 0 ? histSorted.length - 1 : 0
  const bridgePoint = histSorted.length > 0 ? `${getX(bridgeIndex)},${getY(histSorted[bridgeIndex].close)}` : null
  const predPoints = predictions.map((d, i) => `${getX(histSorted.length + i)},${getY(d.predicted_price)}`)
  const forecastPath = `M ${[...(bridgePoint ? [bridgePoint] : []), ...predPoints].join(' L ')}`

  const bandUpper = predictions.map((d, i) => `${getX(histSorted.length + i)},${getY(d.upper_bound ?? d.predicted_price)}`)
  const bandLower = predictions.map((d, i) => `${getX(histSorted.length + i)},${getY(d.lower_bound ?? d.predicted_price)}`).reverse()
  const bandPath = `M ${bandUpper.join(' L ')} L ${bandLower.join(' L ')} Z`

  const splitX = histSorted.length > 0 ? getX(histSorted.length - 1) : null

  return (
    <Card variant="default" elevation="low" padding={3}>
      <VStack gap={2}>
        <HStack justify="between" align="center">
          <HStack gap={2} align="center">
            <Text weight="semibold">Visualisasi Historis & Proyeksi Peramalan ({ticker})</Text>
            {modelType && (
              <Badge
                label={`Model: ${modelType.toUpperCase()}${modelName ? ` (${modelName})` : ''}`}
                variant="neutral"
              />
            )}
          </HStack>
          <HStack gap={3}>
            <Text size="xsm" color="secondary">● Historis ({histSorted.length} hari)</Text>
            <Text size="xsm" style={{ color: accent }}>● Prediksi ({predictions.length} hari)</Text>
            <Text size="xsm" color="secondary">■ CI 95%</Text>
          </HStack>
        </HStack>


        <svg viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', height: 'auto', display: 'block' }}>
          <line x1={padLeft} y1={padTop} x2={width - padRight} y2={padTop} stroke={gridColor} strokeDasharray="3 3" />
          <line x1={padLeft} y1={padTop + plotH / 2} x2={width - padRight} y2={padTop + plotH / 2} stroke={gridColor} strokeDasharray="3 3" />
          <line x1={padLeft} y1={height - padBottom} x2={width - padRight} y2={height - padBottom} stroke={gridColor} />

          {splitX && <line x1={splitX} y1={padTop} x2={splitX} y2={height - padBottom} stroke={gridColor} strokeDasharray="4 4" />}

          <text x={padLeft - 8} y={padTop + 4} fill={textMuted} fontSize="11" textAnchor="end">Rp {Math.round(maxVal).toLocaleString('id-ID')}</text>
          <text x={padLeft - 8} y={height - padBottom} fill={textMuted} fontSize="11" textAnchor="end">Rp {Math.round(minVal).toLocaleString('id-ID')}</text>

          <path d={bandPath} fill={accent} fillOpacity="0.15" />
          {histPath && <path d={histPath} fill="none" stroke={textMuted} strokeWidth="1.8" />}
          <path d={forecastPath} fill="none" stroke={accent} strokeWidth="2.5" strokeLinecap="round" />

          <text x={padLeft} y={height - 10} fill={textMuted} fontSize="11">{histSorted[0]?.date || predictions[0].date}</text>
          {splitX && <text x={splitX} y={height - 10} fill={textMuted} fontSize="11" textAnchor="middle">Kini</text>}
          <text x={width - padRight} y={height - 10} fill={textMuted} fontSize="11" textAnchor="end">{predictions[predictions.length - 1].date}</text>
        </svg>
      </VStack>
    </Card>
  )
}
