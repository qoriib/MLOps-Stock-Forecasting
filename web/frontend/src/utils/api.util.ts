/**
 * Mengekstrak pesan error yang dapat dibaca manusia dari blok tangkapan (catch block) try-catch.
 * Mendukung objek Error standar, string, maupun tipe error yang belum diketahui.
 */
export function extractErrorMessage(
  caughtError: unknown,
  fallbackMessage: string = 'Terjadi kesalahan sistem yang tidak terduga',
): string {
  if (caughtError instanceof Error) {
    if (caughtError.message && caughtError.message.trim().length > 0) {
      return caughtError.message
    }
  }

  if (typeof caughtError === 'string') {
    if (caughtError.trim().length > 0) {
      return caughtError
    }
  }

  return fallbackMessage
}
