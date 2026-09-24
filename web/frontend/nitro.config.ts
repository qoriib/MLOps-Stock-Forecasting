import { defineConfig } from 'nitro'

export default defineConfig({
  preset: 'static',
  prerender: {
    crawlLinks: true,
    routes: ['/'],
  },
})
