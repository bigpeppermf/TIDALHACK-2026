<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import katex from 'katex'
import { useExport } from '@/composables/useExport'

const props = defineProps<{
  imageUrl: string
  latex: string
  isPdf?: boolean
  pdfFile?: File
}>()

const emit = defineEmits<{
  reset: []
}>()

const { exportTex } = useExport()

const code = ref(props.latex)
const copied = ref(false)
const activeTab = ref<'preview' | 'source'>('preview')
const slideIn = ref(false)
const pdfDataUrl = ref('')

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

onMounted(() => {
  setTimeout(() => {
    slideIn.value = true
  }, 50)
  
  // Create object URL for PDF if provided
  if (props.isPdf && props.pdfFile) {
    pdfDataUrl.value = URL.createObjectURL(props.pdfFile)
  }
})

watch(
  () => props.latex,
  (nextLatex) => {
    code.value = nextLatex
  },
)

/**
 * Render a clean, Overleaf-style preview of the LaTeX document.
 * Properly handles sections, math, and text content.
 */
const renderedPreview = computed(() => {
  let src = code.value
  const safeBlocks: string[] = []

  const insertSafeBlock = (content: string): string => {
    const token = `@@SAFE_BLOCK_${safeBlocks.length}@@`
    safeBlocks.push(content)
    return token
  }

  // Extract document body
  const beginDoc = src.indexOf('\\begin{document}')
  const endDoc = src.indexOf('\\end{document}')
  if (beginDoc !== -1 && endDoc !== -1) {
    src = src.slice(beginDoc + '\\begin{document}'.length, endDoc).trim()
  }

  // Handle sections and subsections FIRST
  src = src.replace(/\\section\{([^}]*)\}/g, (_m, title) => 
    insertSafeBlock(`<h2 class="text-2xl font-bold mt-8 mb-4 text-foreground">${escapeHtml(title)}</h2>`)
  )
  src = src.replace(/\\subsection\{([^}]*)\}/g, (_m, title) => 
    insertSafeBlock(`<h3 class="text-xl font-semibold mt-6 mb-3 text-foreground">${escapeHtml(title)}</h3>`)
  )
  src = src.replace(/\\subsubsection\{([^}]*)\}/g, (_m, title) => 
    insertSafeBlock(`<h4 class="text-lg font-medium mt-4 mb-2 text-foreground/90">${escapeHtml(title)}</h4>`)
  )

  // Handle display math environments BEFORE inline math
  src = src.replace(/\\\[([\s\S]*?)\\\]/g, (_m, tex) => {
    try {
      return insertSafeBlock(`<div class="my-6 overflow-x-auto flex justify-center">${katex.renderToString(tex.trim(), { displayMode: true, throwOnError: false })}</div>`)
    } catch { 
      return insertSafeBlock(`<div class="my-6 p-4 bg-destructive/10 text-destructive rounded font-mono text-sm overflow-x-auto">${escapeHtml(tex)}</div>`) 
    }
  })
  
  src = src.replace(/\$\$([\s\S]*?)\$\$/g, (_m, tex) => {
    try {
      return insertSafeBlock(`<div class="my-6 overflow-x-auto flex justify-center">${katex.renderToString(tex.trim(), { displayMode: true, throwOnError: false })}</div>`)
    } catch { 
      return insertSafeBlock(`<div class="my-6 p-4 bg-destructive/10 text-destructive rounded font-mono text-sm overflow-x-auto">${escapeHtml(tex)}</div>`) 
    }
  })

  // Handle align, equation environments
  src = src.replace(/\\begin\{(align\*?|equation\*?|gather\*?)\}([\s\S]*?)\\end\{\1\}/g, (_m, _env, tex) => {
    try {
      return insertSafeBlock(`<div class="my-6 overflow-x-auto flex justify-center">${katex.renderToString(tex.trim(), { displayMode: true, throwOnError: false })}</div>`)
    } catch { 
      return insertSafeBlock(`<div class="my-6 p-4 bg-destructive/10 text-destructive rounded font-mono text-sm overflow-x-auto">${escapeHtml(tex)}</div>`) 
    }
  })

  // Handle inline math - CRITICAL: Do this before escaping HTML
  src = src.replace(/\$([^$]+?)\$/g, (_m, tex) => {
    try {
      return insertSafeBlock(katex.renderToString(tex.trim(), { displayMode: false, throwOnError: false }))
    } catch { 
      return insertSafeBlock(`<span class="text-destructive font-mono text-sm">${escapeHtml(tex)}</span>`) 
    }
  })

  // Handle itemize/enumerate - process items recursively to catch nested math
  src = src.replace(/\\begin\{itemize\}([\s\S]*?)\\end\{itemize\}/g, (_m, items) => {
    const processedItems = items.split('\\item').filter((item: string) => item.trim()).map((item: string) => {
      let processedItem = item.trim()
      // Process any remaining inline math in list items
      processedItem = processedItem.replace(/\$([^$]+?)\$/g, (_m2: string, tex: string) => {
        try {
          return insertSafeBlock(katex.renderToString(tex.trim(), { displayMode: false, throwOnError: false }))
        } catch { 
          return insertSafeBlock(`<span class="text-destructive font-mono text-sm">${escapeHtml(tex)}</span>`) 
        }
      })
      return `<li class="ml-6 mb-2">${processedItem}</li>`
    }).join('')
    return insertSafeBlock(`<ul class="list-disc my-4">${processedItems}</ul>`)
  })
  
  src = src.replace(/\\begin\{enumerate\}([\s\S]*?)\\end\{enumerate\}/g, (_m, items) => {
    const processedItems = items.split('\\item').filter((item: string) => item.trim()).map((item: string) => {
      let processedItem = item.trim()
      // Process any remaining inline math in list items
      processedItem = processedItem.replace(/\$([^$]+?)\$/g, (_m2: string, tex: string) => {
        try {
          return insertSafeBlock(katex.renderToString(tex.trim(), { displayMode: false, throwOnError: false }))
        } catch { 
          return insertSafeBlock(`<span class="text-destructive font-mono text-sm">${escapeHtml(tex)}</span>`) 
        }
      })
      return `<li class="ml-6 mb-2">${processedItem}</li>`
    }).join('')
    return insertSafeBlock(`<ol class="list-decimal my-4">${processedItems}</ol>`)
  })

  // Handle common LaTeX text commands BEFORE escaping
  src = src.replace(/\\textbf\{([^}]*)\}/g, (_m, text) => insertSafeBlock(`<strong>${escapeHtml(text)}</strong>`))
  src = src.replace(/\\textit\{([^}]*)\}/g, (_m, text) => insertSafeBlock(`<em>${escapeHtml(text)}</em>`))
  src = src.replace(/\\emph\{([^}]*)\}/g, (_m, text) => insertSafeBlock(`<em>${escapeHtml(text)}</em>`))
  src = src.replace(/\\texttt\{([^}]*)\}/g, (_m, text) => insertSafeBlock(`<code class="font-mono text-sm">${escapeHtml(text)}</code>`))
  
  // Escape remaining HTML
  src = escapeHtml(src)

  // Convert paragraphs
  const paragraphs = src.split(/\n\s*\n/)
  src = paragraphs.map(p => {
    const trimmed = p.trim()
    if (!trimmed) return ''
    const text = trimmed.replace(/\n/g, ' ')
    return `<p class="mb-4 text-base leading-relaxed">${text}</p>`
  }).join('')
  
  // Restore safe blocks
  src = src.replace(/@@SAFE_BLOCK_(\d+)@@/g, (_m, idx) => safeBlocks[Number(idx)] ?? '')
  
  return src
})

