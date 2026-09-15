import type { ISODateString } from '@astryxdesign/core/Calendar'

/**
 * Konversi objek Date ke format ISODateString (YYYY-MM-DD).
 */
export function toISODate(date: Date): ISODateString {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}` as ISODateString
}

/**
 * Format tanggal YYYY-MM-DD menjadi DD/MM untuk tampilan sumbu grafik.
 */
export function formatShortDate(val: string): string {
  if (!val) return ''
  const parts = val.split('-')
  return parts.length === 3 ? `${parts[2]}/${parts[1]}` : val
}

/**
 * Menghasilkan objek Date mundur N hari dari hari ini.
 */
export function getDaysAgoDate(days: number): Date {
  const date = new Date()
  date.setDate(date.getDate() - days)
  return date
}
