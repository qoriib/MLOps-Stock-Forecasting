import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts'
import { Card } from '@astryxdesign/core/Card'
import { VStack, HStack } from '@astryxdesign/core/Stack'
import { Text } from '@astryxdesign/core/Text'
import { Token } from '@astryxdesign/core/Token'
import { useTheme } from '@astryxdesign/core/theme'
import type { StockDataPoint } from '@/types/stock'

interface HistoryChartProps {
  items: StockDataPoint[]
  ticker: string
}

interface CustomTooltipProps {
  active?: boolean
  payload?: Array<{
    payload: StockDataPoint
    value: number
  }>
  label?: string
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
  if (active && payload && payload.length) {
    const data = payload[0].payload
    return (
      <div
        style={{
          backgroundColor: 'var(--color-surface, #ffffff)',
          border: '1px solid var(--color-border, #e5e7eb)',
          borderRadius: '8px',
          padding: '10px 14px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
          fontSize: '12px',
          minWidth: '160px',
        }}
      >
        <div style={{ fontWeight: 600, marginBottom: '6px', color: 'var(--color-text-primary, #111827)' }}>
          {data.date}
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }}>
          <span style={{ color: 'var(--color-text-secondary, #6b7280)' }}>Penutupan:</span>
          <span style={{ fontWeight: 600, color: 'var(--color-accent, #3b82f6)' }}>
            Rp {Number(data.close).toLocaleString('id-ID')}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }}>
          <span style={{ color: 'var(--color-text-secondary, #6b7280)' }}>Pembukaan:</span>
          <span>Rp {Number(data.open).toLocaleString('id-ID')}</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }}>
          <span style={{ color: 'var(--color-text-secondary, #6b7280)' }}>Tertinggi:</span>
          <span style={{ color: '#16a34a' }}>Rp {Number(data.high).toLocaleString('id-ID')}</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }}>
          <span style={{ color: 'var(--color-text-secondary, #6b7280)' }}>Terendah:</span>
          <span style={{ color: '#dc2626' }}>Rp {Number(data.low).toLocaleString('id-ID')}</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px', borderTop: '1px dashed var(--color-border, #e5e7eb)', paddingTop: '4px' }}>
          <span style={{ color: 'var(--color-text-secondary, #6b7280)' }}>Volume:</span>
          <span style={{ fontWeight: 500 }}>{Number(data.volume).toLocaleString('id-ID')}</span>
        </div>
      </div>
    )
  }
  return null
}

export function HistoryChart({ items, ticker }: HistoryChartProps) {
  const { token } = useTheme()
  const accent = token('--color-accent') || '#3b82f6'
  const textMuted = token('--color-text-secondary') || '#6b7280'
  const gridColor = token('--color-border') || 'rgba(0, 0, 0, 0.08)'

  if (!items || items.length === 0) return null

  const sortedData = [...items].sort((a, b) => a.date.localeCompare(b.date))
  const prices = sortedData.map((d) => d.close)
  const minPrice = Math.min(...prices)
  const maxPrice = Math.max(...prices)
  const pricePadding = (maxPrice - minPrice) * 0.05

  return (
    <Card variant="default" elevation="low" padding={4}>
      <VStack gap={4}>
        <HStack justify="between" align="center">
          <VStack gap={1}>
            <Text weight="semibold" size="base">
              Grafik Tren Harga Historis
            </Text>
            <Text color="secondary" size="xsm">
              Pergerakan harga penutupan harian pasar saham
            </Text>
          </VStack>

          <HStack gap={2} align="center">
            <Token label={ticker} size="sm" />
            <Text color="secondary" size="xsm">
              {sortedData.length} data ditampilkan
            </Text>
          </HStack>
        </HStack>

        <div style={{ width: '100%', height: 320 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={sortedData}
              margin={{ top: 10, right: 10, left: 10, bottom: 0 }}
            >
              <defs>
                <linearGradient id="historyGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={accent} stopOpacity={0.28} />
                  <stop offset="95%" stopColor={accent} stopOpacity={0.01} />
                </linearGradient>
              </defs>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke={gridColor}
                vertical={false}
              />
              <XAxis
                dataKey="date"
                stroke={textMuted}
                fontSize={11}
                tickLine={false}
                axisLine={{ stroke: gridColor }}
                tickFormatter={(val: string) => {
                  if (!val) return ''
                  const parts = val.split('-')
                  return parts.length === 3 ? `${parts[2]}/${parts[1]}` : val
                }}
              />
              <YAxis
                stroke={textMuted}
                fontSize={11}
                tickLine={false}
                axisLine={false}
                domain={[
                  Math.floor(minPrice - pricePadding),
                  Math.ceil(maxPrice + pricePadding),
                ]}
                tickFormatter={(val: number) => `Rp ${val.toLocaleString('id-ID')}`}
                width={75}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="close"
                stroke={accent}
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#historyGradient)"
                activeDot={{
                  r: 5,
                  stroke: accent,
                  strokeWidth: 2,
                  fill: 'var(--color-surface, #ffffff)',
                }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </VStack>
    </Card>
  )
}
