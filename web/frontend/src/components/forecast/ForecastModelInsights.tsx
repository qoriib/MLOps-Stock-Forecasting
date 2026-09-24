import { Badge, Card, Heading, HStack, Text, VStack } from '@astryxdesign/core'
import { Layout, LayoutHeader, LayoutContent } from '@astryxdesign/core/Layout'
import { useStockStore } from '@/stores'
import { formatCurrency } from '@/utils'

export function ForecastModelInsights() {
  const ticker = useStockStore((state) => state.ticker)
  const modelType = useStockStore((state) => state.modelType)
  const predictResult = useStockStore((state) => state.predictResult)
  const modelMetricsMap = useStockStore((state) => state.modelMetrics)

  const currentTickerMetrics = ticker ? modelMetricsMap[ticker] : undefined
  const modelTypeUpper = (modelType || 'lstm').toUpperCase()

  const bestConfig =
    predictResult?.best_config ||
    currentTickerMetrics?.best_configs?.[modelTypeUpper]

  const metrics =
    predictResult?.metrics ||
    currentTickerMetrics?.metrics?.[modelTypeUpper]

  const isBestModel =
    currentTickerMetrics?.best_model?.toUpperCase() === modelTypeUpper

  const windowSize =
    predictResult?.window_size ||
    bestConfig?.time_steps ||
    metrics?.time_steps ||
    30

  if (!predictResult && !metrics && !bestConfig) {
    return null
  }

  return (
    <Card variant="default">
      <Layout
        header={
          <LayoutHeader>
            <HStack justify="space-between" align="center" wrap="wrap" gap={3}>
              <HStack gap={2} align="center">
                <Heading level={5}>Wawasan Model & Hyperparameter Optimal</Heading>
                <Badge
                  label={modelTypeUpper}
                  variant="neutral"
                  size="small"
                />
                {isBestModel && (
                  <Badge
                    label="Pilihan Terbaik (RMSE Terendah)"
                    variant="success"
                    size="small"
                  />
                )}
              </HStack>
              <Text color="secondary" type="caption">
                Hasil Eksperimen Grid Search MLOps Pipeline
              </Text>
            </HStack>
          </LayoutHeader>
        }
        content={
          <LayoutContent padding={4}>
            <HStack gap={4} wrap="wrap" justify="space-between">
              {/* Parameter 1: Time Steps / Window Size */}
              <VStack gap={1} style={{ minWidth: 120 }}>
                <Text color="secondary" type="caption">
                  Sequence Window
                </Text>
                <Text weight="bold" type="code">
                  {windowSize} Hari
                </Text>
              </VStack>

              {/* Parameter 2: Optimizer */}
              <VStack gap={1} style={{ minWidth: 120 }}>
                <Text color="secondary" type="caption">
                  Optimizer
                </Text>
                <Text weight="bold" type="code">
                  {bestConfig?.optimizer || metrics?.optimizer || 'Adam'}
                </Text>
              </VStack>

              {/* Parameter 3: Batch Size */}
              <VStack gap={1} style={{ minWidth: 120 }}>
                <Text color="secondary" type="caption">
                  Batch Size
                </Text>
                <Text weight="bold" type="code">
                  {bestConfig?.batch_size || metrics?.batch_size || 32}
                </Text>
              </VStack>

              {/* Parameter 4: Learning Rate */}
              <VStack gap={1} style={{ minWidth: 120 }}>
                <Text color="secondary" type="caption">
                  Learning Rate
                </Text>
                <Text weight="bold" type="code">
                  {bestConfig?.learning_rate ?? metrics?.learning_rate ?? 0.001}
                </Text>
              </VStack>

              {/* Metrik: RMSE */}
              <VStack gap={1} style={{ minWidth: 120 }}>
                <Text color="secondary" type="caption">
                  Test RMSE
                </Text>
                <Text weight="bold" type="code">
                  {metrics?.RMSE != null
                    ? formatCurrency(metrics.RMSE, { minimumFractionDigits: 2 })
                    : bestConfig?.RMSE != null
                      ? formatCurrency(bestConfig.RMSE, { minimumFractionDigits: 2 })
                      : '-'}
                </Text>
              </VStack>

              {/* Metrik: MAPE */}
              <VStack gap={1} style={{ minWidth: 120 }}>
                <Text color="secondary" type="caption">
                  Test MAPE
                </Text>
                <Text weight="bold" type="code">
                  {metrics?.MAPE != null
                    ? `${metrics.MAPE.toFixed(2)}%`
                    : bestConfig?.MAPE != null
                      ? `${bestConfig.MAPE.toFixed(2)}%`
                      : '-'}
                </Text>
              </VStack>

              {/* Metrik: R2 */}
              <VStack gap={1} style={{ minWidth: 120 }}>
                <Text color="secondary" type="caption">
                  Test R² Score
                </Text>
                <Text weight="bold" type="code">
                  {metrics?.R2 != null
                    ? metrics.R2.toFixed(3)
                    : bestConfig?.R2 != null
                      ? bestConfig.R2.toFixed(3)
                      : '-'}
                </Text>
              </VStack>
            </HStack>
          </LayoutContent>
        }
      />
    </Card>
  )
}
