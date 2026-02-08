<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick, shallowRef, markRaw } from 'vue'
import katex from 'katex'
import * as PDFJS from 'pdfjs-dist'
import { useExport } from '@/composables/useExport'

// Set up PDF.js worker - serve from public folder
PDFJS.GlobalWorkerOptions.workerSrc = '/pdf.worker.mjs'

const props = defineProps<{
  imageUrl: string
  latex: string
  isPdf?: boolean
  pdfFile?: File
  texFileId?: string
}>()

const emit = defineEmits<{
  reset: []
}>()

const { exportFile, exporting, error: exportError } = useExport()

const code = ref(props.latex)
const copied = ref(false)
const activeTab = ref<'preview' | 'source'>('preview')
const slideIn = ref(false)
const leftZoom = ref(100)
const rightZoom = ref(100)
const pdfDoc = shallowRef<any>(null)
const currentPage = ref(1)
const totalPages = ref(0)
const pdfCanvas = ref<HTMLCanvasElement | null>(null)
const pdfLoading = ref(false)
const pdfError = ref('')
const pageRendering = ref(false)
const pageNumPending = ref<number | null>(null)
const renderTask = shallowRef<any>(null)
const showDownloadOptions = ref(false)
const selectedFormat = ref<'tex' | 'html' | 'pdf'>('tex')
const exportNotice = ref<string | null>(null)

const formatOptions = [
  { value: 'tex' as const, label: 'LaTeX (.tex)' },
  { value: 'html' as const, label: 'HTML (.html)' },
  { value: 'pdf' as const, label: 'PDF (.pdf)' },
]

const canExportRemoteFormats = computed(() => Boolean(props.texFileId))

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

const KATEX_MACROS: Record<string, string> = {
  '\\R': '\\mathbb{R}',
  '\\N': '\\mathbb{N}',
  '\\Z': '\\mathbb{Z}',
  '\\Q': '\\mathbb{Q}',
  '\\C': '\\mathbb{C}',
  '\\dx': '\\,dx',
  '\\dy': '\\,dy',
  '\\dt': '\\,dt',
  '\\ds': '\\,ds',
}

function safeMathRender(tex: string, displayMode: boolean = false): string {
  try {
    let cleanedTex = tex.trim()
    cleanedTex = cleanedTex.replace(/\\MATH/g, '')
    cleanedTex = cleanedTex.replace(/\\begin\{scope\}/g, '')
    cleanedTex = cleanedTex.replace(/\\end\{scope\}/g, '')
    cleanedTex = cleanedTex.replace(/\\foreach/g, '%')
    cleanedTex = cleanedTex.replace(/\\label\{[^}]*\}/g, '')
    cleanedTex = cleanedTex.replace(/\\nonumber/g, '')
    cleanedTex = cleanedTex.replace(/\\notag/g, '')
    cleanedTex = cleanedTex.replace(/\\allowbreak/g, '')

    return katex.renderToString(cleanedTex, {
      displayMode,
      throwOnError: false,
      strict: false,
      output: 'htmlAndMathml',
      errorColor: '#000',
      trust: false,
      macros: KATEX_MACROS,
    })
  } catch {
    const text = tex
      .trim()
      .replace(/\\\\/g, '\n')
      .replace(/\$/g, '')
      .replace(/\{/g, '(')
      .replace(/\}/g, ')')
      .slice(0, 120)

    return displayMode
      ? `<div class="my-6 overflow-x-auto rounded border border-black/10 bg-black/5 p-3 font-mono text-xs text-black">${escapeHtml(text)}</div>`
      : `<code class="rounded border border-black/10 bg-black/5 px-1.5 py-0.5 font-mono text-xs text-black">${escapeHtml(text)}</code>`
  }
}

onMounted(() => {
  setTimeout(() => {
    slideIn.value = true
  }, 50)
})

