import { useMemo } from 'react'
import { HStack, Selector, TopNav, TopNavHeading, TopNavItem } from '@astryxdesign/core'
import { useRouterState } from '@tanstack/react-router'
import { useHeaderState } from '@/stores'
import { APP_CONFIG } from '@/configs'

export function AppHeader() {
  const { ticker, setTicker, availableTickers, loadingTickers } = useHeaderState()
  const routerState = useRouterState()
  const currentPath = routerState.location.pathname

  const tickerOptions = useMemo(
    () => availableTickers.map((t) => ({ value: t, label: t })),
    [availableTickers],
  )

  return (
    <TopNav
      label="Navigasi Utama Aplikasi"
      heading={
        <TopNavHeading heading={APP_CONFIG.name} />
      }
      startContent={
        <HStack gap={1}>
          <TopNavItem
            label="Prediksi"
            href="/"
            isSelected={currentPath === '/'}
          />
          <TopNavItem
            label="Histori"
            href="/history"
            isSelected={currentPath === '/history'}
          />
        </HStack>
      }
      endContent={
        <HStack gap={1}>
          <Selector
            isLabelHidden
            width={140}
            label="Pilih Saham"
            placeholder={loadingTickers ? 'Memuat...' : 'Pilih Ticker'}
            options={tickerOptions}
            value={ticker || undefined}
            onChange={setTicker}
            isDisabled={loadingTickers || availableTickers.length === 0}
          />
        </HStack>
      }
    />
  )
}
