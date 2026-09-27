import { API_ENDPOINTS } from '@/configs'
import type {
  PredictResponse,
  StockHistoryResponse,
  ModelsResponse,
  PredictRequest,
} from '@/types'

/**
 * Custom Error Class untuk menangani response gagal dari backend API.
 */
export class ApiError extends Error {
  statusCode: number
  detail: unknown

  constructor(message: string, statusCode: number = 500, detail?: unknown) {
    super(message)
    this.name = 'ApiError'
    this.statusCode = statusCode
    this.detail = detail
  }
}

/**
 * Helper untuk mengekstrak pesan error ramah pengguna dari response FastAPI.
 */
function parseFastApiErrorMessage(errorData: unknown, statusCode: number): string {
  if (!errorData || typeof errorData !== 'object') {
    return `HTTP ${statusCode}: Terjadi kesalahan pada server`
  }

  const record = errorData as Record<string, unknown>

  // 1. Kasus standar FastAPI: detail berupa string
  if (typeof record.detail === 'string') {
    return record.detail
  }

  // 2. Kasus FastAPI validation error: detail berupa array of errors
  if (Array.isArray(record.detail) && record.detail.length > 0) {
    const firstError = record.detail[0] as { msg?: string; loc?: string[] }
    const field = firstError.loc ? firstError.loc.slice(-1)[0] : 'field'
    const msg = firstError.msg || 'Data tidak valid'
    return `Parameter '${field}' tidak valid: ${msg}`
  }

  // 3. Fallback jika ada field message atau error
  if (typeof record.message === 'string') return record.message
  if (typeof record.error === 'string') return record.error

  return `HTTP ${statusCode}: Gagal memproses permintaan`
}

/**
 * Wrapper HTTP fetch dengan penanganan error terpusat dan aman.
 */
async function request<T>(url: string, options?: RequestInit): Promise<T> {
  let response: Response

  try {
    response = await fetch(url, options)
  } catch (err: unknown) {
    const errorMsg =
      err instanceof Error ? err.message : 'Koneksi jaringan gagal atau server tidak dapat dijangkau'
    throw new ApiError(
      `Tidak dapat terhubung ke Backend API (${url}). Pastikan backend menyala. Detail: ${errorMsg}`,
      0,
      err,
    )
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => null)
    const userMessage = parseFastApiErrorMessage(errorData, response.status)
    throw new ApiError(userMessage, response.status, errorData)
  }

  try {
    return (await response.json()) as T
  } catch (jsonErr: unknown) {
    throw new ApiError(
      `Format data dari server tidak dapat diurai (JSON parsing error).`,
      response.status,
      jsonErr,
    )
  }
}

/**
 * Mengambil daftar ticker dan model yang tersedia dari backend.
 */
export async function fetchAvailableModels(): Promise<ModelsResponse> {
  return request<ModelsResponse>(API_ENDPOINTS.models, {
    method: 'GET',
    headers: { Accept: 'application/json' },
  })
}

/**
 * Mengambil data historis pasar saham (candlestick OHLC) dari backend.
 */
export async function fetchStockHistoryData(
  ticker: string,
  startDate: string,
  endDate: string,
): Promise<StockHistoryResponse> {
  const cleanTicker = ticker.trim().toUpperCase()
  const endpoint = API_ENDPOINTS.stockHistory(cleanTicker, startDate, endDate)

  return request<StockHistoryResponse>(endpoint, {
    method: 'GET',
    headers: { Accept: 'application/json' },
  })
}

/**
 * Mengirim permintaan inferensi peramalan harga saham ke backend.
 */
export async function fetchForecastPrediction(params: {
  ticker: string
  model: string
  startDate: string
  endDate: string
}): Promise<PredictResponse> {
  const payload: PredictRequest = {
    ticker: params.ticker.trim().toUpperCase(),
    model: params.model.trim().toLowerCase(),
    start_date: params.startDate,
    end_date: params.endDate,
  }

  return request<PredictResponse>(API_ENDPOINTS.predict, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify(payload),
  })
}
