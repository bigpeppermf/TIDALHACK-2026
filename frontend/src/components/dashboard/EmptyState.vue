<script setup lang="ts">
import { FileText, Upload } from 'lucide-vue-next'

defineEmits<{
  upload: []
}>()
</script>

<template>
  <div class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border bg-card px-8 py-20">
    <!-- Icon -->
    <div class="mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-primary/15">
      <FileText class="h-10 w-10 text-primary" />
    </div>

    <!-- Copy -->
    <h3 class="mb-2 text-xl font-semibold text-foreground">
      No Projects Yet
    </h3>
    <p class="mb-8 max-w-md text-center text-sm text-muted-foreground">
      Upload your first handwritten document and watch it transform into beautifully formatted LaTeX.
    </p>

    <!-- CTA -->
    <button
      class="flex items-center gap-2 rounded-xl bg-primary px-6 py-3 font-medium text-primary-foreground shadow-lg shadow-primary/20 transition-all hover:shadow-xl hover:shadow-primary/30 active:scale-95"
      @click="$emit('upload')"
    >
      <Upload class="h-5 w-5" />
      Upload Document
    </button>
  </div>
</template>
