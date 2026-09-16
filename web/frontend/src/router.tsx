import { createRouter as createTanStackRouter, Link } from '@tanstack/react-router'
import { Button, Center, EmptyState } from '@astryxdesign/core'
import { routeTree } from '@/routeTree.gen'

export function getRouter() {
  const router = createTanStackRouter({
    routeTree,
    scrollRestoration: true,
    defaultPreload: 'intent',
    defaultPreloadStaleTime: 0,
    defaultNotFoundComponent: () => (
      <Center height={400}>
        <EmptyState
          title="Halaman Tidak Ditemukan"
          description="Halaman yang Anda tuju tidak tersedia atau telah dipindahkan."
          headingLevel={3}
          actions={
            <Link to="/">
              <Button label="Kembali ke Beranda" variant="primary" />
            </Link>
          }
        />
      </Center>
    ),
  })

  return router
}

declare module '@tanstack/react-router' {
  interface Register {
    router: ReturnType<typeof getRouter>
  }
}
