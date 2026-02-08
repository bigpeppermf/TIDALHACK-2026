<script setup lang="ts">
import { FileText, Upload } from 'lucide-vue-next'

defineEmits<{
  upload: []
}>()
</script>

<template>
  <div class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-[#2d2d38] bg-[#131316] px-8 py-20">
    <!-- Icon -->
    <div class="mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-purple-900/30">
      <FileText class="h-10 w-10 text-purple-400" />
    </div>

    <!-- Copy -->
    <h3 class="mb-2 text-xl font-semibold text-gray-200">
      No Projects Yet
    </h3>
    <p class="mb-8 max-w-md text-center text-sm text-gray-500">
      Upload your first handwritten document and watch it transform into beautifully formatted LaTeX.
    </p>

    <!-- CTA -->
    <button
      class="flex items-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-purple-500 px-6 py-3 font-medium text-white shadow-lg shadow-purple-900/30 transition-all hover:shadow-xl hover:shadow-purple-900/40 active:scale-95"
      @click="$emit('upload')"
    >
      <Upload class="h-5 w-5" />
      Upload Document
    </button>
  </div>
</template>
