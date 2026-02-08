<script setup lang="ts">
import { computed } from 'vue'
import { Eye, Edit3, RotateCcw, FileText, Loader2, AlertCircle } from 'lucide-vue-next'
import type { ProjectRecord } from '@/types/project'

const props = defineProps<{
  project: ProjectRecord
}>()

const emit = defineEmits<{
  view: [id: string]
  edit: [id: string]
  retry: [id: string]
}>()

const statusConfig = computed(() => {
  const configs = {
    converted: {
      label: 'Converted',
      bgClass: 'bg-purple-900/30',
      textClass: 'text-purple-300',
      borderClass: 'border-purple-700/30',
      icon: FileText,
      iconClass: 'text-purple-400',
    },
    processing: {
      label: 'Processing',
      bgClass: 'bg-yellow-900/30',
      textClass: 'text-yellow-300',
      borderClass: 'border-yellow-700/30',
      icon: Loader2,
      iconClass: 'text-yellow-400',
    },
    failed: {
      label: 'Failed',
      bgClass: 'bg-red-900/30',
      textClass: 'text-red-300',
      borderClass: 'border-red-700/30',
      icon: AlertCircle,
      iconClass: 'text-red-400',
    },
  }
  return configs[props.project.status]
})
</script>

<template>
  <div
    class="group flex items-center gap-4 rounded-xl border border-transparent bg-card p-4 transition-all hover:border-border hover:bg-secondary hover:shadow-lg"
  >
    <!-- Thumbnail -->
    <div class="flex h-20 w-20 flex-shrink-0 items-center justify-center overflow-hidden rounded-lg bg-background">
      <img
        v-if="project.thumbnail"
        :src="project.thumbnail"
        :alt="project.name"
        class="h-full w-full object-cover"
      />
      <FileText v-else class="h-8 w-8 text-muted-foreground/50" />
    </div>

    <!-- Info -->
    <div class="flex min-w-0 flex-1 flex-col gap-1">
      <h4 class="truncate text-sm font-medium text-foreground">
        {{ project.name }}
      </h4>
      <p class="text-xs text-muted-foreground">
        Updated {{ project.updatedAt }}
      </p>
      <span
        :class="[
          'inline-flex w-fit items-center gap-1 rounded-full border px-2 py-0.5 text-xs',
          statusConfig.bgClass,
          statusConfig.textClass,
          statusConfig.borderClass,
        ]"
      >
        <component
          :is="statusConfig.icon"
          :class="['h-3 w-3', statusConfig.iconClass, project.status === 'processing' ? 'animate-spin' : '']"
        />
        {{ statusConfig.label }}
      </span>
    </div>

    <!-- Hover Actions -->
    <div class="flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100">
      <button
        class="rounded-lg p-2 text-muted-foreground transition-colors hover:bg-secondary hover:text-primary"
        title="View"
        @click="$emit('view', project.id)"
      >
        <Eye class="h-4 w-4" />
      </button>
      <button
        v-if="project.status === 'converted'"
        class="rounded-lg p-2 text-muted-foreground transition-colors hover:bg-secondary hover:text-primary"
        title="Edit"
        @click="$emit('edit', project.id)"
      >
        <Edit3 class="h-4 w-4" />
      </button>
      <button
        v-if="project.status === 'failed'"
        class="rounded-lg p-2 text-muted-foreground transition-colors hover:bg-secondary hover:text-yellow-400"
        title="Retry"
        @click="$emit('retry', project.id)"
      >
        <RotateCcw class="h-4 w-4" />
      </button>
    </div>
  </div>
</template>
