import { useEffect } from 'react'
import { HeadContent, Link, Scripts, createRootRoute } from '@tanstack/react-router'
import { Theme } from '@astryxdesign/core/theme'
import { neutralTheme } from '@astryxdesign/theme-neutral/built'
import { LinkProvider } from '@astryxdesign/core/Link'
import { Layout, LayoutHeader, LayoutContent, LayoutFooter } from '@astryxdesign/core/Layout'
import { useStockStore } from '@/stores'
import { AppHeader } from '@/components/AppHeader'
import { AppFooter } from '@/components/AppFooter'
import appCss from '@/styles.css?url'

export const Route = createRootRoute({
  head: () => ({
    meta: [
      {
        charSet: 'utf-8',
      },
      {
        name: 'viewport',
        content: 'width=device-width, initial-scale=1',
      },
      {
        title: 'Stock Inference System - IDX MLOps',
      },
    ],
    links: [
      {
        rel: 'stylesheet',
        href: appCss,
      },
    ],
  }),
  shellComponent: RootDocument,
})

function RootDocument({ children }: { children: React.ReactNode }) {
  const checkHealth = useStockStore((state) => state.checkHealth)
  const themeMode = useStockStore((state) => state.themeMode)
  const setThemeMode = useStockStore((state) => state.setThemeMode)

  useEffect(() => {
    checkHealth()
    const saved = localStorage.getItem('theme-mode') as 'light' | 'dark' | null
    if (saved === 'light' || saved === 'dark') {
      setThemeMode(saved)
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setThemeMode('dark')
    }
  }, [checkHealth, setThemeMode])

  return (
    <html lang="en">
      <head>
        <HeadContent />
      </head>
      <body>
        <Theme theme={neutralTheme} mode={themeMode}>
          <LinkProvider component={Link}>
            <Layout
              contentWidth={1040}
              defaultHasDividers
              header={
                <LayoutHeader>
                  <AppHeader />
                </LayoutHeader>
              }
              content={<LayoutContent>{children}</LayoutContent>}
              footer={
                <LayoutFooter>
                  <AppFooter />
                </LayoutFooter>
              }
            />
          </LinkProvider>
        </Theme>
        <Scripts />
      </body>
    </html>
  )
}
