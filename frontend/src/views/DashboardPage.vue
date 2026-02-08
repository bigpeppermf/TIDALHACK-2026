<script setup lang="ts">
import { useAuth } from '@clerk/vue'
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import katex from 'katex'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import EmptyState from '@/components/dashboard/EmptyState.vue'
import ProjectRow from '@/components/dashboard/ProjectRow.vue'
import { AUTH_SESSION_EXPIRED_MESSAGE, useProjects } from '@/composables/useProjects'
import { useExport } from '@/composables/useExport'

const DEFAULT_LATEX = `\\documentclass{article}
\\usepackage{amsmath}
\\begin{document}
\\section{Untitled}
Start writing here.
\\end{document}`

const router = useRouter()
const { isLoaded, isSignedIn, userId } = useAuth()
const { projects, addConvertedProject, deleteProject, ensureRemoteProjectsLoaded, fetchProjectById } = useProjects(userId)
const { exportFile, exporting: exportingFile } = useExport()
const authErrorMessage = ref('')
const deletingId = ref<string | null>(null)
const selectedProjectId = ref<string | null>(null)
const showPreviewDownload = ref(false)

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
        : ''
    })
  },
  { immediate: true },
)

// Auto-select first project when projects load
watch(projects, (list) => {
  if (list.length > 0 && !selectedProjectId.value) {
    selectedProjectId.value = list[0].id
  }
}, { immediate: true })

const selectedProject = computed(() => {
  if (!selectedProjectId.value) return null
  return projects.value.find((p) => p.id === selectedProjectId.value) ?? null
})

function handleSelectProject(id: string) {
  selectedProjectId.value = id
  // Fetch full project data if latex is missing
  const project = projects.value.find((p) => p.id === id)
  if (project && !project.latex && !id.startsWith('local-')) {
    void fetchProjectById(id)
  }
}

function handleUpload() {
  router.push('/convert')
}

