import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { logger } from 'hono/logger'
import { modelsRoute } from './routes/models.route'
import { stocksRoute } from './routes/stocks.route'
import { predictRoute } from './routes/predict.route'
import { APP_CONFIG } from './configs/app.config'
import type { HonoEnv } from './types'

const app = new Hono<HonoEnv>()


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
