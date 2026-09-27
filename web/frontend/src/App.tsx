import { useEffect } from 'react'
import { Theme } from '@astryxdesign/core/theme'
import { neutralTheme } from '@astryxdesign/theme-neutral/built'
import { Layout, LayoutHeader, LayoutContent, LayoutFooter } from '@astryxdesign/core/Layout'
import { Banner, VStack } from '@astryxdesign/core'
import { useStockStore, useShallow } from '@/stores'
import { Header } from '@/components/Header'
import { Footer } from '@/components/Footer'
import { Controls } from '@/components/Controls'
import { StockChart } from '@/components/StockChart'
import { ForecastTable } from '@/components/ForecastTable'

export function App() {
  const { themeMode, error, initApp } = useStockStore(
    useShallow((state) => ({
      themeMode: state.themeMode,
      error: state.error,
      initApp: state.initApp,
    })),
  )

  useEffect(() => {
    initApp()
  }, [initApp])

  return (
    <Theme theme={neutralTheme} mode={themeMode}>
      <Layout
        contentWidth={1120}
        defaultHasDividers
        header={
          <LayoutHeader>
            <Header />
          </LayoutHeader>
        }
        content={
          <LayoutContent>
            <VStack gap={5}>
              {error && (
                <Banner
                  status="error"
                  title="Connection or Data Error"
                  description={error}
                />
              )}
              <Controls />
              <StockChart />
              <ForecastTable />
            </VStack>
          </LayoutContent>
        }
        footer={
          <LayoutFooter>
            <Footer />
          </LayoutFooter>
        }
      />
    </Theme>
  )
}

export default App
