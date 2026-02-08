<script setup lang="ts">
import { useAuth } from '@clerk/vue'
import { onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import UploadZone from '@/components/convert/UploadZone.vue'
import LoadingAnimation from '@/components/convert/LoadingAnimation.vue'
import ResultView from '@/components/convert/ResultView.vue'
import { useConvert } from '@/composables/useConvert'
import { useProjects } from '@/composables/useProjects'

type Stage = 'upload' | 'loading' | 'result' | 'error'

const { userId } = useAuth()
const { error: convertError, convert, reset: resetConvert } = useConvert()
const { addConvertedProject } = useProjects(userId)
const router = useRouter()

const stage = ref<Stage>('upload')
const stageError = ref<string | null>(null)
const imageUrl = ref('')
const isPdf = ref(false)
const latexOutput = ref('')
const uploadedFile = ref<File | null>(null)
const latestProjectId = ref<string | null>(null)
const remoteSaveWarning = ref('')
const remoteSaveBusy = ref(false)
const PENDING_EDITOR_DRAFT_KEY = 'monogram-editor-pending-draft'
const EDITOR_LAST_TARGET_KEY = 'monogram-editor-last-target'

const allStages: ('upload' | 'loading' | 'result')[] = ['upload', 'loading', 'result']

function revokePreviewUrl() {
  if (imageUrl.value) {
    URL.revokeObjectURL(imageUrl.value)
    imageUrl.value = ''
  }
}

async function handleFileAccepted(file: File) {
  stageError.value = null
  isPdf.value = file.type === 'application/pdf'
  uploadedFile.value = file
  revokePreviewUrl()
  imageUrl.value = isPdf.value ? '' : URL.createObjectURL(file)
  stage.value = 'loading'

  try {
    const res = await convert(file)
    latexOutput.value = res.latex

    try {
      const project = await addConvertedProject({
        name: file.name,
        latex: res.latex,
        sourceFilename: file.name,
        sourceKind: isPdf.value ? 'pdf' : 'image',
        ownerId: userId.value ?? null,
      })
      latestProjectId.value = project.id
      if (typeof window !== 'undefined') {
        sessionStorage.setItem(EDITOR_LAST_TARGET_KEY, JSON.stringify({ projectId: project.id }))
      }
      remoteSaveWarning.value = project.id.startsWith('local-')
        ? 'Cloud save failed. Retry save to enable PDF compile in editor.'
        : ''
    } catch {
      latestProjectId.value = null
      if (typeof window !== 'undefined') {
        sessionStorage.setItem(EDITOR_LAST_TARGET_KEY, JSON.stringify({
          draft: {
            latex: res.latex,
            name: file.name || 'Untitled conversion',
            sourceFilename: file.name || 'main.tex',
          },
        }))
      }
      remoteSaveWarning.value = 'Converted successfully, but cloud save failed. Sign in again to save and export HTML/PDF from editor.'
    }

    stage.value = 'result'
  } catch (error) {
    if (error instanceof Error) {
      stageError.value = error.message
    }
    stage.value = 'error'
  }
}

function handleReset() {
  revokePreviewUrl()
  stage.value = 'upload'
  isPdf.value = false
  latexOutput.value = ''
  uploadedFile.value = null
  latestProjectId.value = null
  remoteSaveWarning.value = ''
  stageError.value = null
  resetConvert()
}

function canRetryRemoteSave(): boolean {
  return Boolean(
    uploadedFile.value
    && latexOutput.value
    && latestProjectId.value
    && latestProjectId.value.startsWith('local-'),
  )
}

async function retryRemoteSave(): Promise<boolean> {
  if (!canRetryRemoteSave() || !uploadedFile.value) {
    return false
  }

  remoteSaveBusy.value = true
  try {
    const project = await addConvertedProject({
      name: uploadedFile.value.name,
      latex: latexOutput.value,
      sourceFilename: uploadedFile.value.name,
      sourceKind: isPdf.value ? 'pdf' : 'image',
      ownerId: userId.value ?? null,
    })
    latestProjectId.value = project.id
    remoteSaveWarning.value = project.id.startsWith('local-')
      ? 'Cloud save is still unavailable. PDF compile remains disabled until save succeeds.'
      : ''
    return !project.id.startsWith('local-')
  } catch {
    remoteSaveWarning.value = 'Cloud save retry failed. Please try again.'
    return false
  } finally {
    remoteSaveBusy.value = false
  }
}

async function openEditorForLatest() {
  if (latestProjectId.value?.startsWith('local-')) {
    const saved = await retryRemoteSave()
    if (!saved) {
      if (latexOutput.value) {
        sessionStorage.setItem(PENDING_EDITOR_DRAFT_KEY, JSON.stringify({
          latex: latexOutput.value,
          name: uploadedFile.value?.name || 'Untitled conversion',
          sourceFilename: uploadedFile.value?.name || 'main.tex',
        }))
        router.push({ path: '/editor', query: { draft: '1' } })
      }
      return
    }
  }

  if (latestProjectId.value) {
    router.push({ path: '/editor', query: { projectId: latestProjectId.value } })
    return
  }

  if (latexOutput.value) {
    sessionStorage.setItem(PENDING_EDITOR_DRAFT_KEY, JSON.stringify({
      latex: latexOutput.value,
      name: uploadedFile.value?.name || 'Untitled conversion',
      sourceFilename: uploadedFile.value?.name || 'main.tex',
    }))
    router.push({ path: '/editor', query: { draft: '1' } })
    return
  }

  router.push('/editor')
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
    <div class="relative z-10 border-b border-border/50 bg-[hsl(var(--background)/0.8)] pt-14 md:pt-0 backdrop-blur-xl">
      <div class="mx-auto flex max-w-7xl items-center justify-center gap-2 px-6 py-3 md:pr-28">
        <template v-for="(s, i) in allStages" :key="s">
          <div class="flex items-center gap-2">
            <div
              :class="[
                'flex h-6 w-6 items-center justify-center rounded-sm text-[10px] font-semibold transition-all duration-300',
                stage === s
                  ? 'bg-primary text-primary-foreground'
                  : stageIndex(stage) > i
                    ? 'bg-primary/20 text-primary'
                    : 'text-muted-foreground/50',
              ]"
              :style="stage !== s && stageIndex(stage) <= i ? 'border: 1px solid hsl(var(--border) / 0.4)' : ''"
            >
              {{ i + 1 }}
            </div>
            <span
              :class="[
                'text-[10px] font-semibold tracking-[0.1em] uppercase transition-colors duration-300',
                stage === s ? 'text-foreground' : 'text-muted-foreground/50',
              ]"
            >
              {{ s === 'upload' ? 'Upload' : s === 'loading' ? 'Processing' : 'Result' }}
            </span>
          </div>
          <div
            v-if="i < 2"
            :class="[
              'h-px w-10 transition-colors duration-300',
              stageIndex(stage) > i ? 'bg-[hsl(var(--primary)/0.4)]' : 'bg-[hsl(var(--border)/0.3)]',
            ]"
          />
        </template>
      </div>
    </div>

    <!-- Content area -->
    <div :class="[
      'relative z-10 flex flex-col items-center pt-4 md:pr-24',
      stage === 'result' ? 'min-h-[calc(100vh-56px)]' : 'min-h-[calc(100vh-110px)] justify-center px-6 py-12'
    ]">
      <!-- Upload -->
      <div v-if="stage === 'upload'" class="w-full max-w-2xl">
        <div class="mb-10 text-center">
          <div class="mb-4 flex items-center justify-center gap-3">
            <div class="h-px w-8 bg-primary" />
            <span class="text-[11px] font-semibold tracking-[0.3em] uppercase text-primary">Upload</span>
            <div class="h-px w-8 bg-primary" />
          </div>
          <h1 class="mb-3 text-3xl font-bold text-foreground">Convert Your Notes</h1>
          <p class="text-[13px] tracking-wide text-muted-foreground/70">
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
        <div class="mb-6 flex h-14 w-14 mx-auto items-center justify-center rounded-xl bg-destructive/10 text-destructive">
          <svg class="h-7 w-7" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10" /><path d="m15 9-6 6M9 9l6 6" />
          </svg>
        </div>
        <h2 class="mb-2 text-lg font-semibold text-foreground">Conversion Failed</h2>
        <p class="mb-8 text-[13px] tracking-wide text-muted-foreground/70">{{ stageError || convertError || 'Something went wrong. Please try again.' }}</p>
        <button
          type="button"
          class="inline-flex items-center gap-2 rounded-sm bg-primary px-6 py-2.5 text-[11px] font-semibold tracking-[0.12em] uppercase text-primary-foreground transition-all duration-300 hover:opacity-90"
          @click="handleReset"
        >
          Try Again
        </button>
      </div>

      <!-- Result -->
      <div v-if="stage === 'result'" class="mb-3 w-full max-w-[1600px] px-4 text-right">
        <p v-if="remoteSaveWarning" class="mb-3 rounded-sm border border-destructive/30 bg-destructive/10 px-4 py-2 text-left text-[12px] text-destructive">{{ remoteSaveWarning }}</p>
        <button
          type="button"
          class="inline-flex items-center gap-2 rounded-sm border px-5 py-2 text-[11px] font-semibold tracking-[0.12em] uppercase transition-all duration-300"
          style="background: transparent; color: hsl(var(--muted-foreground)); border-color: hsl(var(--border))"
          :disabled="remoteSaveBusy"
          @click="openEditorForLatest"
        >
          {{ remoteSaveBusy ? 'Saving...' : 'Open In Editor' }}
        </button>
        <button
          v-if="canRetryRemoteSave()"
          type="button"
          class="ml-2 inline-flex items-center gap-2 rounded-sm border px-5 py-2 text-[11px] font-semibold tracking-[0.12em] uppercase transition-all duration-300 disabled:opacity-50"
          style="background: transparent; color: hsl(var(--muted-foreground)); border-color: hsl(var(--border))"
          :disabled="remoteSaveBusy"
          @click="retryRemoteSave"
        >
          {{ remoteSaveBusy ? 'Retrying...' : 'Retry Cloud Save' }}
        </button>
      </div>
      <ResultView
        v-if="stage === 'result'"
        :image-url="imageUrl"
        :is-pdf="isPdf"
        :pdf-file="uploadedFile ?? undefined"
        :latex="latexOutput"
        :tex-file-id="latestProjectId ?? undefined"
        @reset="handleReset"
      />
    </div>
  </div>
</template>