async function loadPdf(file: File) {
  pdfLoading.value = true
  pdfError.value = ''
  try {
    const arrayBuffer = await file.arrayBuffer()
    const uint8Array = new Uint8Array(arrayBuffer)

    const pdf = await PDFJS.getDocument({ 
      data: uint8Array,
      disableAutoFetch: false,
      disableStream: false
    }).promise

    pdfDoc.value = markRaw(pdf)
    totalPages.value = pdf.numPages
    currentPage.value = 1
    pageNumPending.value = null
    pdfLoading.value = false

    // Wait until PDF viewer canvas is mounted in the DOM.
    await nextTick()
    queueRenderPage(1)
  } catch (error: any) {
    pdfError.value = `Failed to load PDF: ${error?.message || 'Unknown error'}`
    pdfDoc.value = null
    totalPages.value = 0
    currentPage.value = 1
    pdfLoading.value = false
  } finally {
    if (pdfLoading.value) {
      pdfLoading.value = false
    }
  }
}

async function renderPage(pageNum: number) {
  if (!pdfDoc.value || !pdfCanvas.value || pageRendering.value) {
    if (pageRendering.value) {
      pageNumPending.value = pageNum
    }
    return
  }

  pageRendering.value = true
  try {
    const page = await pdfDoc.value.getPage(pageNum)
    const scale = 1.2
    const viewport = page.getViewport({ scale })
    const outputScale = window.devicePixelRatio || 1
    const canvas = pdfCanvas.value
    const context = canvas.getContext('2d', { alpha: false })
    if (!context) {
      throw new Error('Failed to get 2D context')
    }

    canvas.width = Math.floor(viewport.width * outputScale)
    canvas.height = Math.floor(viewport.height * outputScale)
    canvas.style.width = `${Math.floor(viewport.width)}px`
    canvas.style.height = `${Math.floor(viewport.height)}px`

    context.clearRect(0, 0, canvas.width, canvas.height)
    context.fillStyle = 'white'
    context.fillRect(0, 0, canvas.width, canvas.height)

    const transform = outputScale !== 1 ? [outputScale, 0, 0, outputScale, 0, 0] : undefined
    renderTask.value = page.render({
      canvasContext: context,
      viewport: viewport,
      transform,
    })
    await renderTask.value.promise

    currentPage.value = pageNum
    pdfError.value = ''
  } catch (error: any) {
    pdfError.value = String(error?.message || error)
  } finally {
    renderTask.value = null
    pageRendering.value = false

    if (pageNumPending.value !== null) {
      const pending = pageNumPending.value
      pageNumPending.value = null
      renderPage(pending)
    }
  }
}

function queueRenderPage(pageNum: number) {
  if (pageRendering.value) {
    pageNumPending.value = pageNum
    return
  }
  renderPage(pageNum)
}

function nextPage() {
  if (currentPage.value < totalPages.value) {
    queueRenderPage(currentPage.value + 1)
  }
}

function prevPage() {
  if (currentPage.value > 1) {
    queueRenderPage(currentPage.value - 1)
  }
}

watch(
  () => props.latex,
  (nextLatex) => {
    code.value = nextLatex
  },
)

