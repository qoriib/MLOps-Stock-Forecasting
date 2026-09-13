import { HStack } from '@astryxdesign/core/Stack'
import { Text } from '@astryxdesign/core/Text'
import { StatusDot } from '@astryxdesign/core/StatusDot'
import { Button } from '@astryxdesign/core/Button'
import { useStock } from '@/context/StockContext'

export function AppFooter() {
  const { backendHealthy, checkHealth } = useStock()

  return (
    <HStack justify="between" align="center">
      <Text color="secondary" size="sm">
        MLOps Stock Forecasting
      </Text>

      <HStack gap={2} align="center">
        <StatusDot
          variant={backendHealthy ? 'success' : backendHealthy === false ? 'error' : 'neutral'}
          label={backendHealthy ? 'Backend Aktif' : 'Backend Offline'}
          isPulsing={backendHealthy === true}
        />
        <Text color={backendHealthy ? 'primary' : 'secondary'} size="sm" weight="medium">
          {backendHealthy ? 'API Online' : 'API Offline'}
        </Text>
        <Button
          label="Cek Status"
          variant="ghost"
          size="sm"
          onClick={checkHealth}
        />
      </HStack>
    </HStack>
  )
}
