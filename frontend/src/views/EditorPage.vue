<script setup lang="ts">
import { computed, ref } from 'vue'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import LatexEditorPanel from '@/components/convert/LatexEditorPanel.vue'

const code = ref(`\\documentclass{article}
\\usepackage{amsmath}
\\begin{document}
\\section{Monogram Editor}
Type your LaTeX here and use Preview to inspect output.

Inline math: $E = mc^2$

\\[
\\int_0^1 x^2 \\, dx = \\frac{1}{3}
\\]
\\end{document}`)

const activeTab = ref<'preview' | 'source'>('source')
const zoom = ref(100)
const copied = ref(false)

const renderedPreview = computed(() => {
  const escaped = code.value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  return `<pre style="white-space: pre-wrap; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; line-height: 1.6;">${escaped}</pre>`
})

async function handleCopy() {
  await navigator.clipboard.writeText(code.value)
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 1500)
}

function handleDownload() {
  const blob = new Blob([code.value], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = 'editor-notes.tex'
  anchor.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <main class="min-h-screen bg-background">
    <AppNavbar />

    <section class="px-4 pt-20 pb-4 md:px-6">
      <div class="mx-auto mb-4 max-w-[1400px]">
        <h1 class="text-3xl font-bold text-foreground md:text-4xl">LaTeX Editor</h1>
        <p class="mt-1 text-sm text-muted-foreground">Write, preview, and export your LaTeX from one workspace.</p>
      </div>

      <div class="mx-auto h-[calc(100vh-150px)] max-w-[1400px] overflow-hidden rounded-2xl border border-border bg-card">
        <LatexEditorPanel
          :model-value="code"
          :active-tab="activeTab"
          :copied="copied"
          :rendered-preview="renderedPreview"
          :zoom="zoom"
          @update:model-value="code = $event"
          @update:active-tab="activeTab = $event"
          @update:zoom="zoom = $event"
          @copy="handleCopy"
          @download="handleDownload"
        />
      </div>
    </section>
  </main>
</template>
