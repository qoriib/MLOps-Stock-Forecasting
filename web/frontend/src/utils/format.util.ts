export interface FormatCurrencyOptions {
  prefix?: string
  minimumFractionDigits?: number
  maximumFractionDigits?: number
}

/**
 * Format angka ke mata uang Rupiah (IDR).
 * Menangani null/undefined/string kosong dengan fallback '—'.
 */
export function formatCurrency(
  value: number | string | null | undefined,
  options: FormatCurrencyOptions = {},
): string {
  if (value == null || value === '') return '—'
  const num = typeof value === 'string' ? Number(value) : value
  if (Number.isNaN(num)) return '—'

  const { minimumFractionDigits = 2, maximumFractionDigits = 2 } = options

  return num.toLocaleString('id-ID', {
    minimumFractionDigits,
    maximumFractionDigits,
  })
}

/**
 * Format angka umum dengan pemisah ribuan standar id-ID.
 */
export function formatNumber(
  value: number | string | null | undefined,
  options?: Intl.NumberFormatOptions,
): string {
  if (value == null || value === '') return '0'
  const num = typeof value === 'string' ? Number(value) : value
  if (Number.isNaN(num)) return '0'
  return num.toLocaleString('id-ID', options)
}
