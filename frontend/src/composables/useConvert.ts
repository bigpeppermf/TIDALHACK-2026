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

  async function convert(file: File, context: string = 'general'): Promise<ConvertResult> {
    loading.value = true
    error.value = null
    result.value = null

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`/api/convert?context=${encodeURIComponent(context)}`, {
        method: 'POST',
        body: formData,
      })

      const data = await res.json()

      if (!res.ok || !data.success) {
        const message = data.error || `Server error (${res.status})`
        error.value = message
        throw new Error(message)
      }

      result.value = data as ConvertResult
      return result.value
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
