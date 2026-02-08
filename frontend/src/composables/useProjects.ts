import { useAuth } from '@clerk/vue'
import { computed, ref, toValue, watch } from 'vue'
import type { MaybeRefOrGetter } from 'vue'
import type { AddConvertedProjectInput, ProjectRecord } from '@/types/project'

const STORAGE_KEY = 'monogram-projects'
const API_BASE = '/api/tex'
export const AUTH_SESSION_EXPIRED_MESSAGE = 'Your session expired. Please sign in again.'

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

export interface ProjectFileMeta {
  path: string
  kind: 'tex' | 'bib' | 'image' | 'dir' | 'asset'
  editable: boolean
  stored: boolean
}

interface ProjectFilesResponse {
  project_id: string
  files: Array<{
    path: string
    kind: string
    editable?: boolean
    stored?: boolean
  }>
}

interface CompileResponse {
  success: boolean
  error?: string
  detail?: string
  project_id?: string
  filename?: string
  pdf_base64?: string
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

function decodeBase64ToBytes(encoded: string): Uint8Array {
  const binary = window.atob(encoded)
  const output = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i += 1) {
    output[i] = binary.charCodeAt(i)
  }
  return output
}

function normalizeProjectFileKind(kind: string): ProjectFileMeta['kind'] {
  if (kind === 'tex' || kind === 'bib' || kind === 'image' || kind === 'dir') {
    return kind
  }
  return 'asset'
}

function isAuthStatus(status: number): boolean {
  return status === 401 || status === 403
}

