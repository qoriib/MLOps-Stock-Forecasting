import * as tf from '@tensorflow/tfjs'
import { getStaticDataUrl, STATIC_BASE_URL } from '@/configs'
import type { PredictResponse, PredictionItem, HistoricalItem, HistoricalResponse } from '@/types'

// Cache model tfjs di memori browser
const modelCache = new Map<string, tf.LayersModel>()
const historyCache = new Map<string, HistoricalItem[]>()

/**
 * Memuat riwayat data historis saham dari asset lokal/public browser.
 */
export async function fetchStockHistory(
  ticker: string,
  limit = 500,
  startDate?: string,
  endDate?: string,
): Promise<HistoricalResponse> {
  const tickerClean = ticker.trim().toUpperCase()

  let items: HistoricalItem[] = []
  if (historyCache.has(tickerClean)) {
    items = historyCache.get(tickerClean)!
  } else {
    try {
      const response = await fetch(getStaticDataUrl(tickerClean))
      if (response.ok) {
        items = await response.json()
        historyCache.set(tickerClean, items)
      }
    } catch {
      // Fallback jika fetch gagal
    }
  }

  // Filter rentang tanggal jika ditentukan
  let filtered = [...items]
  if (startDate) {
    filtered = filtered.filter((d) => d.date >= startDate)
  }
  if (endDate) {
    filtered = filtered.filter((d) => d.date <= endDate)
  }

  const sliced = filtered.slice(-limit)

  return {
    ticker: tickerClean,
    total_records: filtered.length,
    returned_records: sliced.length,
    data: sliced,
  }
}

/**
 * Membantu pembuatan tanggal hari kerja (Business Days / bdate_range).
 */
function generateFutureBusinessDates(lastDateStr: string, steps: number): string[] {
  const dates: string[] = []
  const current = new Date(lastDateStr)

  while (dates.length < steps) {
    current.setDate(current.getDate() + 1)
    const dayOfWeek = current.getDay()
    // 0 = Minggu, 6 = Sabtu
    if (dayOfWeek !== 0 && dayOfWeek !== 6) {
      const yyyy = current.getFullYear()
      const mm = String(current.getMonth() + 1).padStart(2, '0')
      const dd = String(current.getDate()).padStart(2, '0')
      dates.push(`${yyyy}-${mm}-${dd}`)
    }
  }

  return dates
}

/**
 * Memuat model TensorFlow.js atau mengompilasi model LSTM/GRU secara lokal di browser.
 */
async function getOrBuildModel(
  ticker: string,
  modelType: 'lstm' | 'gru',
  trainingData: number[],
  windowSize = 30,
): Promise<tf.LayersModel> {
  const cacheKey = `${ticker}:${modelType}`
  if (modelCache.has(cacheKey)) {
    return modelCache.get(cacheKey)!
  }

  const base = STATIC_BASE_URL.endsWith('/') ? STATIC_BASE_URL.slice(0, -1) : STATIC_BASE_URL
  const modelUrl = `${base}/models/${ticker}_${modelType.toUpperCase()}/model.json`
  try {
    const loadedModel = await tf.loadLayersModel(modelUrl)
    modelCache.set(cacheKey, loadedModel)
    return loadedModel
  } catch {
    // Model file belum diexport ke static files, bangun model in-browser native dengan TensorFlow.js
  }

  // Inisialisasi arsitektur Sequential TensorFlow.js langsung di browser
  const model = tf.sequential()

  if (modelType === 'gru') {
    model.add(
      tf.layers.gru({
        units: 64,
        returnSequences: true,
        inputShape: [windowSize, 1],
      }),
    )
    model.add(tf.layers.dropout({ rate: 0.2 }))
    model.add(
      tf.layers.gru({
        units: 32,
        returnSequences: false,
      }),
    )
  } else {
    model.add(
      tf.layers.lstm({
        units: 64,
        returnSequences: true,
        inputShape: [windowSize, 1],
      }),
    )
    model.add(tf.layers.dropout({ rate: 0.2 }))
    model.add(
      tf.layers.lstm({
        units: 32,
        returnSequences: false,
      }),
    )
  }

  model.add(tf.layers.dropout({ rate: 0.2 }))
  model.add(tf.layers.dense({ units: 16, activation: 'relu' }))
  model.add(tf.layers.dense({ units: 1 }))

  model.compile({
    optimizer: tf.train.adam(0.001),
    loss: 'meanSquaredError',
  })

  // Training / kalibrasi instan di GPU browser menggunakan WebGL
  if (trainingData.length > windowSize + 10) {
    const X: number[][][] = []
    const y: number[] = []

    for (let i = windowSize; i < trainingData.length; i++) {
      const window = trainingData.slice(i - windowSize, i).map((v) => [v])
      X.push(window)
      y.push(trainingData[i])
    }

    const xs = tf.tensor3d(X)
    const ys = tf.tensor2d(y, [y.length, 1])

    await model.fit(xs, ys, {
      epochs: 8,
      batchSize: 32,
      verbose: 0,
      shuffle: true,
    })

    xs.dispose()
    ys.dispose()
  }

  modelCache.set(cacheKey, model)
  return model
}

