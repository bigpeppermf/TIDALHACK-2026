<script setup lang="ts">
import { computed, ref } from 'vue'

const props = defineProps<{
  modelValue: string
  activeTab: 'preview' | 'source'
  copied: boolean
  renderedPreview: string
  zoom: number
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'update:activeTab': [value: 'preview' | 'source']
  'update:zoom': [value: number]
  copy: []
  download: []
}>()

const lineCount = computed(() => {
  if (!props.modelValue) return 0
  return props.modelValue.split('\n').length
})

const wordCount = computed(() => {
  const trimmed = props.modelValue.trim()
  if (!trimmed) return 0
  return trimmed.split(/\s+/).length
})

const lineNumbers = computed(() => {
  return Array.from({ length: Math.max(1, lineCount.value) }, (_, i) => i + 1).join('\n')
})

const gutterRef = ref<HTMLElement | null>(null)

function updateCode(event: Event) {
  const target = event.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
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
</script>

<template>
  <div class="flex h-full flex-col overflow-hidden bg-card">
    <div class="flex items-center justify-between border-b border-border px-4 py-2">
      <div class="flex items-center gap-3">
        <span class="rounded-md bg-primary/20 px-2 py-1 text-xs text-primary">Project</span>
        <span class="text-sm font-semibold text-foreground">main.tex</span>
        <div class="hidden items-center gap-3 text-xs text-muted-foreground md:flex">
          <span>File</span>
          <span>Edit</span>
          <span>View</span>
          <span>Project</span>
          <span>Tools</span>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button
          type="button"
          class="rounded-md border border-border px-3 py-1 text-xs text-foreground transition-colors hover:bg-secondary"
        >
          Recompile
        </button>
        <button
          type="button"
          class="rounded-md bg-primary px-3 py-1 text-xs text-primary-foreground transition-colors hover:bg-[hsl(var(--primary)/0.9)]"
        >
          Share
        </button>
      </div>
    </div>

    <div class="flex min-h-0 flex-1">
      <aside class="hidden w-56 flex-col border-r border-border bg-[hsl(var(--muted)/0.45)] md:flex">
        <div class="border-b border-border px-3 py-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Files
        </div>
        <div class="space-y-1 p-2 text-sm">
          <button class="flex w-full items-center justify-between rounded-md bg-secondary px-2 py-1.5 text-left text-foreground">
            <span>main.tex</span>
            <span class="text-xs text-muted-foreground">tex</span>
          </button>
          <button class="flex w-full items-center justify-between rounded-md px-2 py-1.5 text-left text-muted-foreground hover:bg-secondary/70">
            <span>references.bib</span>
            <span class="text-xs">bib</span>
          </button>
          <button class="flex w-full items-center justify-between rounded-md px-2 py-1.5 text-left text-muted-foreground hover:bg-secondary/70">
            <span>figures/</span>
            <span class="text-xs">dir</span>
          </button>
        </div>
      </aside>

      <section class="flex min-w-0 flex-1 flex-col">
        <div class="flex items-center justify-between border-b border-border px-3 py-2 text-xs text-muted-foreground">
          <div class="flex items-center gap-2">
            <span class="rounded border border-border bg-background px-2 py-0.5">main.tex</span>
            <span>UTF-8</span>
          </div>
          <div class="flex items-center gap-2 md:hidden">
            <button
              type="button"
              :class="[
                'rounded px-2 py-1',
                activeTab === 'source' ? 'bg-secondary text-foreground' : 'text-muted-foreground',
              ]"
              @click="emit('update:activeTab', 'source')"
            >
              Source
            </button>
            <button
              type="button"
              :class="[
                'rounded px-2 py-1',
                activeTab === 'preview' ? 'bg-secondary text-foreground' : 'text-muted-foreground',
              ]"
              @click="emit('update:activeTab', 'preview')"
            >
              Preview
            </button>
          </div>
        </div>

        <div
          class="relative min-h-0 flex-1"
          :class="activeTab === 'preview' ? 'hidden md:block' : 'block'"
        >
          <div class="absolute inset-0 flex bg-[hsl(var(--background)/0.55)]">
            <pre
              ref="gutterRef"
              class="w-14 overflow-hidden border-r border-border bg-[hsl(var(--muted)/0.35)] px-2 py-4 text-right font-mono text-xs leading-6 text-muted-foreground"
            >{{ lineNumbers }}</pre>
            <textarea
              :value="modelValue"
              class="h-full min-w-0 flex-1 resize-none bg-transparent px-4 py-4 font-mono leading-6 text-foreground outline-none"
              :style="{ fontSize: `${Math.round((14 * zoom) / 100)}px` }"
              spellcheck="false"
              @input="updateCode"
              @scroll="handleEditorScroll"
            />
          </div>
        </div>
      </section>

      <section
        class="w-full min-w-0 border-l border-border md:w-[45%]"
        :class="activeTab === 'source' ? 'hidden md:block' : 'block'"
      >
        <div class="flex items-center justify-between border-b border-border px-3 py-2 text-xs text-muted-foreground">
          <div class="flex items-center gap-2">
            <span>PDF Preview</span>
            <span class="rounded bg-emerald-500/15 px-2 py-0.5 text-emerald-400">Up to date</span>
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

        <div class="h-[calc(100%-37px)] overflow-auto bg-[hsl(var(--muted)/0.35)] p-4">
          <div
            class="latex-document-preview mx-auto min-h-full max-w-3xl shadow-2xl"
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

    <div class="flex items-center justify-between border-t border-border px-4 py-2 text-xs">
      <div class="flex items-center gap-3 text-muted-foreground">
        <span>Ln {{ lineCount }}, Col 1</span>
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
    </div>
  </div>
</template>