export function useProjects(ownerId?: MaybeRefOrGetter<string | null | undefined>) {
  const clerkGetToken = ref<(() => Promise<string | null>) | null>(null)
  const clerkUserId = ref<string | null>(null)

  try {
    const auth = useAuth()
    watch(
      () => toValue(auth.getToken as unknown as MaybeRefOrGetter<(() => Promise<string | null>) | undefined>),
      (next) => {
        clerkGetToken.value = next ?? null
      },
      { immediate: true },
    )
    watch(
      () => toValue(auth.userId as unknown as MaybeRefOrGetter<string | null | undefined>),
      (next) => {
        clerkUserId.value = next ?? null
      },
      { immediate: true },
    )
  } catch {
    clerkGetToken.value = null
  }

  const resolvedOwnerId = computed(() => {
    const explicit = toValue(ownerId)
    return explicit ?? clerkUserId.value ?? null
  })

  const projects = computed(() => {
    if (!resolvedOwnerId.value) return []
    return projectsState.value.filter((project) => project.ownerId === resolvedOwnerId.value)
  })

  async function authFetch(url: string, init?: RequestInit): Promise<Response> {
    const headers = new Headers(init?.headers)
    if (clerkGetToken.value) {
      const token = await clerkGetToken.value()
      if (token) {
        headers.set('Authorization', `Bearer ${token}`)
      }
    }
    return fetch(url, { ...init, headers })
  }

  async function fetchRecentProjects(limit = 25): Promise<void> {
    const response = await authFetch(`${API_BASE}?limit=${limit}`)
    if (isAuthStatus(response.status)) {
      throw new Error(AUTH_SESSION_EXPIRED_MESSAGE)
    }
    if (!response.ok) {
      throw new Error('Failed to fetch recent tex files')
    }
    const data = (await response.json()) as TexListItem[]
    if (!Array.isArray(data)) {
      throw new Error('Unexpected tex list payload')
    }

    const mapped = data.map((item) => ({
      ...listItemToProject(item),
      ownerId: resolvedOwnerId.value,
    }))
    const detailsById = new Map(projectsState.value.map((project) => [project.id, project]))
    const merged = mapped.map((project) => {
      const existing = detailsById.get(project.id)
      return existing?.latex
        ? { ...project, latex: existing.latex, updatedAt: existing.updatedAt, updatedAtIso: existing.updatedAtIso }
        : project
    })
    const localDrafts = projectsState.value.filter((project) => {
      return project.id.startsWith('local-') && project.ownerId === resolvedOwnerId.value
    })

    projectsState.value = [...merged, ...localDrafts]
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
    const response = await authFetch(`${API_BASE}/${encodeURIComponent(id)}`)
    if (response.status === 404) {
      return undefined
    }
    if (isAuthStatus(response.status)) {
      throw new Error(AUTH_SESSION_EXPIRED_MESSAGE)
    }
    if (!response.ok) {
      throw new Error('Failed to fetch tex file details')
    }

    const detail = (await response.json()) as TexDetail
    const mapped = {
      ...detailToProject(detail),
      ownerId: resolvedOwnerId.value,
    }
    upsertProject(mapped)
    return mapped
  }

  async function addConvertedProject(input: AddConvertedProjectInput): Promise<ProjectRecord> {
    const payload = {
      filename: filenameFromProjectName(input.sourceFilename ?? input.name),
      latex: input.latex,
    }

    try {
      const response = await authFetch(API_BASE, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        if (isAuthStatus(response.status)) {
          throw new Error(AUTH_SESSION_EXPIRED_MESSAGE)
        }
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
        ownerId: input.ownerId ?? resolvedOwnerId.value ?? null,
      }
      upsertProject(project)
      return project
    } catch (error) {
      if (error instanceof Error && error.message === AUTH_SESSION_EXPIRED_MESSAGE) {
        throw error
      }
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
        ownerId: input.ownerId ?? resolvedOwnerId.value ?? null,
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
      const response = await authFetch(`${API_BASE}/${encodeURIComponent(id)}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filename: target.sourceFilename ?? filenameFromProjectName(target.name),
          latex,
        }),
      })
      if (isAuthStatus(response.status)) {
        throw new Error(AUTH_SESSION_EXPIRED_MESSAGE)
      }
      return response.ok
    } catch (error) {
      if (error instanceof Error && error.message === AUTH_SESSION_EXPIRED_MESSAGE) {
        throw error
      }
      return false
    }
  }

  async function fetchProjectFiles(id: string): Promise<ProjectFileMeta[] | null> {
    if (id.startsWith('local-')) {
      return null
    }

    const response = await authFetch(`${API_BASE}/${encodeURIComponent(id)}/files`)
    if (response.status === 404) {
      return null
    }
    if (isAuthStatus(response.status)) {
      throw new Error(AUTH_SESSION_EXPIRED_MESSAGE)
    }
    if (!response.ok) {
      throw new Error('Failed to fetch project files')
    }

    const payload = (await response.json()) as ProjectFilesResponse
    if (!Array.isArray(payload.files)) {
      return null
    }

    return payload.files.map((file) => ({
      path: file.path,
      kind: normalizeProjectFileKind(file.kind),
      editable: Boolean(file.editable),
      stored: Boolean(file.stored),
    }))
  }

  async function compileProjectPdf(id: string): Promise<{ ok: true; pdfData: Uint8Array } | { ok: false; error: string }> {
    if (id.startsWith('local-')) {
      return { ok: false, error: 'Remote project required for PDF compile.' }
    }

    const response = await authFetch(`${API_BASE}/${encodeURIComponent(id)}/compile`, {
      method: 'POST',
    })
    if (isAuthStatus(response.status)) {
      return { ok: false, error: AUTH_SESSION_EXPIRED_MESSAGE }
    }
    const payload = (await response.json()) as CompileResponse

    if (!response.ok || !payload.success || !payload.pdf_base64) {
      const message = payload.detail || payload.error || 'Compile failed'
      return { ok: false, error: message }
    }

    return {
      ok: true,
      pdfData: decodeBase64ToBytes(payload.pdf_base64),
    }
  }

  return {
    projects,
    addConvertedProject,
    compileProjectPdf,
    ensureRemoteProjectsLoaded,
    fetchProjectFiles,
    fetchProjectById,
    fetchRecentProjects,
    getProjectById,
    updateProjectLatex,
  }
}
