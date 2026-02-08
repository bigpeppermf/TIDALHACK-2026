import { ref } from 'vue'

export function useExport() {
  const exporting = ref(false)
  const error = ref<string | null>(null)

  async function exportTex(latex: string, filename: string = 'notes') {
    exporting.value = true
    error.value = null

    try {
      const res = await fetch('/api/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latex, filename }),
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({ error: `Server error (${res.status})` }))
        error.value = data.error || `Export failed (${res.status})`
        throw new Error(error.value!)
      }

      // Trigger browser download from the response blob
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${filename}.tex`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      if (!error.value) {
        error.value = err instanceof Error ? err.message : 'Export failed'
      }
      throw err
    } finally {
      exporting.value = false
    }
  }

  return { exporting, error, exportTex }
}
