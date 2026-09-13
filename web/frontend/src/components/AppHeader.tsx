import { TopNav, TopNavHeading, TopNavItem } from '@astryxdesign/core/TopNav'
import { Selector } from '@astryxdesign/core/Selector'
import { HStack } from '@astryxdesign/core/Stack'
import { useRouterState } from '@tanstack/react-router'
import { useStock } from '@/context/StockContext'

export function AppHeader() {
  const { ticker, setTicker, availableTickers, loadingTickers } = useStock()
  const routerState = useRouterState()
  const currentPath = routerState.location.pathname

  const tickerOptions = availableTickers.map((t) => ({
    value: t,
    label: t,
  }))

  return (
    <TopNav
      label="Navigasi Utama Aplikasi"
      heading={
        <TopNavHeading
          heading="Stock Forecasting"
        />
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
            label="Pilih Saham"
            isLabelHidden
            placeholder={loadingTickers ? 'Memuat...' : 'Pilih Ticker'}
            options={tickerOptions}
            value={ticker || undefined}
            onChange={(val) => setTicker(val)}
            width={120}
            size="sm"
            isDisabled={loadingTickers || availableTickers.length === 0}
          />
        </HStack>
      }
    />
  )
}
