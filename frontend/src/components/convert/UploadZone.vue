<script setup lang="ts">
import { ref, onUnmounted } from 'vue'

const emit = defineEmits<{
  fileAccepted: [file: File]
}>()

const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp']
const MAX_SIZE = 10 * 1024 * 1024

const dragOver = ref(false)
const preview = ref<string | null>(null)
const selectedFile = ref<File | null>(null)
const error = ref<string | null>(null)

function validate(file: File): string | null {
  if (!ACCEPTED_TYPES.includes(file.type)) {
    return 'Only JPEG, PNG, and WebP images are supported.'
  }
  if (file.size > MAX_SIZE) {
    return 'File must be under 10MB.'
  }
  return null
}

function handleFile(file: File) {
  const err = validate(file)
  if (err) {
    error.value = err
    return
  }
  error.value = null
  selectedFile.value = file
  preview.value = URL.createObjectURL(file)
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
  if (preview.value) URL.revokeObjectURL(preview.value)
  selectedFile.value = null
  preview.value = null
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

onUnmounted(() => {
  if (preview.value) URL.revokeObjectURL(preview.value)
})
</script>

<template>
  <div class="flex flex-col items-center gap-6">
    <!-- Upload area -->
    <label
      v-if="!preview"
      for="file-upload"
      :class="[
        'group relative flex w-full max-w-2xl cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed p-12 transition-all duration-300 md:p-16',
        dragOver
          ? 'border-primary bg-primary/5 shadow-lg shadow-primary/10'
          : 'border-border hover:border-primary/40 hover:bg-card',
      ]"
      @dragover.prevent="dragOver = true"
      @dragleave="dragOver = false"
      @drop="onDrop"
    >
      <input
        id="file-upload"
        type="file"
        accept="image/jpeg,image/png,image/webp"
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
        {{ dragOver ? 'Drop your image here' : 'Drag & drop your notes' }}
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
          JPEG, PNG, WebP
        </span>
        <span class="h-3 w-px bg-[hsl(var(--border))]" />
        <span>Max 10MB</span>
      </div>
    </label>

    <!-- Preview -->
    <div
      v-else
      class="relative w-full max-w-2xl overflow-hidden rounded-2xl border border-border bg-card"
    >
      <div class="relative aspect-video w-full">
        <img
          :src="preview"
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
      class="inline-flex items-center gap-2 rounded-md bg-primary px-6 py-3 text-sm font-medium text-primary-foreground transition-colors hover:bg-[hsl(var(--primary)/0.9)]"
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
