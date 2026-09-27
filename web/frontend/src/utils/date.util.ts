import type { ISODateString } from '@astryxdesign/core/Calendar'

/**
 * Mengonversi objek Date JavaScript ke format standar ISO YYYY-MM-DD.
 * Digunakan untuk integrasi dengan form input tanggal dan parameter query API.
 */
export function toISODate(targetDate: Date): ISODateString {
  const calendarYear = targetDate.getFullYear()
  const rawMonth = targetDate.getMonth() + 1
  const calendarMonth = String(rawMonth).padStart(2, '0')
  const rawDay = targetDate.getDate()
  const calendarDay = String(rawDay).padStart(2, '0')

  const formattedIsoDate = `${calendarYear}-${calendarMonth}-${calendarDay}`
  return formattedIsoDate as ISODateString
}
