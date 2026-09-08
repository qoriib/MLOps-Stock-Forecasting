import { Hono } from 'hono'
import { cors } from 'hono/cors'

type Bindings = {
  DB: D1Database
}

const app = new Hono<{ Bindings: Bindings }>()

app.use('/*', cors())

app.get('/', (c) => {
  return c.json({
    status: 'online',
    service: 'MLOps Stock Forecasting Edge API (Hono + Cloudflare D1)',
    endpoints: [
      'GET /api/stocks',
      'GET /api/stocks/:symbol',
      'GET /api/stocks/:symbol/latest',
      'GET /api/stocks/:symbol/summary',
      'GET /api/stocks/:symbol/forecast',
    ],
  })
})

// GET /api/stocks - Daftar seluruh simbol saham yang tersimpan di D1
app.get('/api/stocks', async (c) => {
  try {
    const query = `
      SELECT 
        symbol,
        COUNT(*) AS total_records,
        MIN(date) AS start_date,
        MAX(date) AS end_date
      FROM stock_prices
      GROUP BY symbol
      ORDER BY symbol ASC;
    `
    const { results } = await c.env.DB.prepare(query).all()
    return c.json({ stocks: results })
  } catch (err: any) {
    return c.json({ error: true, message: err?.message || 'Database query error' }, 500)
  }
})

// GET /api/stocks/:symbol/latest - Baris data harga terbaru
app.get('/api/stocks/:symbol/latest', async (c) => {
  try {
    const symbol = c.req.param('symbol').toUpperCase()
    const row = await c.env.DB.prepare(
      'SELECT * FROM stock_prices WHERE symbol = ? ORDER BY date DESC LIMIT 1'
    ).bind(symbol).first()

    if (!row) {
      return c.json({ error: true, message: `Data untuk '${symbol}' tidak ditemukan.` }, 404)
    }
    return c.json({ symbol, data: row })
  } catch (err: any) {
    return c.json({ error: true, message: err?.message || 'Database query error' }, 500)
  }
})

// GET /api/stocks/:symbol/summary - Statistik ringkasan harga
app.get('/api/stocks/:symbol/summary', async (c) => {
  try {
    const symbol = c.req.param('symbol').toUpperCase()

    const recentResult = await c.env.DB.prepare(
      'SELECT date, close FROM stock_prices WHERE symbol = ? ORDER BY date DESC LIMIT 2'
    ).bind(symbol).all()
    const recentRows = recentResult.results || []

    const stats = await c.env.DB.prepare(`
      SELECT 
        MIN(low) AS min_price,
        MAX(high) AS max_price,
        AVG(volume) AS avg_volume,
        COUNT(*) AS total_records
      FROM stock_prices 
      WHERE symbol = ?;
    `).bind(symbol).first()

    if (recentRows.length === 0) {
      return c.json({ error: true, message: `Data statistik untuk '${symbol}' tidak ditemukan.` }, 404)
    }

    const latestPrice = Number(recentRows[0].close)
    const latestDate = String(recentRows[0].date)
    let prevClose: number | null = null
    let priceChange: number | null = null
    let priceChangePercent: number | null = null

    if (recentRows.length >= 2) {
      prevClose = Number(recentRows[1].close)
      priceChange = Math.round((latestPrice - prevClose) * 100) / 100
      priceChangePercent = Math.round(((priceChange / prevClose) * 100) * 100) / 100
    }

    return c.json({
      symbol,
      latest_date: latestDate,
      latest_price: latestPrice,
      prev_close: prevClose,
      price_change: priceChange,
      price_change_percent: priceChangePercent,
      min_price: stats?.min_price ?? null,
      max_price: stats?.max_price ?? null,
      avg_volume: stats?.avg_volume ? Math.round(Number(stats.avg_volume)) : null,
      total_records: stats?.total_records ?? 0,
    })
  } catch (err: any) {
    return c.json({ error: true, message: err?.message || 'Database query error' }, 500)
  }
})

// GET /api/stocks/:symbol/forecast - Hasil peramalan/prediksi masa depan
app.get('/api/stocks/:symbol/forecast', async (c) => {
  try {
    const symbol = c.req.param('symbol').toUpperCase()
    const { results } = await c.env.DB.prepare(
      'SELECT * FROM stock_forecasts WHERE symbol = ? ORDER BY date ASC;'
    ).bind(symbol).all()

    return c.json({
      symbol,
      total_forecast_records: results.length,
      forecast: results,
    })
  } catch (err: any) {
    return c.json({ error: true, message: err?.message || 'Database query error' }, 500)
  }
})

// GET /api/stocks/:symbol - Riwayat harga dengan pagination & rentang tanggal
app.get('/api/stocks/:symbol', async (c) => {
  try {
    const symbol = c.req.param('symbol').toUpperCase()
    const startDate = c.req.query('start_date')
    const endDate = c.req.query('end_date')
    const limitParam = parseInt(c.req.query('limit') || '100', 10)
    const limit = Math.min(Math.max(limitParam, 1), 2000)
    const order = c.req.query('order')?.toLowerCase() === 'asc' ? 'ASC' : 'DESC'

    let query = 'SELECT * FROM stock_prices WHERE symbol = ?'
    const params: (string | number)[] = [symbol]

    if (startDate) {
      query += ' AND date >= ?'
      params.push(startDate)
    }
    if (endDate) {
      query += ' AND date <= ?'
      params.push(endDate)
    }

    query += ` ORDER BY date ${order} LIMIT ?;`
    params.push(limit)

    const { results } = await c.env.DB.prepare(query).bind(...params).all()

    return c.json({
      symbol,
      total_returned: results.length,
      data: results,
    })
  } catch (err: any) {
    return c.json({ error: true, message: err?.message || 'Database query error' }, 500)
  }
})

export default app
