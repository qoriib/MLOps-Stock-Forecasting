import { Card, HStack, Text, VStack } from '@astryxdesign/core'
import { useStockStore, useShallow } from '@/stores'
import { formatCurrency } from '@/utils'

export function UnifiedMetrics() {
  const { ticker, model, historyData, forecastData } = useStockStore(
    useShallow((state) => ({
      ticker: state.ticker,
      model: state.model,
      historyData: state.historyData,
      forecastData: state.forecastData,
    })),
  )

  if (!historyData.length && !forecastData.length) {
    return null
  }

  const lastHistory = historyData.length > 0 ? historyData[historyData.length - 1] : null
  const lastClose = lastHistory?.close ?? 0

  const firstForecast = forecastData.length > 0 ? forecastData[0] : null
  const lastForecast = forecastData.length > 0 ? forecastData[forecastData.length - 1] : null
  const targetPrice = lastForecast?.predicted_price ?? 0

  const priceDiff = lastClose && targetPrice ? targetPrice - lastClose : 0
  const pctChange = lastClose ? (priceDiff / lastClose) * 100 : 0
  const isPositive = priceDiff >= 0
  const trendColor = isPositive ? '#10b981' : '#ef4444'

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px',
      }}
    >
      {/* Kartu 1: Harga Riwayat Terakhir */}
      <Card variant="default">
        <div style={{ padding: '16px 20px' }}>
          <VStack gap={1}>
            <Text size="xsm" color="secondary" weight="medium">
              Harga Penutupan Terakhir ({lastHistory?.date || '-'})
            </Text>
            <Text size="xl" weight="bold">
              {formatCurrency(lastClose)}
            </Text>
            <Text size="xsm" color="secondary">
              Ticker: {ticker}
            </Text>
          </VStack>
        </div>
      </Card>

      {/* Kartu 2: Estimasi Target Prediksi */}
      <Card variant="default">
        <div style={{ padding: '16px 20px' }}>
          <VStack gap={1}>
            <Text size="xsm" color="secondary" weight="medium">
              Estimasi Harga Akhir ({lastForecast?.date || '-'})
            </Text>
            <div style={{ color: trendColor }}>
              <Text size="xl" weight="bold">
                {formatCurrency(targetPrice)}
              </Text>
            </div>
            <Text size="xsm" color="secondary">
              Model: {model.toUpperCase()}
            </Text>
          </VStack>
        </div>
      </Card>

      {/* Kartu 3: Estimasi Perubahan (Delta) */}
      <Card variant="default">
        <div style={{ padding: '16px 20px' }}>
          <VStack gap={1}>
            <Text size="xsm" color="secondary" weight="medium">
              Proyeksi Perubahan
            </Text>
            <HStack align="center" gap={2}>
              <div style={{ color: trendColor }}>
                <Text size="xl" weight="bold">
                  {isPositive ? '+' : ''}{pctChange.toFixed(2)}%
                </Text>
              </div>
              <div style={{ color: trendColor }}>
                <Text size="sm">
                  ({isPositive ? '+' : ''}{formatCurrency(priceDiff)})
                </Text>
              </div>
            </HStack>
            <Text size="xsm" color="secondary">
              Dari harga riwayat penutupan
            </Text>
          </VStack>
        </div>
      </Card>

      {/* Kartu 4: Horizon Hari Bursa */}
      <Card variant="default">
        <div style={{ padding: '16px 20px' }}>
          <VStack gap={1}>
            <Text size="xsm" color="secondary" weight="medium">
              Horizon Hari Bursa
            </Text>
            <Text size="xl" weight="bold">
              {forecastData.length} Hari Kerja
            </Text>
            <Text size="xsm" color="secondary">
              {firstForecast?.date} s/d {lastForecast?.date}
            </Text>
          </VStack>
        </div>
      </Card>
    </div>
  )
}
