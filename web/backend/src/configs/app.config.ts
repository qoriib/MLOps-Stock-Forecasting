export const APP_CONFIG = {
  name: 'Stock Forecast Inference API',
  version: '2.0.0',
  runtime: 'Hono on Nitro (TensorFlow.js Edge)',
  defaultTicker: 'BBCA.JK',
  defaultModelType: 'lstm',
  availableModelTypes: ['lstm', 'gru'],
  defaultWindowSize: 30,
  defaultSteps: 30,
  defaultHistoryLimit: 30,
  confidenceIntervalZ: 1.96,
} as const
