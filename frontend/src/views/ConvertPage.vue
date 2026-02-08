<script setup lang="ts">
import { onUnmounted, ref } from 'vue'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import UploadZone from '@/components/convert/UploadZone.vue'
import LoadingAnimation from '@/components/convert/LoadingAnimation.vue'
import ResultView from '@/components/convert/ResultView.vue'
import { useConvert } from '@/composables/useConvert'
import { useProjects } from '@/composables/useProjects'

type Stage = 'upload' | 'loading' | 'result' | 'error'

const { error: convertError, convert, reset: resetConvert } = useConvert()
const { addConvertedProject } = useProjects()

const stage = ref<Stage>('upload')
const imageUrl = ref('')
const isPdf = ref(false)
const latexOutput = ref('')
const uploadedFile = ref<File | null>(null)

const allStages: ('upload' | 'loading' | 'result')[] = ['upload', 'loading', 'result']

function revokePreviewUrl() {
  if (imageUrl.value) {
    URL.revokeObjectURL(imageUrl.value)
    imageUrl.value = ''
  }
}

async function handleFileAccepted(file: File) {
  isPdf.value = file.type === 'application/pdf'
  uploadedFile.value = file
  revokePreviewUrl()
  imageUrl.value = isPdf.value ? '' : URL.createObjectURL(file)
  stage.value = 'loading'

  try {
    const res = await convert(file)
    latexOutput.value = res.latex
    addConvertedProject(file.name)
    stage.value = 'result'
  } catch {
    stage.value = 'error'
  }
}

function handleReset() {
  revokePreviewUrl()
  stage.value = 'upload'
  isPdf.value = false
  latexOutput.value = ''
  uploadedFile.value = null
  resetConvert()
}

function stageIndex(s: string): number {
  return allStages.indexOf(s as 'upload' | 'loading' | 'result')
}

onUnmounted(() => {
  revokePreviewUrl()
})
</script>

<template>
  <div class="relative min-h-screen bg-background">
    <AppNavbar />

    <!-- Grid background -->
    <div class="fixed inset-0 bg-grid-pattern opacity-30" />

    <!-- Step indicator bar -->
    <div class="relative z-10 border-b border-border/50 bg-[hsl(var(--background)/0.8)] backdrop-blur-xl">
      <div class="mx-auto flex max-w-7xl items-center justify-center gap-2 px-6 py-3">
        <template v-for="(s, i) in allStages" :key="s">
          <div class="flex items-center gap-2">
            <div
              :class="[
                'flex h-7 w-7 items-center justify-center rounded-full text-xs font-medium transition-all',
                stage === s
                  ? 'bg-primary text-primary-foreground'
                  : stageIndex(stage) > i
                    ? 'bg-primary/20 text-primary'
                    : 'bg-secondary text-muted-foreground',
              ]"
            >
              {{ i + 1 }}
            </div>
            <span
              :class="[
                'text-xs font-medium transition-colors',
                stage === s ? 'text-foreground' : 'text-muted-foreground',
              ]"
            >
              {{ s === 'upload' ? 'Upload' : s === 'loading' ? 'Processing' : 'Result' }}
            </span>
          </div>
          <div
            v-if="i < 2"
            :class="[
              'h-px w-8 transition-colors',
              stageIndex(stage) > i ? 'bg-[hsl(var(--primary)/0.4)]' : 'bg-[hsl(var(--border))]',
            ]"
          />
        </template>
      </div>
    </div>

    <!-- Content area -->
    <div class="relative z-10 flex min-h-[calc(100vh-110px)] flex-col items-center justify-center px-6 py-12">
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

      <!-- Error -->
      <div v-if="stage === 'error'" class="w-full max-w-md text-center">
        <div class="mb-6 flex h-16 w-16 mx-auto items-center justify-center rounded-2xl bg-destructive/10 text-destructive">
          <svg class="h-7 w-7" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10" /><path d="m15 9-6 6M9 9l6 6" />
          </svg>
        </div>
        <h2 class="mb-2 text-xl font-semibold text-foreground">Conversion Failed</h2>
        <p class="mb-6 text-sm text-muted-foreground">{{ convertError || 'Something went wrong. Please try again.' }}</p>
        <button
          type="button"
          class="inline-flex items-center gap-2 rounded-md bg-primary px-6 py-3 text-sm font-medium text-primary-foreground transition-colors hover:bg-[hsl(var(--primary)/0.9)]"
          @click="handleReset"
        >
          Try Again
        </button>
      </div>

      <!-- Result -->
      <ResultView
        v-if="stage === 'result'"
        :image-url="imageUrl"
        :is-pdf="isPdf"
        :pdf-file="uploadedFile"
        :latex="latexOutput"
        @reset="handleReset"
      />
    </div>
  </div>
</template>
