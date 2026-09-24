import { Hono } from 'hono'
import { executeForecast } from '../services/forecast.service'
import type { HonoEnv, PredictRequest } from '../types'

export const predictRoute = new Hono<HonoEnv>()

predictRoute.post('/predict', async (c) => {
  try {
    const body = await c.req.json<PredictRequest>()

    if (!body || !body.ticker) {
      return c.json(
        {
          error: 'Bad Request',
          message: "Field 'ticker' wajib diisi.",
        },
        400,
      )
    }

    const result = await executeForecast(body)
    return c.json(result)
  } catch (err: any) {
    const errorMessage = err?.message || 'Terjadi kegagalan saat proses inferensi model.'
    const status = errorMessage.includes('tidak ditemukan') ? 404 : 500

    return c.json(
      {
        error: status === 404 ? 'Not Found' : 'Internal Server Error',
        message: errorMessage,
      },
      status,
    )
  }
})
