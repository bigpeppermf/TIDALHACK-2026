<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, shallowRef, watch } from 'vue'
import { Codemirror } from 'vue-codemirror'
import { autocompletion, closeBrackets, closeBracketsKeymap, completionKeymap } from '@codemirror/autocomplete'
import { defaultKeymap, history, historyKeymap, indentWithTab } from '@codemirror/commands'
import { bracketMatching, defaultHighlightStyle, foldKeymap, indentOnInput, StreamLanguage, syntaxHighlighting } from '@codemirror/language'
import { searchKeymap } from '@codemirror/search'
import { EditorState } from '@codemirror/state'
import { crosshairCursor, drawSelection, dropCursor, EditorView, highlightActiveLine, highlightActiveLineGutter, keymap, lineNumbers, rectangularSelection } from '@codemirror/view'
import { stex } from '@codemirror/legacy-modes/mode/stex'
import * as PDFJS from 'pdfjs-dist'

PDFJS.GlobalWorkerOptions.workerSrc = '/pdf.worker.mjs'

type EditorFileItem = {
  path: string
  name: string
  kind: 'tex' | 'dir' | 'bib' | 'image' | 'asset'
  editable: boolean
  active?: boolean
}

const props = defineProps<{
  modelValue: string
  activeTab: 'preview' | 'source'
  copied: boolean
  renderedPreview: string
  zoom: number
  projectName?: string
  sourceFilename?: string
  files?: EditorFileItem[]
  readOnly?: boolean
  pdfData?: Uint8Array | null
  pdfError?: string
  saveStatus?: 'idle' | 'saving' | 'saved' | 'error'
  saveStatusLabel?: string
  compileStatus?: 'idle' | 'dirty' | 'compiling' | 'compiled' | 'error'
  compileStatusLabel?: string
  shareLabel?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'update:activeTab': [value: 'preview' | 'source']
  'update:zoom': [value: number]
  'select-file': [path: string]
  copy: []
  download: []
  recompile: []
  share: []
}>()

const codeEditorView = shallowRef<EditorView | null>(null)
const cursorLine = ref(1)
const cursorColumn = ref(1)

const pdfDoc = shallowRef<any>(null)
const pdfCanvas = ref<HTMLCanvasElement | null>(null)
const pdfLoading = ref(false)
const pageRendering = ref(false)
const pageNumPending = ref<number | null>(null)
const renderTask = shallowRef<any>(null)
const currentPage = ref(1)
const totalPages = ref(0)
const pdfViewerError = ref('')

const wordCount = computed(() => {
  const trimmed = props.modelValue.trim()
  return trimmed ? trimmed.split(/\s+/).length : 0
})

const hasRealFiles = computed(() => Array.isArray(props.files) && props.files.length > 0)

const hasCompiledPdf = computed(() => Boolean(pdfDoc.value && totalPages.value > 0))

const compileBadgeClass = computed(() => {
  if (props.compileStatus === 'compiled') return 'bg-emerald-500/15 text-emerald-400'
  if (props.compileStatus === 'compiling') return 'bg-amber-500/15 text-amber-300'
  if (props.compileStatus === 'dirty') return 'bg-yellow-500/15 text-yellow-300'
  if (props.compileStatus === 'error') return 'bg-destructive/15 text-destructive'
  return 'bg-secondary text-muted-foreground'
})

const saveIndicatorClass = computed(() => {
  if (props.saveStatus === 'saved') return 'text-emerald-400'
  if (props.saveStatus === 'saving') return 'text-amber-300'
  if (props.saveStatus === 'error') return 'text-destructive'
  return 'text-muted-foreground'
})

function setActiveTab(tab: 'preview' | 'source') {
  emit('update:activeTab', tab)
}

const editorValue = computed({
  get: () => props.modelValue,
  set: (value: string) => emit('update:modelValue', value),
})

const editorExtensions = computed(() => [
  lineNumbers(),
  highlightActiveLineGutter(),
  history(),
  drawSelection(),
  dropCursor(),
  EditorState.allowMultipleSelections.of(true),
  indentOnInput(),
  bracketMatching(),
  closeBrackets(),
  autocompletion(),
  rectangularSelection(),
  crosshairCursor(),
  highlightActiveLine(),
  syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
  StreamLanguage.define(stex),
  keymap.of([
    indentWithTab,
    ...closeBracketsKeymap,
    ...defaultKeymap,
    ...historyKeymap,
    ...completionKeymap,
    ...searchKeymap,
    ...foldKeymap,
  ]),
  EditorState.readOnly.of(Boolean(props.readOnly)),
  EditorView.editable.of(!props.readOnly),
])

