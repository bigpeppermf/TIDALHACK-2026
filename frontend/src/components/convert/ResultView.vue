<script setup lang="ts">
import { ref, onMounted } from 'vue'

const props = defineProps<{
  imageUrl: string
  latex: string
}>()

const emit = defineEmits<{
  reset: []
}>()

const code = ref(props.latex)
const copied = ref(false)
const activeTab = ref<'preview' | 'source'>('source')
const slideIn = ref(false)

onMounted(() => {
  setTimeout(() => {
    slideIn.value = true
  }, 50)
})

async function handleCopy() {
  await navigator.clipboard.writeText(code.value)
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 2000)
}

function handleDownload() {
  const blob = new Blob([code.value], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'scribetex-output.tex'
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div
    :class="[
      'flex w-full max-w-6xl flex-col gap-4 transition-all duration-700 lg:flex-row',
      slideIn ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0',
    ]"
  >
    <!-- Left panel: Original Image -->
    <div
      :class="[
        'flex-1 overflow-hidden rounded-2xl border border-border bg-card transition-all duration-700 delay-100',
        slideIn ? 'translate-x-0 opacity-100' : '-translate-x-12 opacity-0',
      ]"
    >
      <div class="flex items-center gap-2 border-b border-border px-5 py-3">
        <svg class="h-4 w-4 text-muted-foreground" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7Z" /><circle cx="12" cy="12" r="3" />
        </svg>
        <span class="text-sm font-medium text-foreground">Original</span>
      </div>
      <div class="flex items-center justify-center bg-[hsl(var(--background)/0.5)] p-6">
        <img
          :src="props.imageUrl"
          alt="Original handwritten notes"
          class="max-h-[400px] w-full rounded-lg object-contain"
        />
      </div>
    </div>

    <!-- Right panel: LaTeX -->
    <div
      :class="[
        'flex-1 overflow-hidden rounded-2xl border border-border bg-card transition-all duration-700 delay-200',
        slideIn ? 'translate-x-0 opacity-100' : 'translate-x-12 opacity-0',
      ]"
    >
      <!-- Tab header -->
      <div class="flex items-center justify-between border-b border-border px-5 py-3">
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
      <div class="relative min-h-[300px]">
        <textarea
          v-if="activeTab === 'source'"
          v-model="code"
          class="h-full min-h-[300px] w-full resize-none bg-transparent p-5 font-mono text-sm leading-relaxed text-foreground outline-none placeholder:text-muted-foreground"
          spellcheck="false"
        />
        <div v-else class="p-5">
          <div class="rounded-lg bg-secondary/50 p-6">
            <p class="font-mono text-sm leading-relaxed text-muted-foreground">
              [KaTeX preview will render here — connect KaTeX library]
            </p>
            <div class="mt-4 rounded-md border border-border bg-[hsl(var(--background)/0.5)] p-4">
              <pre class="whitespace-pre-wrap font-mono text-xs text-foreground">{{ code }}</pre>
            </div>
          </div>
        </div>
      </div>

      <!-- Action bar -->
      <div class="flex items-center justify-between border-t border-border px-5 py-3">
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
