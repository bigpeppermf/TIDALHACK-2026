<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import DashboardTopBar from '@/components/dashboard/DashboardTopBar.vue'
import ComparisonPanel from '@/components/dashboard/ComparisonPanel.vue'
import ProjectRow from '@/components/dashboard/ProjectRow.vue'
import EmptyState from '@/components/dashboard/EmptyState.vue'
import LoadingSkeleton from '@/components/dashboard/LoadingSkeleton.vue'
import ErrorState from '@/components/dashboard/ErrorState.vue'
import type { Project } from '@/components/dashboard/ProjectRow.vue'

type ViewState = 'loaded' | 'empty' | 'loading' | 'error'

const router = useRouter()
const viewState = ref<ViewState>('loaded')
const emphasis = ref<'left' | 'right' | 'none'>('none')

// --- Mock data (will be replaced by backend) ---
const MOCK_PROJECTS: Project[] = [
  { id: '1', name: 'Calculus Notes — Chapter 3', updatedAt: '2 hours ago', status: 'converted' },
  { id: '2', name: 'Physics Lab Report #7', updatedAt: '5 hours ago', status: 'processing' },
  { id: '3', name: 'Organic Chemistry Equations', updatedAt: '1 day ago', status: 'converted' },
  { id: '4', name: 'Statistics Homework Set 4', updatedAt: '2 days ago', status: 'failed' },
  { id: '5', name: 'Linear Algebra Proofs', updatedAt: '3 days ago', status: 'converted' },
]

const CURRENT_PROJECT = {
  fileName: 'calculus-ch3-notes.png',
  date: 'Jan 15, 2026',
  status: 'converted',
}

// --- Handlers ---
function handleUpload() {
  router.push('/convert')
}

function handleEmphasisToggle(side: 'left' | 'right') {
  if (emphasis.value === side) {
    emphasis.value = 'none'
  } else {
    emphasis.value = side
  }
}

function handleRetry() {
  viewState.value = 'loading'
  setTimeout(() => {
    viewState.value = 'loaded'
  }, 1500)
}
</script>

<template>
  <div class="relative min-h-screen bg-[#0a0a0b] text-gray-100">
    <!-- Top Bar -->
    <DashboardTopBar @upload-click="handleUpload" />

    <!-- Main Content -->
    <main class="mx-auto max-w-7xl px-6 py-8">
      <!-- Demo State Controls (dev only — remove for production) -->
      <div class="mb-6 flex items-center gap-2 rounded-lg border border-[#2d2d38] bg-[#131316] px-4 py-2">
        <span class="mr-2 text-xs text-gray-500">View:</span>
        <button
          v-for="state in (['loaded', 'empty', 'loading', 'error'] as ViewState[])"
          :key="state"
          :class="[
            'rounded-md px-3 py-1 text-xs font-medium transition-colors',
            viewState === state
              ? 'bg-purple-600 text-white'
              : 'bg-[#1a1a1f] text-gray-400 hover:text-gray-200',
          ]"
          @click="viewState = state"
        >
          {{ state }}
        </button>
      </div>

      <!-- Loading -->
      <LoadingSkeleton v-if="viewState === 'loading'" />

      <!-- Error -->
      <ErrorState v-else-if="viewState === 'error'" @retry="handleRetry" />

      <!-- Empty -->
      <EmptyState v-else-if="viewState === 'empty'" @upload="handleUpload" />

      <!-- Loaded -->
      <template v-else>
        <!-- Comparison Panels -->
        <div
          :class="[
            'mb-10 grid gap-6 transition-all duration-300',
            emphasis === 'none' ? 'grid-cols-2' : 'grid-cols-3',
          ]"
        >
          <ComparisonPanel
            type="original"
            :project-data="CURRENT_PROJECT"
            :emphasis="emphasis"
            @emphasis-toggle="handleEmphasisToggle('left')"
          />
          <ComparisonPanel
            type="converted"
            :project-data="CURRENT_PROJECT"
            :emphasis="emphasis"
            @emphasis-toggle="handleEmphasisToggle('right')"
          />
        </div>

        <!-- Recent Projects -->
        <section>
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-200">
              Recent Projects
            </h2>
            <button class="text-sm text-purple-400 transition-colors hover:text-purple-300">
              See all projects →
            </button>
          </div>

          <div class="space-y-2">
            <ProjectRow
              v-for="project in MOCK_PROJECTS"
              :key="project.id"
              :project="project"
              @view="(id) => console.log('View', id)"
              @edit="(id) => console.log('Edit', id)"
              @retry="(id) => console.log('Retry', id)"
            />
          </div>
        </section>
      </template>
    </main>
  </div>
</template>