const editorStyle = computed(() => ({
  fontSize: `${Math.round((14 * props.zoom) / 100)}px`,
}))

function syncCursorFromView(view: EditorView) {
  const head = view.state.selection.main.head
  const line = view.state.doc.lineAt(head)
  cursorLine.value = line.number
  cursorColumn.value = head - line.from + 1
}

function handleEditorReady(payload: { view: EditorView }) {
  codeEditorView.value = payload.view
  syncCursorFromView(payload.view)
}

function handleEditorUpdate(update: { view: EditorView; selectionSet: boolean }) {
  if (update.selectionSet) {
    syncCursorFromView(update.view)
  }
}

function updateZoom(event: Event) {
  const target = event.target as HTMLInputElement
  emit('update:zoom', Number(target.value))
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
    const viewport = page.getViewport({ scale: 1.15 })
    const outputScale = window.devicePixelRatio || 1
    const canvas = pdfCanvas.value
    const context = canvas.getContext('2d', { alpha: false })

    if (!context) {
      throw new Error('Canvas 2D context unavailable')
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
      viewport,
      transform,
    })

    await renderTask.value.promise
    currentPage.value = pageNum
  } finally {
    renderTask.value = null
    pageRendering.value = false

    if (pageNumPending.value !== null) {
      const pending = pageNumPending.value
      pageNumPending.value = null
      void renderPage(pending)
    }
  }
}

function queueRenderPage(pageNum: number) {
  if (pageRendering.value) {
    pageNumPending.value = pageNum
    return
  }
  void renderPage(pageNum)
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

function resetPdfState() {
  if (renderTask.value) {
    try {
      renderTask.value.cancel()
    } catch {
      // no-op
    }
    renderTask.value = null
  }

  if (pdfDoc.value && typeof pdfDoc.value.destroy === 'function') {
    void pdfDoc.value.destroy()
  }

  pdfDoc.value = null
  currentPage.value = 1
  totalPages.value = 0
  pageNumPending.value = null
  pageRendering.value = false
}

async function loadPdfFromBytes(data: Uint8Array) {
  pdfLoading.value = true
  pdfViewerError.value = ''

  resetPdfState()

  try {
    const loadingTask = PDFJS.getDocument({ data })
    const loadedDoc = await loadingTask.promise
    pdfDoc.value = loadedDoc
    totalPages.value = loadedDoc.numPages
    currentPage.value = 1

    await nextTick()
    queueRenderPage(1)
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error)
    pdfViewerError.value = `Unable to render compiled PDF: ${message}`
    resetPdfState()
  } finally {
    pdfLoading.value = false
  }
}

watch(
  () => props.pdfData,
  (nextPdfData) => {
    if (nextPdfData && nextPdfData.length > 0) {
      void loadPdfFromBytes(nextPdfData)
      return
    }

    resetPdfState()
  },
  { immediate: true },
)

watch(
  () => props.pdfError,
  (nextError) => {
    if (nextError) {
      pdfViewerError.value = nextError
    }
  },
)

onBeforeUnmount(() => {
  resetPdfState()
})
</script>

