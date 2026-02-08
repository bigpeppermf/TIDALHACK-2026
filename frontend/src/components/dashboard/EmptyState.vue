<script setup lang="ts">
import { FileText, Upload } from 'lucide-vue-next'

defineEmits<{
  upload: []
}>()
</script>

<template>
  <div
    class="flex flex-col items-center justify-center rounded-xl border border-dashed px-8 py-24"
    style="border-color: hsl(var(--border) / 0.3); background: hsl(var(--card) / 0.3)"
  >
    <!-- Icon -->
    <div class="mb-8 flex h-16 w-16 items-center justify-center rounded-xl" style="background: hsl(var(--primary) / 0.1)">
      <FileText class="h-7 w-7 text-primary/60" />
    </div>

    <!-- Copy -->
    <h3 class="mb-2 text-lg font-semibold text-foreground">
      No Projects Yet
    </h3>
    <p class="mb-10 max-w-md text-center text-[13px] tracking-wide text-muted-foreground/60">
      Upload your first handwritten document and watch it transform into beautifully formatted LaTeX.
    </p>

    <!-- CTA -->
    <button
      class="inline-flex items-center gap-2 rounded-sm bg-primary px-6 py-2.5 text-[11px] font-semibold tracking-[0.12em] uppercase text-primary-foreground transition-all duration-300 hover:opacity-90"
      @click="$emit('upload')"
    >
      <Upload class="h-4 w-4" />
      Upload Document
    </button>
  </div>
</template>
