import type { HistoricalItem, HistoricalResponse } from '../types'

/**
 * Mengambil daftar ticker yang tersedia secara dinamis dari Cloudflare D1.
 * Tidak ada ticker yang di-hardcode.
 */
export async function getAvailableTickers(db?: D1Database): Promise<string[]> {
  if (db) {
    try {
      const { results } = await db
        .prepare('SELECT DISTINCT ticker FROM stock_prices ORDER BY ticker ASC')
        .all<{ ticker: string }>()
      if (results && results.length > 0) {
        return results.map((r) => r.ticker)
      }
    } catch (err) {
      console.warn('[D1 Tickers Warning] Gagal mengambil daftar ticker:', err)
    }
  }
  return []
}

/**
 * Mengambil deret harga historis saham secara dinamis dari Cloudflare D1.
 * Tidak ada ticker yang di-hardcode.
 */
export async function getStockHistory(
  ticker: string,
  limit = 500,
  startDate?: string,
  endDate?: string,
  db?: D1Database,
): Promise<HistoricalResponse | null> {
  const tickerClean = ticker.trim().toUpperCase()

  if (db) {
    try {
      let query = 'SELECT date, open, high, low, close, volume FROM stock_prices WHERE ticker = ?'
      const params: (string | number)[] = [tickerClean]

      if (startDate) {
        query += ' AND date >= ?'
        params.push(startDate)
      }
      if (endDate) {
        query += ' AND date <= ?'
        params.push(endDate)
      }

      query += ' ORDER BY date ASC'

      const stmt = db.prepare(query).bind(...params)
      const { results } = await stmt.all<HistoricalItem>()

      if (results && results.length > 0) {
        const sliced = results.slice(-limit)
        return {
          ticker: tickerClean,
          total_records: results.length,
          returned_records: sliced.length,
          data: sliced,
        }
      }
    } catch (err) {
      console.warn(`[D1 Query Error] Gagal query D1 untuk '${tickerClean}':`, err)
    }
  }

  return null
}
