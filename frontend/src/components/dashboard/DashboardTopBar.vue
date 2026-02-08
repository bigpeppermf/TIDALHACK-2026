<script setup lang="ts">
import { Search, Upload, User } from 'lucide-vue-next'

defineEmits<{
  uploadClick: []
}>()
</script>

<template>
  <div class="border-b border-[#2d2d38] bg-[#131316] px-6 py-5 shadow-lg">
    <div class="mx-auto flex max-w-[1600px] items-center justify-between">
      <!-- Title -->
      <h1 class="text-4xl tracking-wide text-purple-400 md:text-5xl">
        Dashboard
      </h1>

      <!-- Search and Actions -->
      <div class="flex items-center gap-4">
        <!-- Search -->
        <div
          class="hidden items-center gap-2 rounded-lg border border-[#2d2d38] bg-[#1a1a1f] px-4 py-2.5 transition-all focus-within:border-purple-500/50 focus-within:shadow-[0_0_0_3px_rgba(168,85,247,0.1)] md:flex"
          style="min-width: 320px"
        >
          <Search class="h-4 w-4 text-gray-500" />
          <input
            type="text"
            placeholder="Search projects..."
            class="w-full border-none bg-transparent text-sm text-gray-300 placeholder-gray-600 outline-none"
          />
        </div>

        <!-- Upload Button -->
        <button
          class="flex items-center gap-2.5 rounded-lg bg-gradient-to-r from-purple-600 to-purple-500 px-6 py-2.5 font-medium text-white shadow-md transition-all hover:from-purple-500 hover:to-purple-400 hover:shadow-[0_0_25px_rgba(168,85,247,0.5)] active:scale-[0.98]"
          @click="$emit('uploadClick')"
        >
          <Upload class="h-4 w-4" />
          <span class="hidden sm:inline">Go to Upload</span>
        </button>

        <!-- Profile -->
        <button
          class="flex h-11 w-11 items-center justify-center rounded-full border-2 border-purple-700 bg-gradient-to-br from-purple-900 to-purple-800 transition-all hover:border-purple-500 hover:shadow-[0_0_15px_rgba(168,85,247,0.3)]"
        >
          <User class="h-5 w-5 text-purple-300" />
        </button>
      </div>
    </div>
  </div>
</template>
