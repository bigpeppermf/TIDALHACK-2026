<script setup lang="ts">
import { ref } from 'vue'
import { ZoomIn, ZoomOut, Maximize2, Minimize2, Expand, Edit3 } from 'lucide-vue-next'

const props = defineProps<{
  type: 'original' | 'converted'
  projectData?: {
    fileName: string
    date: string
    status: string
  }
  emphasis?: 'left' | 'right' | 'none'
}>()

const emit = defineEmits<{
  openEditor: []
  emphasisToggle: []
}>()

const zoom = ref(100)
const isFullscreen = ref(false)

const isOriginal = props.type === 'original'
</script>

<template>
  <div
    :class="[
      'flex flex-col overflow-hidden rounded-xl border border-[#2d2d38] bg-[#1a1a1f] shadow-lg transition-all duration-300',
      emphasis === 'left' && isOriginal ? 'col-span-2' : '',
      emphasis === 'right' && !isOriginal ? 'col-span-2' : '',
      emphasis === 'left' && !isOriginal ? 'col-span-1' : '',
      emphasis === 'right' && isOriginal ? 'col-span-1' : '',
    ]"
  >
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-[#2d2d38] bg-[#131316] px-4 py-3">
      <h3 class="text-sm font-medium text-gray-400">
        {{ isOriginal ? 'Original Document' : 'Converted Document' }}
      </h3>

      <!-- Controls -->
      <div class="flex items-center gap-2">
        <button
          class="rounded p-1.5 text-gray-400 transition-colors hover:bg-[#2d2d38] hover:text-purple-400"
          title="Zoom out"
          @click="zoom = Math.max(50, zoom - 10)"
        >
          <ZoomOut class="h-4 w-4" />
        </button>
        <span class="min-w-[3rem] text-center text-xs text-gray-500">
          {{ zoom }}%
        </span>
        <button
          class="rounded p-1.5 text-gray-400 transition-colors hover:bg-[#2d2d38] hover:text-purple-400"
          title="Zoom in"
          @click="zoom = Math.min(200, zoom + 10)"
        >
          <ZoomIn class="h-4 w-4" />
        </button>

        <div class="mx-1 h-5 w-px bg-[#2d2d38]" />

        <button
          class="rounded p-1.5 text-gray-400 transition-colors hover:bg-[#2d2d38] hover:text-purple-400"
          title="Emphasize panel"
          @click="$emit('emphasisToggle')"
        >
          <Expand class="h-4 w-4" />
        </button>

        <button
          class="rounded p-1.5 text-gray-400 transition-colors hover:bg-[#2d2d38] hover:text-purple-400"
          title="Fullscreen"
          @click="isFullscreen = !isFullscreen"
        >
          <Minimize2 v-if="isFullscreen" class="h-4 w-4" />
          <Maximize2 v-else class="h-4 w-4" />
        </button>
      </div>
    </div>

    <!-- Document Preview -->
    <div class="relative flex min-h-[500px] flex-1 items-center justify-center overflow-hidden bg-[#0a0a0b] p-8">
      <template v-if="projectData">
        <div
          class="w-full max-w-lg rounded bg-white p-10 shadow-2xl transition-transform"
          :style="{ transform: `scale(${zoom / 100})` }"
        >
          <div class="space-y-3 text-gray-900" style="font-family: Georgia, serif">
            <h2 class="mb-6 text-2xl font-bold text-gray-900" style="font-family: Georgia, serif">
              Meeting Notes
            </h2>
            <p class="text-base leading-relaxed">
              The quick brown fox jumps over the lazy dog. This is a sample of handwritten text
              that has been converted into digital format using monogram's conversion technology.
            </p>
            <p class="text-base leading-relaxed">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor
              incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud
              exercitation.
            </p>
            <p class="text-base leading-relaxed">
              Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu
              fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident.
            </p>
            <div class="mt-8 border-t border-gray-300 pt-4">
              <p class="text-sm font-medium text-gray-600">January 2026</p>
            </div>
          </div>
        </div>
      </template>
      <template v-else>
        <div class="text-center text-gray-600">
          <p>No document selected</p>
        </div>
      </template>

      <!-- Subtle glow effect -->
      <div class="pointer-events-none absolute inset-0 bg-gradient-to-t from-purple-900/10 to-transparent" />
    </div>

    <!-- Metadata & Actions -->
    <div v-if="projectData" class="border-t border-[#2d2d38] bg-[#131316] px-4 py-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-6 text-xs text-gray-500">
          <span class="font-medium text-gray-300">{{ projectData.fileName }}</span>
          <span>{{ projectData.date }}</span>
          <span
            :class="[
              'rounded-full border px-2 py-0.5 text-xs',
              projectData.status === 'converted'
                ? 'border-purple-700/30 bg-purple-900/30 text-purple-300'
                : 'border-gray-600/30 bg-gray-700/30 text-gray-400',
            ]"
          >
            {{ projectData.status }}
          </span>
        </div>

        <button
          v-if="!isOriginal"
          class="flex items-center gap-2 rounded-lg bg-purple-600 px-4 py-1.5 text-sm text-white transition-all hover:bg-purple-500 hover:shadow-[0_0_15px_rgba(168,85,247,0.3)] active:scale-95"
          @click="$emit('openEditor')"
        >
          <Edit3 class="h-3.5 w-3.5" />
          Open in Editor
        </button>
      </div>
    </div>
  </div>
</template>
