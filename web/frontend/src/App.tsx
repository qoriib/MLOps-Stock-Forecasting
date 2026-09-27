import { useEffect } from 'react'
import { Theme } from '@astryxdesign/core/theme'
import { neutralTheme } from '@astryxdesign/theme-neutral/built'
import { Layout, LayoutHeader, LayoutContent, LayoutFooter } from '@astryxdesign/core/Layout'
import { Banner, VStack } from '@astryxdesign/core'
import { useStockStore, useShallow } from '@/stores'
import { AppHeader } from '@/components/AppHeader'
import { AppFooter } from '@/components/AppFooter'
import { UnifiedControls } from '@/components/UnifiedControls'
import { UnifiedMetrics } from '@/components/UnifiedMetrics'
import { UnifiedStockChart } from '@/components/UnifiedStockChart'

export function App() {
  const { themeMode, error, initApp, setThemeMode } = useStockStore(
    useShallow((state) => ({
      themeMode: state.themeMode,
      error: state.error,
      initApp: state.initApp,
      setThemeMode: state.setThemeMode,
    })),
  )

  useEffect(() => {
    // Muat preferensi tema
    const saved = localStorage.getItem('theme-mode') as 'light' | 'dark' | null
    if (saved === 'light' || saved === 'dark') {
      setThemeMode(saved)
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setThemeMode('dark')
    }

    // Inisialisasi data dari backend
    initApp()
  }, [initApp, setThemeMode])

  return (
    <Theme theme={neutralTheme} mode={themeMode}>
      <Layout
        contentWidth={1120}
        defaultHasDividers
        header={
          <LayoutHeader>
            <AppHeader />
          </LayoutHeader>
        }
        content={
          <LayoutContent>
            <VStack gap={5}>
              {error && (
                <Banner
                  status="error"
                  title="Kendala Koneksi atau Data"
                  description={error}
                />
              )}

              {/* Kontrol Input Parameter: Ticker, Model, History Range, Forecast Range */}
              <UnifiedControls />

              {/* Metrik Ringkasan Nilai & Performa */}
              <UnifiedMetrics />

              {/* Single Unified Chart: Candlestick (History) + Line (Forecast) */}
              <UnifiedStockChart />
            </VStack>
          </LayoutContent>
        }
        footer={
          <LayoutFooter>
            <AppFooter />
          </LayoutFooter>
        }
      />
    </Theme>
  )
}

export default App
