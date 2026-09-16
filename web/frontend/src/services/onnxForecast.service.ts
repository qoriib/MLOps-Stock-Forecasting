import * as ort from 'onnxruntime-web'
import { getStaticDataUrl, STATIC_BASE_URL } from '@/configs'
import type { PredictResponse, PredictionItem, HistoricalItem, HistoricalResponse } from '@/types'

// Cache session model ONNX di memori browser
const sessionCache = new Map<string, ort.InferenceSession>()
const historyCache = new Map<string, HistoricalItem[]>()

// Konfigurasi path WebAssembly dan logging ONNX Runtime
if (typeof window !== 'undefined') {
  ort.env.wasm.numThreads = 1
  ort.env.wasm.simd = true
  ort.env.logLevel = 'error'
}

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
 * Memuat atau menginisialisasi InferenceSession ONNX Runtime Web.
 */
async function getOrLoadOnnxSession(
  ticker: string,
  modelType: 'lstm' | 'gru',
): Promise<ort.InferenceSession> {
  const cacheKey = `${ticker}:${modelType}`
  if (sessionCache.has(cacheKey)) {
    return sessionCache.get(cacheKey)!
  }

  const base = STATIC_BASE_URL.endsWith('/') ? STATIC_BASE_URL.slice(0, -1) : STATIC_BASE_URL
  const onnxUrl = `${base}/models/${ticker}_${modelType.toUpperCase()}.onnx`

  // Di onnxruntime-web modern, WebGL digantikan oleh WebGPU (hardware) & WebAssembly SIMD (CPU)
  const providers: ort.InferenceSession.ExecutionProviderConfig[] =
    typeof navigator !== 'undefined' && 'gpu' in navigator
      ? ['webgpu', 'wasm']
      : ['wasm']

  try {
    const session = await ort.InferenceSession.create(onnxUrl, {
      executionProviders: providers,
      graphOptimizationLevel: 'all',
      logSeverityLevel: 3,
    })
    sessionCache.set(cacheKey, session)
    return session
  } catch (err) {
    try {
      // Fallback murni WebAssembly CPU
      const sessionWasm = await ort.InferenceSession.create(onnxUrl, {
        executionProviders: ['wasm'],
        graphOptimizationLevel: 'all',
        logSeverityLevel: 3,
      })
      sessionCache.set(cacheKey, sessionWasm)
      return sessionWasm
    } catch {
      throw new Error(`Gagal memuat model ONNX dari ${onnxUrl}: ${err}`)
    }
  }
}

/**
 * Menjalankan inferensi peramalan harga saham langsung di browser client menggunakan ONNX Runtime Web.
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

  // 3. Pemuatan model ONNX di browser
  const session = await getOrLoadOnnxSession(ticker, modelType)

  // 4. Inferensi Rekursif Multi-step Autoregressive via ONNX Runtime Web
  let currentWindow = scaledPrices.slice(-windowSize)
  const predictedScaled: number[] = []

  const inputName = session.inputNames[0] || 'input'
  const outputName = session.outputNames[0] || 'output'

  for (let i = 0; i < steps; i++) {
    const inputData = new Float32Array(currentWindow)
    const inputTensor = new ort.Tensor('float32', inputData, [1, windowSize, 1])

    const feeds: Record<string, ort.Tensor> = { [inputName]: inputTensor }
    const results = await session.run(feeds)
    const outputTensor = results[outputName]
    const nextVal = (outputTensor.data as Float32Array)[0]

    predictedScaled.push(nextVal)
    currentWindow = currentWindow.slice(1).concat(nextVal)
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
    model_name: `ONNX Runtime Web (${modelType.toUpperCase()}) [WebGL / WASM]`,
    forecast_steps: steps,
    last_historical_date: lastDateStr,
    predictions: predictionItems,
    history: allRecords.slice(-historyLimit),
  }
}
