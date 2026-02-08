<script setup lang="ts">
import { AlertCircle, RotateCcw } from 'lucide-vue-next'

defineProps<{
  message?: string
}>()

defineEmits<{
  retry: []
}>()
</script>

<template>
  <div class="flex flex-col items-center justify-center rounded-2xl border border-[#2d2d38] bg-[#131316] px-8 py-20">
    <!-- Icon -->
    <div class="mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-red-900/30">
      <AlertCircle class="h-10 w-10 text-red-400" />
    </div>

    <!-- Copy -->
    <h3 class="mb-2 text-xl font-semibold text-gray-200">
      Something Went Wrong
    </h3>
    <p class="mb-8 max-w-md text-center text-sm text-gray-500">
      {{ message || 'We couldn\'t load your dashboard. Please check your connection and try again.' }}
    </p>

    <!-- Retry -->
    <button
      class="flex items-center gap-2 rounded-xl border border-[#2d2d38] bg-[#1a1a1f] px-6 py-3 font-medium text-gray-300 transition-all hover:border-purple-700/50 hover:text-purple-400 active:scale-95"
      @click="$emit('retry')"
    >
      <RotateCcw class="h-5 w-5" />
      Try Again
    </button>
  </div>
</template>
