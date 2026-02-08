<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  fileAccepted: [file: File]
}>()

const ACCEPTED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf']
const ACCEPTED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.pdf']
const MAX_SIZE = 10 * 1024 * 1024

const dragOver = ref(false)
const preview = ref<string | null>(null)
const selectedFile = ref<File | null>(null)
const error = ref<string | null>(null)

function validate(file: File): string | null {
  const fileName = file.name.toLowerCase()
  const hasAcceptedMimeType = ACCEPTED_MIME_TYPES.includes(file.type)
  const hasAcceptedExtension = ACCEPTED_EXTENSIONS.some((ext) => fileName.endsWith(ext))

  if (!hasAcceptedMimeType && !hasAcceptedExtension) {
    return 'Only JPEG, PNG, WebP images and PDF documents are supported.'
  }
  if (file.size > MAX_SIZE) {
    return 'File must be under 10MB.'
  }
  return null
}

const isPdf = ref(false)

function handleFile(file: File) {
  const err = validate(file)
  if (err) {
    error.value = err
    return
  }

  if (preview.value && preview.value !== 'pdf') {
    URL.revokeObjectURL(preview.value)
  }

  error.value = null
  selectedFile.value = file
  const fileName = file.name.toLowerCase()
  isPdf.value = file.type === 'application/pdf' || fileName.endsWith('.pdf')
  preview.value = isPdf.value ? 'pdf' : URL.createObjectURL(file)
}

function onDrop(e: DragEvent) {
  e.preventDefault()
  dragOver.value = false
  const file = e.dataTransfer?.files[0]
  if (file) handleFile(file)
}

function onInputChange(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) handleFile(file)
}

function clearFile() {
  if (preview.value && preview.value !== 'pdf') URL.revokeObjectURL(preview.value)
  selectedFile.value = null
  preview.value = null
  isPdf.value = false
  error.value = null
}

function submit() {
  if (selectedFile.value) {
    emit('fileAccepted', selectedFile.value)
  }
}

function fileSizeLabel(size: number) {
  return `${(size / 1024).toFixed(0)} KB`
}

</script>

<template>
  <div class="flex flex-col items-center gap-6">
    <!-- Upload area -->
    <label
      v-if="!preview"
      for="file-upload"
      :class="[
        'group relative flex w-full max-w-2xl cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-12 transition-all duration-300 md:p-16',
        dragOver
          ? 'border-primary bg-primary/5 shadow-lg shadow-primary/10'
          : 'border-[hsl(var(--border)/0.4)] hover:border-primary/40 hover:bg-[hsl(var(--card)/0.3)]',
      ]"
      @dragover.prevent="dragOver = true"
      @dragleave="dragOver = false"
      @drop="onDrop"
    >
      <input
        id="file-upload"
        type="file"
        accept="image/jpeg,image/png,image/webp,application/pdf"
        class="sr-only"
        @change="onInputChange"
      />

      <div
        :class="[
          'mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 text-primary transition-transform duration-300',
          dragOver ? 'scale-110' : 'group-hover:scale-105',
        ]"
      >
        <!-- Upload icon -->
        <svg
          class="h-7 w-7"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12" />
        </svg>
      </div>

      <p class="mb-2 text-lg font-semibold text-foreground">
        {{ dragOver ? 'Drop your file here' : 'Drag & drop your notes' }}
      </p>
      <p class="mb-4 text-sm text-muted-foreground">or click to browse files</p>
      <div class="flex items-center gap-4 text-xs text-muted-foreground">
        <span class="flex items-center gap-1">
          <!-- Image icon -->
          <svg
            class="h-3 w-3"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <rect width="18" height="18" x="3" y="3" rx="2" ry="2" />
            <circle cx="9" cy="9" r="2" />
            <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />
          </svg>
          JPEG, PNG, WebP, PDF
        </span>
        <span class="h-3 w-px bg-[hsl(var(--border))]" />
        <span>Max 10MB</span>
      </div>
    </label>

    <!-- Preview -->
    <div
      v-else
      class="relative w-full max-w-2xl overflow-hidden rounded-xl border"
      style="border-color: hsl(var(--border) / 0.4); background: hsl(var(--card) / 0.5)"
    >
      <div class="relative aspect-video w-full">
        <!-- PDF preview -->
        <div v-if="isPdf" class="flex h-full w-full flex-col items-center justify-center gap-3 bg-[hsl(var(--background)/0.5)] p-4">
          <svg class="h-16 w-16 text-primary/60" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
            <line x1="10" y1="9" x2="8" y2="9" />
          </svg>
          <span class="text-sm font-medium text-foreground">PDF Document</span>
        </div>
        <!-- Image preview -->
        <img
          v-else
          :src="preview!"
          alt="Preview of uploaded handwritten notes"
          class="h-full w-full object-contain bg-[hsl(var(--background)/0.5)] p-4"
        />
        <button
          type="button"
          class="absolute right-3 top-3 flex h-8 w-8 items-center justify-center rounded-full bg-[hsl(var(--background)/0.8)] text-foreground backdrop-blur-sm transition-colors hover:bg-destructive hover:text-destructive-foreground"
          aria-label="Remove file"
          @click="clearFile"
        >
          <!-- X icon -->
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
            <path d="M18 6 6 18M6 6l12 12" />
          </svg>
        </button>
      </div>
      <div class="flex items-center justify-between border-t border-border px-5 py-3">
        <div class="flex items-center gap-3">
          <svg
            class="h-4 w-4 text-muted-foreground"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <rect width="18" height="18" x="3" y="3" rx="2" ry="2" />
            <circle cx="9" cy="9" r="2" />
            <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />
          </svg>
          <span class="text-sm text-foreground">{{ selectedFile?.name }}</span>
          <span v-if="selectedFile" class="text-xs text-muted-foreground">
            {{ fileSizeLabel(selectedFile.size) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Error -->
    <p v-if="error" class="text-sm text-destructive">{{ error }}</p>

    <!-- Convert button -->
    <button
      v-if="preview && selectedFile"
      type="button"
      class="inline-flex items-center gap-2 rounded-sm bg-primary px-8 py-3 text-[11px] font-semibold tracking-[0.12em] uppercase text-primary-foreground transition-all duration-300 hover:opacity-90"
      @click="submit"
    >
      Convert to LaTeX
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
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12" />
      </svg>
    </button>
  </div>
</template>
