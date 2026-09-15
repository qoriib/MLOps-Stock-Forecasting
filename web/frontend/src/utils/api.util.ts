/**
 * Mengekstrak pesan error ramah pengguna dari unknown catch block error.
 */
export function extractErrorMessage(
  err: unknown,
  fallbackMessage = 'Terjadi kesalahan sistem yang tidak terduga',
): string {
  if (err instanceof Error) {
    return err.message
  }
  if (typeof err === 'string') {
    return err
  }
  return fallbackMessage
}

/**
 * Memeriksa status respons fetch dan mem-parsing JSON data atau melempar Error terformat.
 */
export async function parseApiResponse<T>(
  response: Response,
  defaultErrorMessage = 'Gagal memproses data dari server',
): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: null }))
    const message =
      errorData?.detail || `HTTP ${response.status}: ${defaultErrorMessage}`
    throw new Error(message)
  }
  return (await response.json()) as T
}
