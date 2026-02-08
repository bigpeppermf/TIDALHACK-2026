import { computed, ref } from 'vue'
import type { AddConvertedProjectInput, ProjectRecord } from '@/types/project'

const STORAGE_KEY = 'monogram-projects'
const API_BASE = '/api/tex'

interface TexListItem {
  id: string
  filename: string
  created_at: string
}

interface TexDetail {
  id: string
  filename: string
  latex: string
  created_at: string
  updated_at: string
}

let remoteLoadPromise: Promise<void> | null = null
const projectsState = ref<ProjectRecord[]>(loadProjects())

function nowIso(): string {
  return new Date().toISOString()
}

function toDisplayTime(isoString: string): string {
  const parsed = new Date(isoString)
  if (Number.isNaN(parsed.getTime())) {
    return new Date().toLocaleString()
  }
  return parsed.toLocaleString()
}

function filenameFromProjectName(name: string): string {
  const trimmed = name.trim()
  if (!trimmed) return 'main.tex'
  return trimmed.endsWith('.tex') ? trimmed : `${trimmed}.tex`
}

function loadProjects(): ProjectRecord[] {
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
    return parsed.filter((item): item is ProjectRecord => {
      return (
        typeof item?.id === 'string'
        && typeof item?.name === 'string'
        && typeof item?.updatedAt === 'string'
        && typeof item?.updatedAtIso === 'string'
        && (item?.status === 'converted' || item?.status === 'processing' || item?.status === 'failed')
        && typeof item?.latex === 'string'
      )
    })
  } catch {
    return []
  }
}

function persistProjects() {
  if (typeof window === 'undefined') {
    return
  }
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(projectsState.value))
}

function listItemToProject(item: TexListItem): ProjectRecord {
  return {
    id: item.id,
    name: item.filename.replace(/\.tex$/i, ''),
    updatedAt: toDisplayTime(item.created_at),
    updatedAtIso: item.created_at,
    status: 'converted',
    latex: '',
    sourceFilename: item.filename,
    sourceKind: 'unknown',
    ownerId: null,
  }
}

function detailToProject(detail: TexDetail): ProjectRecord {
  return {
    id: detail.id,
    name: detail.filename.replace(/\.tex$/i, ''),
    updatedAt: toDisplayTime(detail.updated_at || detail.created_at),
    updatedAtIso: detail.updated_at || detail.created_at || nowIso(),
    status: 'converted',
    latex: detail.latex,
    sourceFilename: detail.filename,
    sourceKind: 'unknown',
    ownerId: null,
  }
}

function upsertProject(project: ProjectRecord) {
  const index = projectsState.value.findIndex((existing) => existing.id === project.id)
  if (index === -1) {
    projectsState.value = [project, ...projectsState.value].slice(0, 100)
  } else {
    projectsState.value[index] = { ...projectsState.value[index], ...project }
    projectsState.value = [...projectsState.value]
  }
  persistProjects()
}

export function useProjects(ownerId?: string | null) {
  const projects = computed(() => {
    if (!ownerId) return projectsState.value
    return projectsState.value.filter((project) => project.ownerId === ownerId)
  })

  async function fetchRecentProjects(limit = 25): Promise<void> {
    const response = await fetch(`${API_BASE}?limit=${limit}`)
    if (!response.ok) {
      throw new Error('Failed to fetch recent tex files')
    }
    const data = (await response.json()) as TexListItem[]
    if (!Array.isArray(data)) {
      throw new Error('Unexpected tex list payload')
    }

    const mapped = data.map(listItemToProject)
    const detailsById = new Map(projectsState.value.map((project) => [project.id, project]))
    const merged = mapped.map((project) => {
      const existing = detailsById.get(project.id)
      return existing?.latex
        ? { ...project, latex: existing.latex, updatedAt: existing.updatedAt, updatedAtIso: existing.updatedAtIso }
        : project
    })

    projectsState.value = merged
    persistProjects()
  }

  async function ensureRemoteProjectsLoaded(): Promise<void> {
    if (remoteLoadPromise) {
      await remoteLoadPromise
      return
    }

    remoteLoadPromise = fetchRecentProjects().finally(() => {
      remoteLoadPromise = null
    })
    await remoteLoadPromise
  }

  function getProjectById(id: string): ProjectRecord | undefined {
    return projectsState.value.find((project) => project.id === id)
  }

  async function fetchProjectById(id: string): Promise<ProjectRecord | undefined> {
    const response = await fetch(`${API_BASE}/${encodeURIComponent(id)}`)
    if (response.status === 404) {
      return undefined
    }
    if (!response.ok) {
      throw new Error('Failed to fetch tex file details')
    }

    const detail = (await response.json()) as TexDetail
    const mapped = detailToProject(detail)
    upsertProject(mapped)
    return mapped
  }

  async function addConvertedProject(input: AddConvertedProjectInput): Promise<ProjectRecord> {
    const payload = {
      filename: filenameFromProjectName(input.sourceFilename ?? input.name),
      latex: input.latex,
    }

    try {
      const response = await fetch(API_BASE, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error('Failed to create tex file')
      }

      const created = (await response.json()) as { id: string; filename: string; created_at: string }
      const project: ProjectRecord = {
        id: created.id,
        name: created.filename.replace(/\.tex$/i, ''),
        updatedAt: toDisplayTime(created.created_at),
        updatedAtIso: created.created_at,
        status: 'converted',
        thumbnail: input.thumbnail,
        latex: input.latex,
        sourceFilename: created.filename,
        sourceKind: input.sourceKind ?? 'unknown',
        ownerId: input.ownerId ?? null,
      }
      upsertProject(project)
      return project
    } catch {
      const timestamp = nowIso()
      const localFallback: ProjectRecord = {
        id: `local-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        name: input.name.trim() || 'Untitled conversion',
        updatedAt: toDisplayTime(timestamp),
        updatedAtIso: timestamp,
        status: 'converted',
        thumbnail: input.thumbnail,
        latex: input.latex,
        sourceFilename: filenameFromProjectName(input.sourceFilename ?? input.name),
        sourceKind: input.sourceKind ?? 'unknown',
        ownerId: input.ownerId ?? null,
      }
      upsertProject(localFallback)
      return localFallback
    }
  }

  async function updateProjectLatex(id: string, latex: string): Promise<boolean> {
    const target = projectsState.value.find((project) => project.id === id)
    if (!target) return false

    const timestamp = nowIso()
    target.latex = latex
    target.updatedAtIso = timestamp
    target.updatedAt = toDisplayTime(timestamp)
    persistProjects()

    if (id.startsWith('local-')) {
      return true
    }

    try {
      const response = await fetch(`${API_BASE}/${encodeURIComponent(id)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filename: target.sourceFilename ?? filenameFromProjectName(target.name),
          latex,
        }),
      })
      return response.ok
    } catch {
      return false
    }
  }

  return {
    projects,
    addConvertedProject,
    ensureRemoteProjectsLoaded,
    fetchProjectById,
    fetchRecentProjects,
    getProjectById,
    updateProjectLatex,
  }
}
