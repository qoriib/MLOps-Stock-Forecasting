export interface CurrencyFormattingOptions {
  minimumFractionDigits?: number
  maximumFractionDigits?: number
}

/**
 * Memformat nilai angka menjadi format mata uang Rupiah (IDR) standar Indonesia.
 * Menangani input null, undefined, string kosong, atau NaN dengan mengembalikan placeholder '—'.
 */
export function formatCurrency(
  rawPriceValue: number | string | null | undefined,
  formattingOptions: CurrencyFormattingOptions = {},
): string {
  if (rawPriceValue === null || rawPriceValue === undefined || rawPriceValue === '') {
    return '—'
  }

  let numericPriceValue: number
  if (typeof rawPriceValue === 'string') {
    numericPriceValue = Number(rawPriceValue)
  } else {
    numericPriceValue = rawPriceValue
  }

  if (Number.isNaN(numericPriceValue)) {
    return '—'
  }

  const minimumFractionDigits = formattingOptions.minimumFractionDigits ?? 2
  const maximumFractionDigits = formattingOptions.maximumFractionDigits ?? 2

  const formattedCurrencyString = numericPriceValue.toLocaleString('en-US', {
    minimumFractionDigits,
    maximumFractionDigits,
  })

  return formattedCurrencyString
}