async function handleNewProject() {
  const project = await addConvertedProject({
    name: 'Untitled project',
    latex: DEFAULT_LATEX,
    sourceFilename: 'main.tex',
    sourceKind: 'unknown',
    ownerId: userId.value ?? null,
  })
  router.push({ path: '/editor', query: { projectId: project.id } })
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

async function handleDelete(id: string) {
  deletingId.value = id
  try {
    await deleteProject(id)
    if (selectedProjectId.value === id) {
      selectedProjectId.value = projects.value[0]?.id ?? null
    }
  } catch {
    // silently fail
  } finally {
    deletingId.value = null
  }
}

async function handlePreviewDownload(format: 'tex' | 'html' | 'pdf') {
  showPreviewDownload.value = false
  const project = selectedProject.value
  if (!project) return

  if (format === 'tex') {
    const blob = new Blob([project.latex || ''], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${project.name || 'project'}.tex`
    a.click()
    URL.revokeObjectURL(url)
    return
  }

  let exportId = project.id

  // Auto-promote local projects before export
  if (project.id.startsWith('local-')) {
    try {
      const promoted = await addConvertedProject({
        name: project.name || 'Untitled project',
        latex: project.latex || '',
        sourceFilename: project.name || 'main.tex',
        sourceKind: 'unknown',
        ownerId: userId.value ?? null,
      })
      if (promoted.id.startsWith('local-')) {
        authErrorMessage.value = 'Sign in to enable HTML/PDF export.'
        setTimeout(() => { if (authErrorMessage.value.includes('Sign in')) authErrorMessage.value = '' }, 4000)
        return
      }
      exportId = promoted.id
    } catch {
      authErrorMessage.value = 'Could not save project. Sign in and try again.'
      setTimeout(() => { if (authErrorMessage.value.includes('Could not')) authErrorMessage.value = '' }, 4000)
      return
    }
  }

  try {
    await exportFile({
      format,
      texFileId: exportId,
      latex: project.latex,
      filename: project.name || 'monogram-output',
    })
  } catch {
    authErrorMessage.value = 'Export failed.'
    setTimeout(() => { if (authErrorMessage.value === 'Export failed.') authErrorMessage.value = '' }, 4000)
  }
}

// LaTeX preview rendering (same logic as EditorPage)
const KATEX_MACROS: Record<string, string> = {
  '\\R': '\\mathbb{R}',
  '\\N': '\\mathbb{N}',
  '\\Z': '\\mathbb{Z}',
  '\\Q': '\\mathbb{Q}',
  '\\C': '\\mathbb{C}',
  '\\dx': '\\,dx',
  '\\dy': '\\,dy',
  '\\dt': '\\,dt',
  '\\ds': '\\,ds',
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function safeMathRender(tex: string, displayMode = false): string {
  try {
    let cleanedTex = tex.trim()
    cleanedTex = cleanedTex.replace(/\\MATH/g, '')
    cleanedTex = cleanedTex.replace(/\\begin\{scope\}/g, '')
    cleanedTex = cleanedTex.replace(/\\end\{scope\}/g, '')
    cleanedTex = cleanedTex.replace(/\\foreach/g, '%')
    cleanedTex = cleanedTex.replace(/\\label\{[^}]*\}/g, '')
    cleanedTex = cleanedTex.replace(/\\nonumber/g, '')
    cleanedTex = cleanedTex.replace(/\\notag/g, '')
    cleanedTex = cleanedTex.replace(/\\allowbreak/g, '')

    return katex.renderToString(cleanedTex, {
      displayMode,
      throwOnError: false,
      strict: false,
      output: 'htmlAndMathml',
      errorColor: '#000',
      trust: false,
      macros: KATEX_MACROS,
    })
  } catch {
    const text = tex.trim().replace(/\\\\/g, '\n').replace(/\$/g, '').replace(/\{/g, '(').replace(/\}/g, ')').slice(0, 120)
    return displayMode
      ? `<div class="my-6 overflow-x-auto rounded border border-black/10 bg-black/5 p-3 font-mono text-xs text-black">${escapeHtml(text)}</div>`
      : `<code class="rounded border border-black/10 bg-black/5 px-1.5 py-0.5 font-mono text-xs text-black">${escapeHtml(text)}</code>`
  }
}

const previewHtml = computed(() => {
  const project = selectedProject.value
  if (!project?.latex) return '<p class="text-muted-foreground text-sm">Select a project to preview.</p>'

  let src = project.latex
  const safeBlocks: string[] = []
  const insertSafeBlock = (content: string): string => {
    const token = `@@SAFE_BLOCK_${safeBlocks.length}@@`
    safeBlocks.push(content)
    return token
  }

  const beginDoc = src.indexOf('\\begin{document}')
  const endDoc = src.indexOf('\\end{document}')
  if (beginDoc !== -1 && endDoc !== -1) {
    src = src.slice(beginDoc + '\\begin{document}'.length, endDoc).trim()
  }

  src = src.replace(/\\MATH/g, 'MATH')
  src = src.replace(/\\dx/g, 'dx')
  src = src.replace(/\\frac\{([^}]*)\}\[([^\]]*)\]\[([^\]]*)\]/g, '\\frac{$1}{$2}')

  src = src.replace(/\\section\*?\{([^}]*)\}/g, (_m, title) =>
    insertSafeBlock(`<h2 class="text-2xl font-bold mt-8 mb-4">${escapeHtml(title)}</h2>`))
  src = src.replace(/\\subsection\*?\{([^}]*)\}/g, (_m, title) =>
    insertSafeBlock(`<h3 class="text-xl font-semibold mt-6 mb-3">${escapeHtml(title)}</h3>`))
  src = src.replace(/\\subsubsection\*?\{([^}]*)\}/g, (_m, title) =>
    insertSafeBlock(`<h4 class="text-lg font-medium mt-4 mb-2">${escapeHtml(title)}</h4>`))

  src = src.replace(/\\\[([\s\S]*?)\\\]/g, (_m, tex) =>
    insertSafeBlock(`<div class="my-6 overflow-x-auto flex justify-center">${safeMathRender(tex, true)}</div>`))
  src = src.replace(/\$\$([\s\S]*?)\$\$/g, (_m, tex) =>
    insertSafeBlock(`<div class="my-6 overflow-x-auto flex justify-center">${safeMathRender(tex, true)}</div>`))
  src = src.replace(/\\begin\{(align\*?|equation\*?|gather\*?|multline\*?|split|flalign\*?|eqnarray\*?)\}([\s\S]*?)\\end\{\1\}/g, (_m, env, tex) => {
    let wrapped = tex
    if (env.startsWith('align') || env === 'split' || env.startsWith('flalign') || env.startsWith('eqnarray')) {
      wrapped = `\\begin{aligned}${tex}\\end{aligned}`
    } else if (env.startsWith('gather') || env.startsWith('multline')) {
      wrapped = `\\begin{gathered}${tex}\\end{gathered}`
    } else if (tex.includes('\\\\')) {
      wrapped = `\\begin{gathered}${tex}\\end{gathered}`
    }
    return insertSafeBlock(`<div class="my-6 overflow-x-auto flex justify-center">${safeMathRender(wrapped, true)}</div>`)
  })
  src = src.replace(/\\begin\{(cases|pmatrix|bmatrix|vmatrix|Vmatrix|smallmatrix)\}([\s\S]*?)\\end\{\1\}/g, (_m, env, tex) => {
    const wrapped = `\\begin{${env}}${tex}\\end{${env}}`
    return insertSafeBlock(`<div class="my-6 overflow-x-auto flex justify-center">${safeMathRender(wrapped, true)}</div>`)
  })
  src = src.replace(/\$([^$]+?)\$/g, (_m, tex) => insertSafeBlock(safeMathRender(tex, false)))

  src = src.replace(/\\begin\{itemize\}([\s\S]*?)\\end\{itemize\}/g, (_m, items) => {
    const processedItems = items.split('\\item').filter((item: string) => item.trim()).map((item: string) => `<li class="ml-6 mb-2">${item.trim()}</li>`).join('')
    return insertSafeBlock(`<ul class="list-disc my-4">${processedItems}</ul>`)
  })
  src = src.replace(/\\begin\{enumerate\}([\s\S]*?)\\end\{enumerate\}/g, (_m, items) => {
    const processedItems = items.split('\\item').filter((item: string) => item.trim()).map((item: string) => `<li class="ml-6 mb-2">${item.trim()}</li>`).join('')
    return insertSafeBlock(`<ol class="list-decimal my-4">${processedItems}</ol>`)
  })

  src = src.replace(/\\textbf\{([^}]*)\}/g, (_m, text) => insertSafeBlock(`<strong>${escapeHtml(text)}</strong>`))
  src = src.replace(/\\textit\{([^}]*)\}/g, (_m, text) => insertSafeBlock(`<em>${escapeHtml(text)}</em>`))
  src = src.replace(/\\emph\{([^}]*)\}/g, (_m, text) => insertSafeBlock(`<em>${escapeHtml(text)}</em>`))
  src = src.replace(/\\texttt\{([^}]*)\}/g, (_m, text) => insertSafeBlock(`<code class="font-mono text-sm">${escapeHtml(text)}</code>`))
  src = src.replace(/\\underline\{([^}]*)\}/g, (_m, text) => insertSafeBlock(`<span class="underline">${escapeHtml(text)}</span>`))

  src = src.replace(/\\newpage/g, insertSafeBlock('<hr class="my-8 border-border" />'))
  src = src.replace(/\\(vspace|hspace)\{[^}]*\}/g, '')
  src = src.replace(/\\(hline|noindent|clearpage|pagebreak)/g, '')
  src = src.replace(/\\\\(?!\[)/g, insertSafeBlock('<br />'))

  src = escapeHtml(src)

  const paragraphs = src.split(/\n\s*\n/)
  src = paragraphs.map((p) => {
    const trimmed = p.trim()
    if (!trimmed) return ''
    return `<p class="mb-4 text-base leading-relaxed">${trimmed.replace(/\n/g, ' ')}</p>`
  }).join('')

  let previous = ''
  while (src !== previous) {
    previous = src
    src = src.replace(/@@SAFE_BLOCK_(\d+)@@/g, (_m, idx) => safeBlocks[Number(idx)] ?? '')
  }

  return src
})
</script>

<template>
  <div class="relative min-h-screen bg-background">
    <AppNavbar />
    <div class="fixed inset-0 bg-grid-pattern opacity-20" />

    <main class="relative z-10 mx-auto max-w-7xl px-6 pt-20 pb-12 md:pr-28">
      <!-- Page header -->
      <div class="mb-10 flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div class="mb-3 flex items-center gap-3">
            <div class="h-px w-8 bg-primary" />
            <span class="text-[11px] font-semibold tracking-[0.3em] uppercase text-primary">Projects</span>
          </div>
          <h1 class="text-3xl font-bold text-foreground">Dashboard</h1>
          <p class="mt-2 text-[13px] tracking-wide text-muted-foreground/70">Your recent conversions and projects.</p>
        </div>
        <div class="flex items-center gap-3">
          <button
            class="inline-flex items-center gap-2 rounded-sm border px-5 py-2 text-[11px] font-semibold tracking-[0.12em] uppercase transition-all duration-300 hover:text-foreground"
            style="background: transparent; color: hsl(var(--muted-foreground)); border-color: hsl(var(--border))"
            @click="handleNewProject"
          >
            New Project
          </button>
          <button
            class="inline-flex items-center gap-2 rounded-sm bg-primary px-5 py-2 text-[11px] font-semibold tracking-[0.12em] uppercase text-primary-foreground transition-all duration-300 hover:opacity-90"
            @click="handleUpload"
          >
            New Conversion
          </button>
        </div>
      </div>
      <p v-if="authErrorMessage" class="mb-4 rounded-sm border border-destructive/30 bg-destructive/10 px-4 py-2 text-[12px] text-destructive">{{ authErrorMessage }}</p>

      <!-- Empty state -->
      <EmptyState v-if="projects.length === 0" @upload="handleUpload" />

      <!-- Split layout: project list + preview -->
      <div v-else class="flex gap-6">
        <!-- Left: Project list -->
        <section class="w-full lg:w-[45%]">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-[13px] font-semibold tracking-[0.15em] uppercase text-foreground">Recent Projects</h2>
            <span class="text-[11px] tracking-wide text-muted-foreground/50">{{ projects.length }} project{{ projects.length === 1 ? '' : 's' }}</span>
          </div>
          <div class="space-y-2">
            <div
              v-for="project in projects"
              :key="project.id"
              :class="[
                'cursor-pointer rounded-lg transition-all duration-300',
                selectedProjectId === project.id ? 'ring-1 ring-primary/50' : '',
              ]"
              @click="handleSelectProject(project.id)"
            >
              <ProjectRow
                :project="project"
                :deleting="deletingId === project.id"
                @view="handleView"
                @edit="handleEdit"
                @retry="handleRetry"
                @delete="handleDelete"
              />
            </div>
          </div>
        </section>

        <!-- Right: Preview panel (sticky) -->
        <aside class="hidden lg:block lg:w-[55%]">
          <div class="sticky top-24">
            <div
              class="flex flex-col overflow-hidden rounded-xl border"
              style="background: hsl(var(--card) / 0.6); border-color: hsl(var(--border) / 0.4); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px)"
            >
              <!-- Preview header -->
              <div class="flex items-center justify-between px-5 py-3" style="border-bottom: 1px solid hsl(var(--border) / 0.3)">
                <div class="flex items-center gap-2">
                  <span class="text-[11px] font-semibold tracking-[0.15em] uppercase text-muted-foreground/60">Preview</span>
                  <span v-if="selectedProject" class="truncate text-[11px] tracking-wide text-muted-foreground/40">
                    — {{ selectedProject.name }}
                  </span>
                </div>
                <div class="flex items-center gap-2">
                  <!-- Download dropdown -->
                  <div class="relative">
                    <button
                      type="button"
                      class="inline-flex items-center gap-1.5 rounded-sm border px-3 py-1.5 text-[10px] font-semibold tracking-[0.1em] uppercase transition-all duration-300"
                      style="background: transparent; color: hsl(var(--muted-foreground)); border-color: hsl(var(--border) / 0.6)"
                      :disabled="!selectedProject || exportingFile"
                      @click="showPreviewDownload = !showPreviewDownload"
                    >
                      {{ exportingFile ? 'Exporting...' : 'Download' }}
                      <svg class="h-3 w-3 opacity-50" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="m6 9 6 6 6-6" />
                      </svg>
                    </button>
                    <div
                      v-if="showPreviewDownload"
                      class="absolute right-0 top-full z-10 mt-1 w-36 overflow-hidden rounded-sm border shadow-xl"
                      style="background: hsl(var(--card) / 0.9); border-color: hsl(var(--border) / 0.4); backdrop-filter: blur(16px)"
                    >
                      <button
                        type="button"
                        class="flex w-full items-center gap-2 px-3 py-2 text-left text-[10px] font-medium tracking-[0.1em] uppercase text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
                        @click="handlePreviewDownload('tex')"
                      >
                        .tex
                      </button>
                      <button
                        type="button"
                        class="flex w-full items-center gap-2 px-3 py-2 text-left text-[10px] font-medium tracking-[0.1em] uppercase text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
                        @click="handlePreviewDownload('html')"
                      >
                        .html
                      </button>
                      <button
                        type="button"
                        class="flex w-full items-center gap-2 px-3 py-2 text-left text-[10px] font-medium tracking-[0.1em] uppercase text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
                        @click="handlePreviewDownload('pdf')"
                      >
                        .pdf
                      </button>
                    </div>
                  </div>
                  <!-- Open in editor -->
                  <button
                    v-if="selectedProject"
                    type="button"
                    class="rounded-sm bg-primary px-4 py-1.5 text-[10px] font-semibold tracking-[0.1em] uppercase text-primary-foreground transition-all duration-300 hover:opacity-90"
                    @click="handleEdit(selectedProject.id)"
                  >
                    Open in Editor
                  </button>
                </div>
              </div>

              <!-- Preview content -->
              <div class="h-[calc(100vh-16rem)] overflow-y-auto bg-white p-6">
                <div
                  class="latex-document-preview mx-auto max-w-none text-black"
                  v-html="previewHtml"
                />
              </div>
            </div>
          </div>
        </aside>
      </div>
    </main>
  </div>
</template>
