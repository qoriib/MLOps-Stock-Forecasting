import { parquetReadObjects } from 'hyparquet'
import { compressors } from 'hyparquet-compressors'
import { APP_CONFIG } from '../configs/app.config'
import type { HistoricalItem, HistoricalResponse } from '../types'
import { listAssetFiles, readAssetBinary } from '../utils/assets'

/**
 * Melakukan parsing data Parquet harga saham ke array HistoricalItem.
 */
export async function parseStockParquet(arrayBuffer: ArrayBuffer): Promise<HistoricalItem[]> {
  try {
    const rows = await parquetReadObjects({
      file: arrayBuffer,
      compressors,
    })

    const items: HistoricalItem[] = []

    for (const r of rows as any[]) {
      if (!r || r.date === undefined || r.close === undefined) continue

      const dateStr = String(r.date).trim()
      const open = Number(r.open) || 0
      const high = Number(r.high) || 0
      const low = Number(r.low) || 0
      const close = Number(r.close) || 0
      const volume = Number(r.volume) || 0

      items.push({
        date: dateStr,
        open,
        high,
        low,
        close,
        volume,
      })
    }

    items.sort((a, b) => a.date.localeCompare(b.date))
    return items
  } catch (err) {
    console.error('[Parquet Parse Error] Gagal mem-parse file parquet:', err)
    return []
  }
}

/**
 * Mengambil daftar ticker yang tersedia secara dinamis dari file .parquet di folder assets.
 */
export async function getAvailableTickers(): Promise<string[]> {
  const files = await listAssetFiles()
  const tickers: string[] = []

  for (const f of files) {
    if (f.endsWith('.parquet')) {
      const ticker = f.replace(/\.parquet$/, '').toUpperCase()
      tickers.push(ticker)
    }
  }

  tickers.sort()
  return tickers.length > 0 ? tickers : [APP_CONFIG.defaultTicker]
}

/**
 * Mengambil deret harga historis saham langsung dari file Parquet ticker di web/backend/assets.
 */
export async function getStockHistory(
  ticker: string,
  limit = 500,
  startDate?: string,
  endDate?: string,
): Promise<HistoricalResponse | null> {
  const tickerClean = ticker.trim().toUpperCase()
  const binaryBuffer = await readAssetBinary(`${tickerClean}.parquet`)

  if (!binaryBuffer) {
    console.warn(`[Parquet Not Found] File data untuk ticker '${tickerClean}' tidak ditemukan di assets.`)
    return null
  }

  let records = await parseStockParquet(binaryBuffer)
  if (records.length === 0) return null

  if (startDate) {
    records = records.filter((r) => r.date >= startDate)
  }
  if (endDate) {
    records = records.filter((r) => r.date <= endDate)
  }

  const sliced = records.slice(-limit)

  return {
    ticker: tickerClean,
    total_records: records.length,
    returned_records: sliced.length,
    data: sliced,
  }
}
