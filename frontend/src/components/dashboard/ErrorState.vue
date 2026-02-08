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
  <div class="flex flex-col items-center justify-center rounded-2xl border border-border bg-card px-8 py-20">
    <!-- Icon -->
    <div class="mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-destructive/15">
      <AlertCircle class="h-10 w-10 text-destructive" />
    </div>

    <!-- Copy -->
    <h3 class="mb-2 text-xl font-semibold text-foreground">
      Something Went Wrong
    </h3>
    <p class="mb-8 max-w-md text-center text-sm text-muted-foreground">
      {{ message || 'We couldn\'t load your dashboard. Please check your connection and try again.' }}
    </p>

    <!-- Retry -->
    <button
      class="flex items-center gap-2 rounded-xl border border-border bg-secondary px-6 py-3 font-medium text-foreground transition-all hover:border-primary/50 hover:text-primary active:scale-95"
      @click="$emit('retry')"
    >
      <RotateCcw class="h-5 w-5" />
      Try Again
    </button>
  </div>
</template>