/**
 * Menjalankan inferensi peramalan harga saham langsung di browser client menggunakan TensorFlow.js.
 */
export async function runInBrowserForecast(params: {
  ticker: string
  modelType?: string
  steps?: number
  startDate?: string
  endDate?: string
  historyLimit?: number
}): Promise<PredictResponse> {
  const ticker = params.ticker.trim().toUpperCase()
  const rawType = (params.modelType || 'lstm').toLowerCase()
  const modelType: 'lstm' | 'gru' = rawType === 'gru' ? 'gru' : 'lstm'
  const steps = params.steps && params.steps > 0 ? params.steps : 30
  const historyLimit = params.historyLimit || 30

  // 1. Dapatkan data historis
  const historyRes = await fetchStockHistory(ticker, 500, params.startDate, params.endDate)
  const allRecords = historyRes.data
  if (!allRecords || allRecords.length === 0) {
    throw new Error(`Data pasar untuk ticker '${ticker}' tidak ditemukan.`)
  }

  const windowSize = 30
  const closePrices = allRecords.map((r) => r.close)

  if (closePrices.length < windowSize) {
    throw new Error(
      `Data historis (${closePrices.length} baris) belum mencukupi window size minimal (${windowSize}).`,
    )
  }

  // 2. Normalisasi MinMaxScaler langsung di JavaScript
  const minVal = Math.min(...closePrices)
  const maxVal = Math.max(...closePrices)
  const rangeVal = maxVal - minVal > 0 ? maxVal - minVal : 1.0

  const scaledPrices = closePrices.map((p) => (p - minVal) / rangeVal)

  // 3. Pemuatan atau kompilasi model di browser
  const model = await getOrBuildModel(ticker, modelType, scaledPrices, windowSize)

  // 4. Inferensi Rekursif Multi-step Autoregressive
  let currentWindow = scaledPrices.slice(-windowSize)
  const predictedScaled: number[] = []

  for (let i = 0; i < steps; i++) {
    const inputTensor = tf.tensor3d([currentWindow.map((v) => [v])], [1, windowSize, 1])
    const predTensor = model.predict(inputTensor) as tf.Tensor
    const predData = await predTensor.data()
    const nextVal = predData[0]

    predictedScaled.push(nextVal)
    currentWindow = currentWindow.slice(1).concat(nextVal)

    inputTensor.dispose()
    predTensor.dispose()
  }

  // 5. Denormalisasi kembali ke harga riil Rupiah
  const predictedPrices = predictedScaled.map((v) => Math.round((v * rangeVal + minVal) * 100) / 100)

  // 6. Hitung estimasi interval keyakinan 95%
  const last60 = closePrices.slice(-60)
  let diffSum = 0
  for (let i = 1; i < last60.length; i++) {
    diffSum += Math.pow(last60[i] - last60[i - 1], 2)
  }
  const rmse = Math.sqrt(diffSum / Math.max(1, last60.length - 1)) || 50

  const lastDateStr = allRecords[allRecords.length - 1].date
  const futureDates = generateFutureBusinessDates(lastDateStr, steps)

  const predictionItems: PredictionItem[] = futureDates.map((date, idx) => {
    const price = predictedPrices[idx]
    const margin = 1.96 * rmse * (1.0 + 0.03 * idx)
    return {
      date,
      predicted_price: price,
      lower_bound: Math.round(Math.max(0, price - margin) * 100) / 100,
      upper_bound: Math.round((price + margin) * 100) / 100,
    }
  })

  return {
    ticker,
    model_type: modelType,
    model_name: `TensorFlow.js (${modelType.toUpperCase()}) [In-Browser WebGL]`,
    forecast_steps: steps,
    last_historical_date: lastDateStr,
    predictions: predictionItems,
    history: allRecords.slice(-historyLimit),
  }
}
