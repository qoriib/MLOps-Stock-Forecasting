import { defineConfig } from 'nitro'

export default defineConfig({
  preset: 'cloudflare_module',
  compatibilityDate: '2024-09-19',
  serverEntry: './src/index.ts',
  cloudflare: {
    deployConfig: true,
    nodeCompat: true,
    wrangler: {
      name: 'stock-forecast-api',
      d1_databases: [
        {
          binding: 'DB',
          database_name: 'stock-forecast-db',
          database_id: 'e272aa1e-554b-4b39-a1d5-a4c03392e017',
          migrations_dir: 'migrations',
        },
      ],
    },
  },
})
