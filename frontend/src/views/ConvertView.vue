<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import UploadZone from '@/components/convert/UploadZone.vue'
import LoadingAnimation from '@/components/convert/LoadingAnimation.vue'
import ResultView from '@/components/convert/ResultView.vue'

type Stage = 'upload' | 'loading' | 'result'

const MOCK_LATEX = `\\documentclass{article}
\\usepackage{amsmath}
\\begin{document}

\\section{Quadratic Formula}

The solutions to the quadratic equation $ax^2 + bx + c = 0$ are given by:

\\[
  x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}
\\]

where $a \\neq 0$.

\\section{Euler's Identity}

\\[
  e^{i\\pi} + 1 = 0
\\]

\\end{document}`

const stage = ref<Stage>('upload')
const imageUrl = ref('')

const allStages: Stage[] = ['upload', 'loading', 'result']

function handleFileAccepted(file: File) {
  imageUrl.value = URL.createObjectURL(file)
  stage.value = 'loading'

  // Simulate API call — replace with real POST /api/convert
  setTimeout(() => {
    stage.value = 'result'
  }, 7500)
}

function handleReset() {
  stage.value = 'upload'
  imageUrl.value = ''
}

function stageIndex(s: Stage): number {
  return allStages.indexOf(s)
}
</script>

<template>
  <div class="relative min-h-screen bg-background">
    <!-- Grid background -->
    <div class="fixed inset-0 bg-grid-pattern opacity-30" />

    <!-- Top bar -->
    <div class="relative z-10 border-b border-border/50 bg-[hsl(var(--background)/0.8)] backdrop-blur-xl">
      <div class="mx-auto flex max-w-7xl items-center gap-4 px-6 py-4">
        <RouterLink
          to="/"
          class="flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m12 19-7-7 7-7M19 12H5" />
          </svg>
          Back
        </RouterLink>
        <div class="h-4 w-px bg-[hsl(var(--border))]" />
        <div class="flex items-center gap-2">
          <div class="flex h-6 w-6 items-center justify-center rounded-md bg-primary">
            <span class="font-mono text-[10px] font-bold text-primary-foreground">S</span>
          </div>
          <span class="text-sm font-medium text-foreground">ScribeTeX</span>
        </div>

        <!-- Step indicator -->
        <div class="ml-auto flex items-center gap-2">
          <template v-for="(s, i) in allStages" :key="s">
            <div
              :class="[
                'flex h-6 w-6 items-center justify-center rounded-full text-xs font-medium transition-all',
                stage === s
                  ? 'bg-primary text-primary-foreground'
                  : stageIndex(stage) > i
                    ? 'bg-primary/20 text-primary'
                    : 'bg-secondary text-muted-foreground',
              ]"
            >
              {{ i + 1 }}
            </div>
            <div
              v-if="i < 2"
              :class="[
                'h-px w-6 transition-colors',
                stageIndex(stage) > i ? 'bg-[hsl(var(--primary)/0.4)]' : 'bg-[hsl(var(--border))]',
              ]"
            />
          </template>
        </div>
      </div>
    </div>

    <!-- Content area -->
    <div class="relative z-10 flex min-h-[calc(100vh-65px)] flex-col items-center justify-center px-6 py-12">
      <!-- Upload -->
      <div v-if="stage === 'upload'" class="w-full max-w-2xl">
        <div class="mb-8 text-center">
          <h1 class="mb-2 text-3xl font-bold text-foreground">Convert Your Notes</h1>
          <p class="text-muted-foreground">
            Upload a photo of your handwritten notes to get started.
          </p>
        </div>
        <UploadZone @file-accepted="handleFileAccepted" />
      </div>

      <!-- Loading -->
      <div v-if="stage === 'loading'" class="w-full max-w-md">
        <LoadingAnimation />
      </div>

      <!-- Result -->
      <ResultView
        v-if="stage === 'result'"
        :image-url="imageUrl"
        :latex="MOCK_LATEX"
        @reset="handleReset"
      />
    </div>
  </div>
</template>