<template>
  <div class="flex h-full min-h-0 flex-col overflow-hidden bg-card">
    <header class="flex items-center justify-between gap-3 border-b border-border bg-[hsl(var(--card)/0.95)] px-3 py-2 md:px-4">
      <div class="flex min-w-0 items-center gap-3">
        <span class="rounded-md border border-border bg-secondary px-2 py-1 text-[11px] font-semibold uppercase tracking-wide text-primary">
          Project
        </span>
        <span class="truncate text-sm font-semibold text-foreground">{{ props.projectName || 'tidalhack-paper' }}</span>
        <nav class="hidden items-center gap-3 text-xs text-muted-foreground md:flex">
          <button type="button" class="hover:text-foreground">File</button>
          <button type="button" class="hover:text-foreground">Edit</button>
          <button type="button" class="hover:text-foreground">View</button>
          <button type="button" class="hover:text-foreground">Project</button>
          <button type="button" class="hover:text-foreground">Tools</button>
        </nav>
      </div>
      <div class="flex items-center gap-2">
        <button
          type="button"
          class="rounded-md border border-border bg-secondary px-3 py-1.5 text-xs text-foreground transition-colors hover:bg-[hsl(var(--muted)/0.7)]"
          :disabled="props.compileStatus === 'compiling'"
          @click="emit('recompile')"
        >
          {{ props.compileStatus === 'compiling' ? 'Compiling...' : 'Recompile' }}
        </button>
        <button
          type="button"
          class="rounded-md bg-primary px-3 py-1.5 text-xs text-primary-foreground transition-opacity hover:opacity-90"
          @click="emit('share')"
        >
          {{ props.shareLabel || 'Share' }}
        </button>
      </div>
    </header>

    <div class="flex min-h-0 flex-1 overflow-hidden">
      <aside class="hidden w-60 flex-col border-r border-border bg-[hsl(var(--muted)/0.3)] md:flex">
        <div class="border-b border-border px-3 py-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Files
        </div>
        <div v-if="hasRealFiles" class="space-y-1 p-2 text-sm">
          <button
            v-for="file in props.files"
            :key="file.path"
            type="button"
            :class="[
              'flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left',
              file.active ? 'bg-secondary text-foreground' : 'text-muted-foreground hover:bg-secondary/70',
            ]"
            @click="emit('select-file', file.path)"
          >
            <span class="text-xs" :class="file.active ? 'text-primary' : 'text-muted-foreground'">{{ file.active ? '●' : '•' }}</span>
            <span class="flex-1 truncate">{{ file.name }}</span>
            <span class="text-[11px] uppercase">{{ file.kind }}</span>
          </button>
        </div>
        <div v-else class="space-y-1 p-2 text-sm">
          <button class="flex w-full items-center gap-2 rounded-md bg-secondary px-2 py-1.5 text-left text-foreground">
            <span class="text-xs text-primary">●</span>
            <span class="flex-1">main.tex</span>
            <span class="text-[11px] text-muted-foreground">tex</span>
          </button>
          <button class="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-muted-foreground hover:bg-secondary/70">
            <span class="text-xs">▸</span>
            <span class="flex-1">sections/</span>
            <span class="text-[11px]">dir</span>
          </button>
          <button class="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-muted-foreground hover:bg-secondary/70">
            <span class="text-xs">•</span>
            <span class="flex-1">references.bib</span>
            <span class="text-[11px]">bib</span>
          </button>
          <button class="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-muted-foreground hover:bg-secondary/70">
            <span class="text-xs">▸</span>
            <span class="flex-1">figures/</span>
            <span class="text-[11px]">dir</span>
          </button>
        </div>
      </aside>

      <div class="flex min-w-0 flex-1 overflow-hidden">
        <section class="flex min-w-0 flex-1 flex-col border-r border-border">
          <div class="flex items-center justify-between border-b border-border px-3 py-2 text-xs text-muted-foreground">
            <div class="flex items-center gap-2">
              <span class="rounded border border-border bg-[hsl(var(--background)/0.8)] px-2 py-0.5 text-foreground">
                {{ props.sourceFilename || 'main.tex' }}
              </span>
              <span>UTF-8</span>
              <span v-if="props.readOnly" class="rounded border border-border px-1.5 py-0.5 text-[10px] uppercase tracking-wide">Read only</span>
              <span :class="saveIndicatorClass">{{ props.saveStatusLabel || 'Auto Save' }}</span>
            </div>
            <div class="flex items-center gap-2 md:hidden">
              <button
                type="button"
                :class="[
                  'rounded px-2 py-1',
                  activeTab === 'source' ? 'bg-secondary text-foreground' : 'text-muted-foreground',
                ]"
                @click="setActiveTab('source')"
              >
                Source
              </button>
              <button
                type="button"
                :class="[
                  'rounded px-2 py-1',
                  activeTab === 'preview' ? 'bg-secondary text-foreground' : 'text-muted-foreground',
                ]"
                @click="setActiveTab('preview')"
              >
                Preview
              </button>
            </div>
          </div>

          <div class="relative min-h-0 flex-1" :class="activeTab === 'preview' ? 'hidden md:block' : 'block'">
            <div class="absolute inset-0 bg-[hsl(var(--background)/0.55)]">
              <Codemirror
                v-model="editorValue"
                class="latex-codemirror h-full min-w-0"
                :class="props.readOnly ? 'opacity-75' : ''"
                :style="editorStyle"
                :extensions="editorExtensions"
                :disabled="props.readOnly"
                :indent-with-tab="true"
                :tab-size="2"
                :autofocus="false"
                :auto-destroy="true"
                placeholder="Type LaTeX..."
                @ready="handleEditorReady"
                @update="handleEditorUpdate"
              />
            </div>
          </div>
        </section>

        <section
          class="w-full min-w-0 bg-[hsl(var(--muted)/0.28)] md:w-[46%]"
          :class="activeTab === 'source' ? 'hidden md:block' : 'block'"
        >
          <div class="flex items-center justify-between border-b border-border px-3 py-2 text-xs text-muted-foreground">
            <div class="flex items-center gap-2">
              <span>PDF Preview</span>
              <span class="rounded px-2 py-0.5" :class="compileBadgeClass">{{ props.compileStatusLabel || 'Ready' }}</span>
            </div>
            <div class="flex items-center gap-2">
              <input
                :value="zoom"
                type="range"
                min="70"
                max="150"
                step="5"
                class="w-20 accent-primary"
                @input="updateZoom"
              />
              <span class="w-10 text-right">{{ zoom }}%</span>
            </div>
          </div>

          <div class="h-[calc(100%-37px)] overflow-auto p-4">
            <div v-if="pdfLoading" class="mx-auto flex min-h-[12rem] max-w-3xl items-center justify-center rounded-sm border border-border bg-[hsl(var(--card)/0.9)] text-sm text-muted-foreground">
              Rendering PDF...
            </div>

            <div v-else-if="hasCompiledPdf" class="mx-auto max-w-3xl space-y-3">
              <div class="flex items-center justify-between rounded-sm border border-border bg-[hsl(var(--card)/0.9)] px-3 py-2 text-xs text-muted-foreground">
                <button type="button" class="rounded border border-border px-2 py-1 text-foreground disabled:opacity-50" :disabled="currentPage <= 1" @click="prevPage">
                  Prev
                </button>
                <span>Page {{ currentPage }} / {{ totalPages }}</span>
                <button
                  type="button"
                  class="rounded border border-border px-2 py-1 text-foreground disabled:opacity-50"
                  :disabled="currentPage >= totalPages"
                  @click="nextPage"
                >
                  Next
                </button>
              </div>

              <div class="overflow-auto rounded-sm border border-black/5 bg-white p-3 shadow-2xl">
                <div
                  class="mx-auto"
                  :style="{
                    transform: `scale(${zoom / 100})`,
                    transformOrigin: 'top center',
                    width: `${100 / (zoom / 100)}%`,
                  }"
                >
                  <canvas ref="pdfCanvas" class="mx-auto block" />
                </div>
              </div>
            </div>

            <div v-else class="space-y-3">
              <div
                v-if="pdfViewerError"
                class="mx-auto max-w-3xl rounded-sm border border-destructive/30 bg-destructive/10 px-3 py-2 text-xs text-destructive"
              >
                {{ pdfViewerError }}
              </div>

              <div
                class="latex-document-preview mx-auto min-h-full max-w-3xl rounded-sm border border-black/5 shadow-2xl"
                :style="{
                  transform: `scale(${zoom / 100})`,
                  transformOrigin: 'top center',
                  width: `${100 / (zoom / 100)}%`,
                }"
                v-html="renderedPreview"
              />
            </div>
          </div>
        </section>
      </div>
    </div>

    <footer class="flex items-center justify-between border-t border-border bg-[hsl(var(--card)/0.96)] px-3 py-2 text-xs md:px-4">
      <div class="flex items-center gap-3 text-muted-foreground">
        <span>Ln {{ cursorLine }}, Col {{ cursorColumn }}</span>
        <span>{{ wordCount }} words</span>
        <span>{{ modelValue.length }} chars</span>
      </div>
      <div class="flex items-center gap-2">
        <button
          type="button"
          class="rounded-md border border-border px-3 py-1 text-foreground transition-colors hover:bg-secondary"
          @click="emit('copy')"
        >
          {{ copied ? 'Copied' : 'Copy' }}
        </button>
        <button
          type="button"
          class="rounded-md border border-border px-3 py-1 text-foreground transition-colors hover:bg-secondary"
          @click="emit('download')"
        >
          Download .tex
        </button>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.latex-codemirror :deep(.cm-editor) {
  height: 100%;
  background: transparent;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
}

.latex-codemirror :deep(.cm-scroller) {
  min-height: 100%;
  line-height: 1.5;
}

.latex-codemirror :deep(.cm-content) {
  padding: 1rem;
}

.latex-codemirror :deep(.cm-gutters) {
  border-right: 1px solid hsl(var(--border));
  background: hsl(var(--muted) / 0.35);
}
</style>
