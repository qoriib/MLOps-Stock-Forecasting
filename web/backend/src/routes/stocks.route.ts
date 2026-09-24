import { Hono } from 'hono'
import { getStockHistory } from '../data/stocks.data'
import type { HonoEnv } from '../types'

export const stocksRoute = new Hono<HonoEnv>()

stocksRoute.get('/stocks/:ticker', async (c) => {
  const ticker = c.req.param('ticker')
  const limitParam = c.req.query('limit')
  const startDate = c.req.query('start_date')
  const endDate = c.req.query('end_date')

  const limit = limitParam ? parseInt(limitParam, 10) : 500

  const history = await getStockHistory(ticker, limit, startDate, endDate)
  if (!history) {
    return c.json(
      {
        error: 'Not Found',
        message: `Data saham untuk ticker '${ticker}' tidak ditemukan.`,
      },
      404,
    )
  }

  return c.json(history)
})
