<script setup lang="ts">
import { computed, ref } from 'vue'

type EditorFileItem = {
  name: string
  kind: 'tex' | 'dir' | 'bib' | 'md'
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
  copy: []
  download: []
  recompile: []
  share: []
}>()

const editorRef = ref<HTMLTextAreaElement | null>(null)
const gutterRef = ref<HTMLElement | null>(null)
const cursorLine = ref(1)
const cursorColumn = ref(1)

const lineCount = computed(() => Math.max(1, props.modelValue.split('\n').length))

const wordCount = computed(() => {
  const trimmed = props.modelValue.trim()
  return trimmed ? trimmed.split(/\s+/).length : 0
})

const lineNumbers = computed(() => {
  return Array.from({ length: lineCount.value }, (_, index) => index + 1).join('\n')
})

const hasRealFiles = computed(() => Array.isArray(props.files) && props.files.length > 0)

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

function updateCode(event: Event) {
  const target = event.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
  updateCursorPosition(target)
}

function updateZoom(event: Event) {
  const target = event.target as HTMLInputElement
  emit('update:zoom', Number(target.value))
}

function handleEditorScroll(event: Event) {
  const target = event.target as HTMLTextAreaElement
  if (gutterRef.value) {
    gutterRef.value.scrollTop = target.scrollTop
  }
}

function updateCursorPosition(target?: HTMLTextAreaElement) {
  const editor = target ?? editorRef.value
  if (!editor) return
  const cursorIndex = editor.selectionStart
  const contentBeforeCursor = editor.value.slice(0, cursorIndex)
  const rows = contentBeforeCursor.split('\n')
  cursorLine.value = rows.length
  cursorColumn.value = (rows[rows.length - 1] ?? '').length + 1
}
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
            :key="file.name"
            type="button"
            :class="[
              'flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left',
              file.active ? 'bg-secondary text-foreground' : 'text-muted-foreground hover:bg-secondary/70',
            ]"
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
            <div class="absolute inset-0 flex bg-[hsl(var(--background)/0.55)]">
              <pre
                ref="gutterRef"
                class="w-14 overflow-hidden border-r border-border bg-[hsl(var(--muted)/0.35)] px-2 py-4 text-right font-mono text-xs leading-6 text-muted-foreground"
              >{{ lineNumbers }}</pre>
              <textarea
                ref="editorRef"
                :value="modelValue"
                class="h-full min-w-0 flex-1 resize-none bg-transparent px-4 py-4 font-mono leading-6 text-foreground outline-none"
                :style="{ fontSize: `${Math.round((14 * zoom) / 100)}px` }"
                spellcheck="false"
                @input="updateCode"
                @scroll="handleEditorScroll"
                @click="updateCursorPosition()"
                @keyup="updateCursorPosition()"
                @select="updateCursorPosition()"
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
