import { defineConfig } from 'nitro'

export default defineConfig({
  preset: 'cloudflare_module',
  serverEntry: './src/index.ts',
  cloudflare: {
    deployConfig: true,
    nodeCompat: true,
  },
})