async function handleCopy() {
  await navigator.clipboard.writeText(code.value)
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 2000)
}

async function handleDownload() {
  try {
    await exportTex(code.value, 'monogram-output')
  } catch {
    // Fallback to client-side download
    const blob = new Blob([code.value], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'monogram-output.tex'
    a.click()
    URL.revokeObjectURL(url)
  }
}
</script>

<template>
  <div
    :class="[
      'flex w-full h-[calc(100vh-200px)] max-w-7xl flex-col gap-4 transition-all duration-700 lg:flex-row',
      slideIn ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0',
    ]"
  >
    <!-- Left panel: Original Image -->
    <div
      :class="[
        'flex-1 flex flex-col overflow-hidden rounded-2xl border border-border bg-card transition-all duration-700 delay-100',
        slideIn ? 'translate-x-0 opacity-100' : '-translate-x-12 opacity-0',
      ]"
    >
      <div class="flex items-center gap-2 border-b border-border px-5 py-3 flex-shrink-0">
        <svg class="h-4 w-4 text-muted-foreground" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7Z" /><circle cx="12" cy="12" r="3" />
        </svg>
        <span class="text-sm font-medium text-foreground">Original</span>
      </div>
      <div class="flex-1 flex items-center justify-center bg-[hsl(var(--background)/0.5)] p-6 overflow-auto">
        <!-- PDF viewer -->
        <iframe
          v-if="props.isPdf && pdfDataUrl"
          :src="pdfDataUrl"
          class="w-full h-full rounded-lg border border-border/50"
          title="Original PDF"
        />
        <!-- Image preview -->
        <img
          v-else-if="!props.isPdf && props.imageUrl"
          :src="props.imageUrl"
          alt="Original handwritten notes"
          class="max-h-full w-full rounded-lg object-contain"
        />
        <!-- Fallback placeholder -->
        <div v-else class="flex flex-col items-center gap-3 py-12">
          <svg class="h-32 w-32 text-primary/50" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
            <line x1="10" y1="9" x2="8" y2="9" />
          </svg>
          <span class="text-base font-medium text-muted-foreground">{{ props.isPdf ? 'PDF Document' : 'Document' }}</span>
          <p class="text-sm text-muted-foreground/70">Original content converted to LaTeX</p>
        </div>
      </div>
    </div>

    <!-- Right panel: LaTeX -->
    <div
      :class="[
        'flex-1 flex flex-col overflow-hidden rounded-2xl border border-border bg-card transition-all duration-700 delay-200',
        slideIn ? 'translate-x-0 opacity-100' : 'translate-x-12 opacity-0',
      ]"
    >
      <!-- Tab header -->
      <div class="flex items-center justify-between border-b border-border px-5 py-3 flex-shrink-0">
        <div class="flex gap-1">
          <button
            type="button"
            :class="[
              'flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm transition-colors',
              activeTab === 'source'
                ? 'bg-secondary text-foreground'
                : 'text-muted-foreground hover:text-foreground',
            ]"
            @click="activeTab = 'source'"
          >
            <svg class="h-3.5 w-3.5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M16 18 22 12 16 6M8 6 2 12 8 18" />
            </svg>
            Source
          </button>
          <button
            type="button"
            :class="[
              'flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm transition-colors',
              activeTab === 'preview'
                ? 'bg-secondary text-foreground'
                : 'text-muted-foreground hover:text-foreground',
            ]"
            @click="activeTab = 'preview'"
          >
            <svg class="h-3.5 w-3.5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7Z" /><circle cx="12" cy="12" r="3" />
            </svg>
            Preview
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="flex-1 relative overflow-hidden">
        <textarea
          v-if="activeTab === 'source'"
          v-model="code"
          class="h-full w-full resize-none bg-transparent p-6 font-mono text-sm leading-relaxed text-foreground outline-none placeholder:text-muted-foreground"
          spellcheck="false"
        />
        <div v-else class="h-full overflow-y-auto bg-white text-black">
          <div class="max-w-4xl mx-auto p-8 latex-document-preview" v-html="renderedPreview" />
        </div>
      </div>

      <!-- Action bar -->
      <div class="flex items-center justify-between border-t border-border px-5 py-3 flex-shrink-0">
        <span class="text-xs text-muted-foreground">{{ code.length }} characters</span>
        <div class="flex gap-2">
          <button
            type="button"
            class="inline-flex items-center gap-1.5 rounded-md border border-border bg-transparent px-3 py-1.5 text-sm text-foreground transition-colors hover:bg-secondary"
            @click="handleCopy"
          >
            <!-- Check or Clipboard icon -->
            <svg v-if="copied" class="h-3.5 w-3.5 text-primary" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 6 9 17l-5-5" />
            </svg>
            <svg v-else class="h-3.5 w-3.5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect width="8" height="4" x="8" y="2" rx="1" ry="1" /><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
            </svg>
            {{ copied ? 'Copied' : 'Copy' }}
          </button>
          <button
            type="button"
            class="inline-flex items-center gap-1.5 rounded-md border border-border bg-transparent px-3 py-1.5 text-sm text-foreground transition-colors hover:bg-secondary"
            @click="handleDownload"
          >
            <svg class="h-3.5 w-3.5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" />
            </svg>
            Download .tex
          </button>
        </div>
      </div>
    </div>

    <!-- Floating reset button -->
    <div class="fixed bottom-6 left-1/2 z-20 -translate-x-1/2">
      <button
        type="button"
        class="inline-flex items-center gap-2 rounded-full border border-border bg-[hsl(var(--card)/0.9)] px-4 py-2 text-sm text-foreground shadow-lg backdrop-blur-sm transition-colors hover:bg-secondary"
        @click="emit('reset')"
      >
        <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" /><path d="M3 3v5h5" />
        </svg>
        Convert Another
      </button>
    </div>
  </div>
</template>
