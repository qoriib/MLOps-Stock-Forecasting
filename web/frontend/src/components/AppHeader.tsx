import { Badge, HStack, StatusDot, TopNav, TopNavHeading, Button } from '@astryxdesign/core'
import { useStockStore, useShallow } from '@/stores'
import { APP_CONFIG } from '@/configs'

export function AppHeader() {
  const { backendHealthy, themeMode, toggleThemeMode, initApp } = useStockStore(
    useShallow((state) => ({
      backendHealthy: state.backendHealthy,
      themeMode: state.themeMode,
      toggleThemeMode: state.toggleThemeMode,
      initApp: state.initApp,
    })),
  )

  const statusLabel =
    backendHealthy === true
      ? 'Backend API Terhubung'
      : backendHealthy === false
        ? 'Backend Terputus'
        : 'Menghubungkan...'

  return (
    <TopNav
      label="Navigasi Utama Aplikasi"
      heading={
        <HStack gap={2} align="center">
          <TopNavHeading heading={APP_CONFIG.name} />
          <Badge variant="neutral" label="v2.0 MLOps" />
        </HStack>
      }
      endContent={
        <HStack gap={3} align="center">
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
            onClick={() => initApp()}
          />
          <Button
            variant="secondary"
            label={themeMode === 'light' ? 'Mode Gelap' : 'Mode Terang'}
            onClick={toggleThemeMode}
          />
        </HStack>
      }
    />
  )
}
