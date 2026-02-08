<script setup lang="ts">
import { useAuth } from '@clerk/vue'
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import EmptyState from '@/components/dashboard/EmptyState.vue'
import ProjectRow from '@/components/dashboard/ProjectRow.vue'
import { AUTH_SESSION_EXPIRED_MESSAGE, useProjects } from '@/composables/useProjects'

const router = useRouter()
const { isLoaded, isSignedIn, userId } = useAuth()
const { projects, ensureRemoteProjectsLoaded } = useProjects(userId)
const authErrorMessage = ref('')

watch(
  [isLoaded, isSignedIn],
  ([loaded, signedIn]) => {
    if (!loaded) return
    if (!signedIn) {
      void router.replace('/')
      return
    }
    void ensureRemoteProjectsLoaded().then(() => {
      authErrorMessage.value = ''
    }).catch((error) => {
      authErrorMessage.value = error instanceof Error && error.message === AUTH_SESSION_EXPIRED_MESSAGE
        ? AUTH_SESSION_EXPIRED_MESSAGE
        : 'Unable to load projects right now.'
    })
  },
  { immediate: true },
)

function handleUpload() {
  router.push('/convert')
}

function handleView(_id: string) {
  router.push({ path: '/editor', query: { projectId: _id } })
}

function handleEdit(_id: string) {
  router.push({ path: '/editor', query: { projectId: _id } })
}

function handleRetry(_id: string) {
  router.push('/convert')
}
</script>

<template>
  <div class="relative min-h-screen bg-background">
    <AppNavbar />
    <div class="fixed inset-0 bg-grid-pattern opacity-20" />

    <main class="relative z-10 mx-auto max-w-5xl px-6 pt-10 pb-12">
      <!-- Page header -->
      <div class="mb-8 flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-foreground">Dashboard</h1>
          <p class="mt-1 text-sm text-muted-foreground">Your recent conversions and projects.</p>
          <p v-if="authErrorMessage" class="mt-2 text-sm text-destructive">{{ authErrorMessage }}</p>
        </div>
        <button
          class="inline-flex items-center gap-2 rounded-md bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground transition-colors hover:bg-[hsl(var(--primary)/0.9)]"
          @click="handleUpload"
        >
          <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12" />
          </svg>
          New Conversion
        </button>
      </div>

      <!-- Empty state -->
      <EmptyState v-if="projects.length === 0" @upload="handleUpload" />

      <!-- Project list (shown once there are conversions) -->
      <section v-else>
        <div class="mb-4 flex items-center justify-between">
          <h2 class="text-lg font-semibold text-foreground">Recent Projects</h2>
          <span class="text-xs text-muted-foreground">{{ projects.length }} project{{ projects.length === 1 ? '' : 's' }}</span>
        </div>
        <div class="space-y-2">
          <ProjectRow
            v-for="project in projects"
            :key="project.id"
            :project="project"
            @view="handleView"
            @edit="handleEdit"
            @retry="handleRetry"
          />
        </div>
      </section>
    </main>
  </div>
</template>
