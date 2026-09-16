import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { logger } from 'hono/logger'
import { modelsRoute } from './routes/models.route'
import { stocksRoute } from './routes/stocks.route'
import { predictRoute } from './routes/predict.route'
import { APP_CONFIG } from './configs/app.config'
import type { HonoEnv } from './types'

const app = new Hono<HonoEnv>()

// Middleware: Inject Cloudflare D1 binding dari Nitro runtime context ke Hono context variable.
// Pola ini memisahkan lapisan platform (Nitro) dari lapisan aplikasi (Hono),
// sehingga preset Nitro bisa diganti tanpa menyentuh kode routes/services.
app.use('*', async (c, next) => {
  // Akses D1 via Nitro event runtime (sesuai best practice nitro.build)
  // Fallback ke c.env.DB untuk kompatibilitas wrangler dev langsung
  const nitroCloudflare = (c.req.raw as any)?.[Symbol.for('nitro:event')]?.req?.runtime?.cloudflare
  const db: D1Database | undefined = nitroCloudflare?.env?.DB ?? (c.env as any)?.DB
  if (db) {
    c.set('db', db)
  }
  await next()
})

// Middleware
app.use('*', logger())
app.use(
  '*',
  cors({
    origin: '*',
    allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowHeaders: ['Content-Type', 'Authorization'],
  }),
)

// Root & Health Check
app.get('/', (c) => {
  return c.json({
    status: 'healthy',
    project: APP_CONFIG.name,
    version: APP_CONFIG.version,
    runtime: APP_CONFIG.runtime,
    endpoints: {
      health: '/health',
      models: '/api/models',
      stocks: '/api/stocks/:ticker',
      predict: '/api/predict',
    },
  })
})

app.get('/health', (c) => {
  return c.json({ status: 'ok', timestamp: new Date().toISOString() })
})

// Sub-routes under /api
app.route('/api', modelsRoute)
app.route('/api', stocksRoute)
app.route('/api', predictRoute)

export default app
