<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'

const words = ['Notes', 'Equations', 'Diagrams', 'Formulas']
const currentWord = ref(0)
const visible = ref(true)

let interval: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  interval = setInterval(() => {
    visible.value = false
    setTimeout(() => {
      currentWord.value = (currentWord.value + 1) % words.length
      visible.value = true
    }, 400)
  }, 3000)
})

onUnmounted(() => {
  if (interval) clearInterval(interval)
})

const stats = [
  { value: '99%', label: 'Accuracy' },
  { value: '<3s', label: 'Conversion' },
  { value: '10k+', label: 'Equations' },
]
</script>

<template>
  <section class="relative flex min-h-screen items-center justify-center overflow-hidden">
    <!-- Grid background -->
    <div class="absolute inset-0 bg-grid-pattern opacity-40" />

    <!-- Radial glow -->
    <div
      class="absolute left-1/2 top-1/4 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/5 blur-3xl"
    />

    <!-- Glow line -->
    <div class="absolute top-0 left-0 right-0 h-px glow-line" />

    <div class="relative z-10 mx-auto flex max-w-4xl flex-col items-center px-6 text-center">
      <!-- Badge -->
      <div
        class="mb-8 inline-flex items-center gap-2 rounded-full border border-border bg-secondary/50 px-4 py-1.5 text-sm text-muted-foreground backdrop-blur-sm"
      >
        <svg
          class="h-3.5 w-3.5 text-primary"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path
            d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"
          />
        </svg>
        <span>AI-Powered LaTeX Conversion</span>
      </div>

      <!-- Heading -->
      <h1
        class="mb-6 text-5xl font-bold leading-tight tracking-tight text-foreground md:text-7xl"
        style="text-wrap: balance"
      >
        Handwritten
        <span
          class="inline-block text-primary transition-all duration-[400ms]"
          :class="visible ? 'translate-y-0 opacity-100' : 'translate-y-2 opacity-0'"
        >
          {{ words[currentWord] }}
        </span>
        <br />
        to Perfect LaTeX
      </h1>

      <!-- Subtitle -->
      <p
        class="mb-10 max-w-2xl text-lg text-muted-foreground md:text-xl"
        style="text-wrap: pretty"
      >
        Upload a photo of your handwritten notes, equations, or formulas.
        ScribeTeX converts them into clean, editable LaTeX in seconds.
      </p>

      <!-- CTA buttons -->
      <div class="flex flex-col items-center gap-4 sm:flex-row">
        <RouterLink
          to="/convert"
          class="inline-flex items-center gap-2 rounded-md bg-primary px-6 py-3 text-sm font-medium text-primary-foreground transition-colors hover:bg-[hsl(var(--primary)/0.9)]"
        >
          Start Converting
          <svg
            class="h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </RouterLink>
        <a
          href="#how-it-works"
          class="inline-flex items-center gap-2 rounded-md border border-border bg-transparent px-6 py-3 text-sm font-medium text-foreground transition-colors hover:bg-secondary"
        >
          See How It Works
        </a>
      </div>

      <!-- Stats row -->
      <div class="mt-16 grid grid-cols-3 gap-8 border-t border-border/50 pt-8">
        <div
          v-for="stat in stats"
          :key="stat.label"
          class="flex flex-col items-center gap-1"
        >
          <span class="text-2xl font-bold text-foreground md:text-3xl">{{ stat.value }}</span>
          <span class="text-xs text-muted-foreground md:text-sm">{{ stat.label }}</span>
        </div>
      </div>
    </div>
  </section>
</template>
