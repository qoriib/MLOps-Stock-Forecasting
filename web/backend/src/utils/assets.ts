import { useStorage } from 'nitro/storage'
import fs from 'node:fs'
import path from 'node:path'

/**
 * Mencari path direktori assets lokal (di dalam folder web/backend/assets).
 * Tidak lagi menggunakan relative path traversal ../.. ke root artifact.
 */
function getLocalAssetsDir(): string {
  const candidateDirs = [
    path.resolve(process.cwd(), 'assets'),
    path.resolve(process.cwd(), 'web/backend/assets'),
  ]
  for (const d of candidateDirs) {
    if (fs.existsSync(d)) {
      return d
    }
  }
  return path.resolve(process.cwd(), 'assets')
}

/**
 * Membaca file teks (seperti file JSON scaler dan metrik) langsung dari folder assets backend.
 */
export async function readAssetText(filename: string): Promise<string | null> {
  // 1. Virtual storage Nitro (Cloudflare Worker serverAssets)
  try {
    const storage = useStorage('assets:assets')
    if (storage) {
      const item: unknown = await storage.getItem(filename)
      if (item !== null && item !== undefined) {
        if (typeof item === 'string') return item
        if (item instanceof Uint8Array) {
          return new TextDecoder().decode(item)
        }
        if (typeof Buffer !== 'undefined' && Buffer.isBuffer(item)) {
          return (item as any).toString('utf-8')
        }
        return JSON.stringify(item)
      }
    }
  } catch {
    // Lanjut ke fallback
  }

  // 2. Fallback Node.js fs (local development / testing dari ./assets)
  try {
    const filePath = path.join(getLocalAssetsDir(), filename)
    if (fs.existsSync(filePath)) {
      return fs.readFileSync(filePath, 'utf-8')
    }
  } catch {
    // fs tidak tersedia di isolate tertentu
  }

  return null
}

/**
 * Membaca file binary (seperti file .parquet) sebagai ArrayBuffer
 * langsung dari folder assets backend.
 */
export async function readAssetBinary(filename: string): Promise<ArrayBuffer | null> {
  // 1. Virtual storage Nitro (Cloudflare Worker serverAssets)
  try {
    const storage = useStorage('assets:assets')
    if (storage) {
      const raw: unknown = await storage.getItemRaw(filename)
      if (raw) {
        if (raw instanceof ArrayBuffer) return raw
        if (raw instanceof Uint8Array) {
          const copy = new Uint8Array(raw.byteLength)
          copy.set(raw)
          return copy.buffer as ArrayBuffer
        }
        if (typeof Buffer !== 'undefined' && Buffer.isBuffer(raw)) {
          const b = raw as any
          return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength) as ArrayBuffer
        }
      }
    }
  } catch {
    // Lanjut ke fallback
  }

  // 2. Fallback Node.js fs
  try {
    const filePath = path.join(getLocalAssetsDir(), filename)
    if (fs.existsSync(filePath)) {
      const buf = fs.readFileSync(filePath)
      const copy = new Uint8Array(buf.byteLength)
      copy.set(buf)
      return copy.buffer as ArrayBuffer
    }
  } catch {
    // fs tidak tersedia
  }

  return null
}

/**
 * Mendapatkan daftar file yang ada di folder web/backend/assets (untuk deteksi dinamis ticker).
 */
export async function listAssetFiles(): Promise<string[]> {
  const filesSet = new Set<string>()

  // 1. Dari virtual storage Nitro
  try {
    const storage = useStorage('assets:assets')
    if (storage) {
      const keys = await storage.getKeys()
      for (const k of keys) {
        const cleanName = k.replace(/^.*[:/]/, '')
        filesSet.add(cleanName)
      }
    }
  } catch {
    // ignore
  }

  // 2. Dari filesystem lokal (assets/)
  try {
    const assetsDir = getLocalAssetsDir()
    if (fs.existsSync(assetsDir)) {
      const files = fs.readdirSync(assetsDir)
      for (const f of files) {
        filesSet.add(f)
      }
    }
  } catch {
    // ignore
  }

  return Array.from(filesSet)
}
