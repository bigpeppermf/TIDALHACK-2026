import { readonly, ref } from 'vue'
import type { Project } from '@/components/dashboard/ProjectRow.vue'

const STORAGE_KEY = 'monogram-projects'

function loadProjects(): Project[] {
  if (typeof window === 'undefined') {
    return []
  }

  const raw = window.localStorage.getItem(STORAGE_KEY)
  if (!raw) {
    return []
  }

  try {
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) {
      return []
    }

    return parsed.filter((item): item is Project => {
      return (
        typeof item?.id === 'string'
        && typeof item?.name === 'string'
        && typeof item?.updatedAt === 'string'
        && (item?.status === 'converted' || item?.status === 'processing' || item?.status === 'failed')
      )
    })
  } catch {
    return []
  }
}

const projectsState = ref<Project[]>(loadProjects())

function persistProjects() {
  if (typeof window === 'undefined') {
    return
  }

  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(projectsState.value))
}

export function useProjects() {
  function addConvertedProject(name: string, thumbnail?: string) {
    const project: Project = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      name: name.trim() || 'Untitled conversion',
      updatedAt: new Date().toLocaleString(),
      status: 'converted',
      thumbnail,
    }

    projectsState.value = [project, ...projectsState.value].slice(0, 50)
    persistProjects()
  }

  return {
    projects: readonly(projectsState),
    addConvertedProject,
  }
}
