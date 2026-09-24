import { Hono } from 'hono'
import { getModelsOverview } from '../data/models.data'
import type { HonoEnv } from '../types'

export const modelsRoute = new Hono<HonoEnv>()

modelsRoute.get('/models', async (c) => {
  const overview = await getModelsOverview()
  return c.json(overview)
})

