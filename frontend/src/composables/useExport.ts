import { useAuth } from '@clerk/vue'
import { ref, toValue } from 'vue'
import type { MaybeRefOrGetter } from 'vue'

export type ExportFormat = 'pdf' | 'html' | 'tex'

interface ExportInput {
  format: ExportFormat
  texFileId?: string
  latex?: string
  filename?: string
}

export function useExport() {
  const exporting = ref(false)
  const error = ref<string | null>(null)

  let authRef: ReturnType<typeof useAuth> | null = null
  try {
    authRef = useAuth()
  } catch {
    authRef = null
  }

  async function buildHeaders(extra?: HeadersInit): Promise<Headers> {
    const headers = new Headers(extra)
    if (authRef) {
      const getToken = toValue(authRef.getToken as unknown as MaybeRefOrGetter<(() => Promise<string | null>) | undefined>)
      if (getToken) {
        const token = await getToken()
        if (token) {
          headers.set('Authorization', `Bearer ${token}`)
        }
      }
    }
    return headers
  }

  function extensionForFormat(format: ExportFormat): string {
    if (format === 'pdf') return 'pdf'
    if (format === 'html') return 'html'
    return 'tex'
  }

  function parseContentDispositionFilename(headerValue: string | null): string | null {
    if (!headerValue) return null

    const utf8Match = headerValue.match(/filename\*\s*=\s*UTF-8''([^;]+)/i)
    if (utf8Match?.[1]) {
      try {
        return decodeURIComponent(utf8Match[1].trim().replace(/^"|"$/g, ''))
      } catch {
        return utf8Match[1].trim().replace(/^"|"$/g, '')
      }
    }

    const basicMatch = headerValue.match(/filename\s*=\s*("?)([^";]+)\1/i)
    if (basicMatch?.[2]) {
      return basicMatch[2].trim()
    }

    return null
  }

  function buildFallbackFilename(filename: string | undefined, format: ExportFormat): string {
    const base = (filename || 'notes').trim() || 'notes'
    const safeBase = base.replace(/\.[A-Za-z0-9]+$/, '')
    return `${safeBase}.${extensionForFormat(format)}`
  }

  function downloadBlob(blob: Blob, filename: string) {
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  async function exportFile(input: ExportInput) {
    const { format, texFileId, latex, filename } = input

    exporting.value = true
    error.value = null

    try {
      let res: Response

      if (texFileId) {
        const headers = await buildHeaders()
        res = await fetch(`/api/tex-files/${encodeURIComponent(texFileId)}/export?format=${encodeURIComponent(format)}`, {
          method: 'GET',
          headers,
        })
      } else if (format === 'tex' && latex) {
        const headers = await buildHeaders({ 'Content-Type': 'application/json' })
        res = await fetch('/api/export', {
          method: 'POST',
          headers,
          body: JSON.stringify({ latex, filename: (filename || 'notes').trim() || 'notes' }),
        })
      } else {
        error.value = 'Only LaTeX (.tex) export is available before project save.'
        throw new Error(error.value)
      }

      if (!res.ok) {
        const data = await res.json().catch(() => ({ error: `Server error (${res.status})` }))
        error.value = data.error || `Export failed (${res.status})`
        throw new Error(error.value!)
      }

      const blob = await res.blob()
      const contentDisposition = res.headers.get('content-disposition')
      const serverFilename = parseContentDispositionFilename(contentDisposition)
      const downloadName = serverFilename || buildFallbackFilename(filename, format)
      downloadBlob(blob, downloadName)
    } catch (err) {
      if (!error.value) {
        error.value = err instanceof Error ? err.message : 'Export failed'
      }
      throw err
    } finally {
      exporting.value = false
    }
  }

  return { exporting, error, exportFile }
}
