import { defineConfig } from 'nitro'

export default defineConfig({
  preset: 'cloudflare_module',
  compatibilityDate: '2024-09-19',
  serverEntry: './src/index.ts',
  serverAssets: [
    {
      baseName: 'assets',
      dir: './assets',
    },
  ],
  cloudflare: {
    deployConfig: true,
    nodeCompat: true,
    wrangler: {
      name: 'stock-forecast-api',
    },
  },
})
