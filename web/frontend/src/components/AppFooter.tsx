import { Button, HStack, StatusDot, Text } from '@astryxdesign/core'
import { useStockStore } from '@/stores'
import { APP_CONFIG } from '@/configs'

export function AppFooter() {
  const backendHealthy = useStockStore((state) => state.backendHealthy)
  const checkHealth = useStockStore((state) => state.checkHealth)
  const themeMode = useStockStore((state) => state.themeMode)
  const toggleThemeMode = useStockStore((state) => state.toggleThemeMode)

  const statusLabel =
    backendHealthy === true
      ? 'Online'
      : backendHealthy === false
        ? 'Offline'
        : 'Cek Status'

  return (
    <HStack justify="between" align="center">
      <Text color="secondary">
        {APP_CONFIG.title}
      </Text>
      <HStack gap={2} align="center">
        <Button
          variant="ghost"
          label={themeMode === 'light' ? 'Mode Gelap' : 'Mode Terang'}
          onClick={toggleThemeMode}
        />
        <Button
          variant="ghost"
          icon={
            <StatusDot
              label={statusLabel}
              variant={backendHealthy ? 'success' : backendHealthy === false ? 'error' : 'neutral'}
              isPulsing={backendHealthy === true}
            />
          }
          label={statusLabel}
          onClick={checkHealth}
        />
      </HStack>
    </HStack>
  )
}