watch(
  () => [props.isPdf, props.pdfFile] as const,
  ([isPdf, file]) => {
    if (isPdf && file) {
      loadPdf(file)
      return
    }
    pdfDoc.value = null
    totalPages.value = 0
    currentPage.value = 1
    pdfError.value = ''
  },
  { immediate: true },
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

  // Clean up common LaTeX errors and invalid commands before processing
  src = src.replace(/\\MATH/g, 'MATH') // Remove invalid \MATH command
  src = src.replace(/\\dx/g, 'dx') // Handle invalid \dx
  src = src.replace(/\\frac\{([^}]*)\}\[([^\]]*)\]\[([^\]]*)\]/g, '\\frac{$1}{$2}') // Fix malformed fractions

  // Handle sections and subsections FIRST (including starred versions)
  src = src.replace(/\\section\*?\{([^}]*)\}/g, (_m, title) => 
    insertSafeBlock(`<h2 class="text-2xl font-bold mt-8 mb-4">${escapeHtml(title)}</h2>`)
  )
  src = src.replace(/\\subsection\*?\{([^}]*)\}/g, (_m, title) => 
    insertSafeBlock(`<h3 class="text-xl font-semibold mt-6 mb-3">${escapeHtml(title)}</h3>`)
  )
  src = src.replace(/\\subsubsection\*?\{([^}]*)\}/g, (_m, title) => 
    insertSafeBlock(`<h4 class="text-lg font-medium mt-4 mb-2">${escapeHtml(title)}</h4>`)
  )

  // Handle display math environments BEFORE inline math
  src = src.replace(/\\\[([\s\S]*?)\\\]/g, (_m, tex) => {
    return insertSafeBlock(`<div class="my-6 overflow-x-auto flex justify-center">${safeMathRender(tex, true)}</div>`)
  })
  
  src = src.replace(/\$\$([\s\S]*?)\$\$/g, (_m, tex) => {
    return insertSafeBlock(`<div class="my-6 overflow-x-auto flex justify-center">${safeMathRender(tex, true)}</div>`)
  })

  // Handle align, equation, gather, and other multi-line math environments
  src = src.replace(/\\begin\{(align\*?|equation\*?|gather\*?|multline\*?|split|flalign\*?|eqnarray\*?)\}([\s\S]*?)\\end\{\1\}/g, (_m, env, tex) => {
    let wrapped = tex
    if (env.startsWith('align') || env === 'split' || env.startsWith('flalign') || env.startsWith('eqnarray')) {
      wrapped = `\\begin{aligned}${tex}\\end{aligned}`
    } else if (env.startsWith('gather') || env.startsWith('multline')) {
      wrapped = `\\begin{gathered}${tex}\\end{gathered}`
    } else if (tex.includes('\\\\')) {
      wrapped = `\\begin{gathered}${tex}\\end{gathered}`
    }
    return insertSafeBlock(`<div class="my-6 overflow-x-auto flex justify-center">${safeMathRender(wrapped, true)}</div>`)
  })
  src = src.replace(/\\begin\{(cases|pmatrix|bmatrix|vmatrix|Vmatrix|smallmatrix)\}([\s\S]*?)\\end\{\1\}/g, (_m, env, tex) => {
    const wrapped = `\\begin{${env}}${tex}\\end{${env}}`
    return insertSafeBlock(`<div class="my-6 overflow-x-auto flex justify-center">${safeMathRender(wrapped, true)}</div>`)
  })

  // Handle inline math - CRITICAL: Do this before escaping HTML
  src = src.replace(/\$([^$]+?)\$/g, (_m, tex) => {
    return insertSafeBlock(safeMathRender(tex, false))
  })

  src = src.replace(/\\begin\{itemize\}([\s\S]*?)\\end\{itemize\}/g, (_m, items) => {
    const processedItems = items
      .split('\\item')
      .filter((item: string) => item.trim())
      .map((item: string) => `<li class="ml-6 mb-2">${item.trim()}</li>`)
      .join('')
    return insertSafeBlock(`<ul class="list-disc my-4">${processedItems}</ul>`)
  })
  src = src.replace(/\\begin\{enumerate\}([\s\S]*?)\\end\{enumerate\}/g, (_m, items) => {
    const processedItems = items
      .split('\\item')
      .filter((item: string) => item.trim())
      .map((item: string) => `<li class="ml-6 mb-2">${item.trim()}</li>`)
      .join('')
    return insertSafeBlock(`<ol class="list-decimal my-4">${processedItems}</ol>`)
  })

  // Handle center and quote environments
  src = src.replace(/\\begin\{center\}([\s\S]*?)\\end\{center\}/g, (_m, content) => {
    return insertSafeBlock(`<div class="my-4 text-center">${content.trim()}</div>`)
  })
  src = src.replace(/\\begin\{quote\}([\s\S]*?)\\end\{quote\}/g, (_m, content) => {
    return insertSafeBlock(`<blockquote class="my-4 border-l-4 border-border pl-4 italic text-muted-foreground">${content.trim()}</blockquote>`)
  })

  // Handle common LaTeX text commands BEFORE escaping
  src = src.replace(/\\textbf\{([^}]*)\}/g, (_m, text) => insertSafeBlock(`<strong>${escapeHtml(text)}</strong>`))
  src = src.replace(/\\textit\{([^}]*)\}/g, (_m, text) => insertSafeBlock(`<em>${escapeHtml(text)}</em>`))
  src = src.replace(/\\emph\{([^}]*)\}/g, (_m, text) => insertSafeBlock(`<em>${escapeHtml(text)}</em>`))
  src = src.replace(/\\texttt\{([^}]*)\}/g, (_m, text) => insertSafeBlock(`<code class="font-mono text-sm">${escapeHtml(text)}</code>`))
  src = src.replace(/\\underline\{([^}]*)\}/g, (_m, text) => insertSafeBlock(`<span class="underline">${escapeHtml(text)}</span>`))

  // Clean up remaining LaTeX commands
  src = src.replace(/\\newpage/g, insertSafeBlock('<hr class="my-8 border-border" />'))
  src = src.replace(/\\(vspace|hspace)\{[^}]*\}/g, '')
  src = src.replace(/\\(hline|noindent|clearpage|pagebreak)/g, '')
  src = src.replace(/\\\\(?!\[)/g, insertSafeBlock('<br />'))

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
  
  // Restore safe blocks (loop until stable for nested blocks)
  let previous = ''
  while (src !== previous) {
    previous = src
    src = src.replace(/@@SAFE_BLOCK_(\d+)@@/g, (_m, idx) => safeBlocks[Number(idx)] ?? '')
  }

  return src
})

