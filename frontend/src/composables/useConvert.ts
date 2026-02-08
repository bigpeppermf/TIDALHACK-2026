import { ref } from 'vue'

export interface ConvertResult {
  success: boolean
  latex: string
  raw_text: string
  processing_time_ms: number
}

export interface ConvertError {
  success: false
  error: string
}

export function useConvert() {
  const loading = ref(false)
  const error = ref<string | null>(null)
  const result = ref<ConvertResult | null>(null)
  const REQUEST_TIMEOUT_MS = 120_000
  const MAX_RETRIES = 1

  async function optimizeImageForUpload(file: File): Promise<File> {
    if (typeof window === 'undefined' || !file.type.startsWith('image/')) {
      return file
    }

    const MAX_DIMENSION = 1600
    const QUALITY = 0.82

    try {
      const imageUrl = URL.createObjectURL(file)
      let img: HTMLImageElement
      try {
        img = await new Promise<HTMLImageElement>((resolve, reject) => {
          const el = new Image()
          el.onload = () => resolve(el)
          el.onerror = () => reject(new Error('Invalid image'))
          el.src = imageUrl
        })
      } finally {
        URL.revokeObjectURL(imageUrl)
      }

      const width = img.naturalWidth || img.width
      const height = img.naturalHeight || img.height
      const scale = Math.min(1, MAX_DIMENSION / Math.max(width, height))
      const targetWidth = Math.max(1, Math.round(width * scale))
      const targetHeight = Math.max(1, Math.round(height * scale))

      const canvas = document.createElement('canvas')
      canvas.width = targetWidth
      canvas.height = targetHeight
      const context = canvas.getContext('2d')
      if (!context) {
        return file
      }

      context.drawImage(img, 0, 0, targetWidth, targetHeight)

      const blob = await new Promise<Blob | null>((resolve) => {
        canvas.toBlob(resolve, 'image/jpeg', QUALITY)
      })
      if (!blob) {
        return file
      }

      const optimizedName = file.name.replace(/\.[^.]+$/, '') + '.jpg'
      return new File([blob], optimizedName, { type: 'image/jpeg' })
    } catch {
      return file
    }
  }

  async function convert(file: File, context: string = 'general'): Promise<ConvertResult> {
    loading.value = true
    error.value = null
    result.value = null

    const uploadFile = await optimizeImageForUpload(file)

    try {
      let lastErr: unknown = null

      for (let attempt = 0; attempt <= MAX_RETRIES; attempt += 1) {
        const formData = new FormData()
        formData.append('file', uploadFile, uploadFile.name)

        const controller = new AbortController()
        const timeoutId = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

        try {
          const res = await fetch(`/api/convert?context=${encodeURIComponent(context)}`, {
            method: 'POST',
            body: formData,
            signal: controller.signal,
          })

          const data = await res.json().catch(() => ({ success: false, error: `Server error (${res.status})` }))
          if (!res.ok || !data.success) {
            const message = data.error || `Server error (${res.status})`
            if (attempt < MAX_RETRIES && res.status >= 500) {
              lastErr = new Error(message)
              continue
            }
            error.value = message
            throw new Error(message)
          }

          result.value = data as ConvertResult
          return result.value
        } catch (err) {
          if (err instanceof DOMException && err.name === 'AbortError') {
            const timeoutMessage = 'Conversion timed out. Try a smaller/clearer image and retry.'
            if (attempt < MAX_RETRIES) {
              lastErr = new Error(timeoutMessage)
              continue
            }
            error.value = timeoutMessage
            throw new Error(timeoutMessage)
          }

          if (attempt < MAX_RETRIES) {
            lastErr = err
            continue
          }

          throw err
        } finally {
          window.clearTimeout(timeoutId)
        }
      }

      throw lastErr instanceof Error ? lastErr : new Error('Conversion failed')
    } catch (err) {
      if (!error.value) {
        error.value = err instanceof Error ? err.message : 'Network error'
      }
      throw err
    } finally {
      loading.value = false
    }
  }

  function reset() {
    loading.value = false
    error.value = null
    result.value = null
  }

  return { loading, error, result, convert, reset }
}
