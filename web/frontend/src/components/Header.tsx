import { StatusDot, TopNav, TopNavHeading, Button } from '@astryxdesign/core'
import { useStockStore, useShallow } from '@/stores'
import { APP_CONFIG } from '@/configs'

export function Header() {
  const { backendHealthy, initApp } = useStockStore(
    useShallow((state) => ({
      backendHealthy: state.backendHealthy,
      initApp: state.initApp,
    })),
  )

  const statusLabel =
    backendHealthy === true
      ? 'Connected'
      : backendHealthy === false
        ? 'Disconnected'
        : 'Connecting...'

  return (
    <TopNav
      label="Main Application Navigation"
      heading={
        <TopNavHeading heading={APP_CONFIG.name} />
      }
      endContent={
        <Button
          variant="ghost"
          label={statusLabel}
          onClick={() => initApp()}
          icon={
            <StatusDot
              label={statusLabel}
              variant={backendHealthy ? 'success' : backendHealthy === false ? 'error' : 'neutral'}
              isPulsing={backendHealthy === true}
            />
          }
        />
      }
    />
  )
}