async function handleCopy() {
  await navigator.clipboard.writeText(code.value)
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 2000)
}

async function handleDownload(format: 'tex' | 'html' | 'pdf') {
  exportNotice.value = null

  if (!canExportRemoteFormats.value && format !== 'tex') {
    exportNotice.value = 'HTML/PDF export requires a saved project.'
    return
  }

  try {
    await exportFile({
      format,
      texFileId: props.texFileId,
      latex: code.value,
      filename: 'monogram-output',
    })
  } catch {
    if (!exportNotice.value) {
      exportNotice.value = exportError.value || 'Export failed'
    }
  }
}

async function handleFormatChange() {
  await handleDownload(selectedFormat.value)
}
</script>

<template>
  <div
    :class="[
      'flex w-full h-[calc(100vh-56px)] max-w-full flex-col gap-4 transition-all duration-700 lg:flex-row px-4 py-4',
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
      <div class="flex items-center justify-between gap-4 border-b border-border px-5 py-3 flex-shrink-0">
        <div class="flex items-center gap-2">
          <svg class="h-4 w-4 text-muted-foreground" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7Z" /><circle cx="12" cy="12" r="3" />
          </svg>
          <span class="text-sm font-medium text-foreground">Original</span>
        </div>
        <div class="flex items-center gap-2 min-w-[140px]">
          <input
            v-model.number="leftZoom"
            type="range"
            min="60"
            max="140"
            step="5"
            class="w-24 accent-primary"
          />
          <span class="w-10 text-right text-xs text-muted-foreground">{{ leftZoom }}%</span>
        </div>
      </div>
      <div class="flex-1 flex flex-col items-center justify-center bg-[hsl(var(--background)/0.5)] p-6 overflow-hidden">
        <!-- PDF viewer -->
        <div
          v-if="props.isPdf"
          class="flex flex-col w-full h-full bg-white rounded-lg border border-border/50"
        >
          <!-- Loading state -->
          <div v-if="pdfLoading" class="flex-1 flex items-center justify-center">
            <div class="text-center">
              <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4" />
              <p class="text-muted-foreground text-sm">Loading PDF...</p>
            </div>
          </div>
          
          <!-- Error state -->
          <div v-else-if="pdfError" class="flex-1 flex items-center justify-center">
            <div class="text-center">
              <svg class="h-16 w-16 text-destructive mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10" /><path d="m15 9-6 6M9 9l6 6" />
              </svg>
              <p class="text-destructive text-sm font-medium">{{ pdfError }}</p>
            </div>
          </div>
          
          <!-- PDF content -->
          <div v-else-if="pdfDoc" class="flex-1 flex flex-col w-full h-full">
            <div class="flex-1 flex items-center justify-center overflow-auto bg-gray-100 p-4">
              <canvas 
                ref="pdfCanvas" 
                id="pdf-canvas"
                class="border-2 border-gray-400 bg-white rounded-lg shadow-2xl"
                :style="{
                  display: 'block',
                  maxWidth: '100%',
                  height: 'auto',
                  minWidth: '300px',
                  minHeight: '400px',
                  transform: `scale(${leftZoom / 100})`,
                  transformOrigin: 'top center',
                }"
              />
            </div>
            <!-- Page navigation -->
            <div class="flex items-center justify-between border-t border-border/50 px-4 py-3 bg-white rounded-b-lg flex-shrink-0">
              <button
                type="button"
                :disabled="currentPage === 1"
                class="px-3 py-1.5 text-sm rounded border border-border disabled:opacity-50 disabled:cursor-not-allowed hover:bg-secondary transition-colors"
                @click="prevPage"
              >
                ← Prev
              </button>
              <span class="text-sm text-muted-foreground">
                Page {{ currentPage }} of {{ totalPages }}
              </span>
              <button
                type="button"
                :disabled="currentPage === totalPages"
                class="px-3 py-1.5 text-sm rounded border border-border disabled:opacity-50 disabled:cursor-not-allowed hover:bg-secondary transition-colors"
                @click="nextPage"
              >
                Next →
              </button>
            </div>
          </div>
        </div>
        <!-- Image preview -->
        <img
          v-else-if="!props.isPdf && props.imageUrl"
          :src="props.imageUrl"
          alt="Original handwritten notes"
          class="max-h-full w-full rounded-lg object-contain"
          :style="{ transform: `scale(${leftZoom / 100})`, transformOrigin: 'top center' }"
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
          <span class="text-base font-medium text-muted-foreground">Document</span>
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
        <div class="flex items-center gap-2 min-w-[140px]">
          <input
            v-model.number="rightZoom"
            type="range"
            min="70"
            max="150"
            step="5"
            class="w-24 accent-primary"
          />
          <span class="w-10 text-right text-xs text-muted-foreground">{{ rightZoom }}%</span>
        </div>
      </div>

      <!-- Content -->
      <div class="flex-1 relative overflow-hidden">
        <textarea
          v-if="activeTab === 'source'"
          v-model="code"
          class="h-full w-full resize-none bg-transparent p-6 font-mono text-sm leading-relaxed text-foreground outline-none placeholder:text-muted-foreground"
          :style="{ fontSize: `${Math.round((14 * rightZoom) / 100)}px` }"
          spellcheck="false"
        />
        <div v-else class="h-full overflow-y-auto bg-white">
          <div
            class="max-w-4xl mx-auto p-8 min-h-full latex-document-preview origin-top"
            :style="{
              transform: `scale(${rightZoom / 100})`,
              transformOrigin: 'top left',
              width: `${100 / (rightZoom / 100)}%`,
            }"
            v-html="renderedPreview"
          />
        </div>
      </div>

      <!-- Action bar -->
      <div class="flex items-center justify-between border-t border-border px-5 py-3 flex-shrink-0">
        <span class="text-xs text-muted-foreground">{{ code.length }} characters</span>
        <div class="flex items-center gap-2">
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
            @click="showDownloadOptions = !showDownloadOptions"
          >
            <svg class="h-3.5 w-3.5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" />
            </svg>
            Download
          </button>
          <div v-if="showDownloadOptions" class="inline-flex items-center gap-2 rounded-md border border-border bg-[hsl(var(--card)/0.92)] px-2 py-1">
            <select
              v-model="selectedFormat"
              class="rounded border border-border bg-transparent px-2 py-1 text-xs text-foreground outline-none"
              @change="handleFormatChange"
            >
              <option
                v-for="option in formatOptions"
                :key="option.value"
                :value="option.value"
                :disabled="!canExportRemoteFormats && option.value !== 'tex'"
              >
                {{ option.label }}
              </option>
            </select>
            <button
              type="button"
              class="rounded border border-border px-2 py-1 text-xs text-foreground transition-colors hover:bg-secondary disabled:opacity-50"
              :disabled="exporting"
              @click="handleDownload(selectedFormat)"
            >
              {{ exporting ? 'Exporting...' : 'Go' }}
            </button>
          </div>
        </div>
      </div>
      <div v-if="exportNotice" class="px-5 pb-3 text-xs text-muted-foreground">
        {{ exportNotice }}
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
