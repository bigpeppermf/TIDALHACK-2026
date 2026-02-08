<script setup lang="ts">
import { useAuth } from '@clerk/vue'
import { computed, onUnmounted, ref, watch } from 'vue'
import katex from 'katex'
import { useRoute, useRouter } from 'vue-router'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import LatexEditorPanel from '@/components/convert/LatexEditorPanel.vue'
import { AUTH_SESSION_EXPIRED_MESSAGE, useProjects, type ProjectFileMeta } from '@/composables/useProjects'
import { useExport } from '@/composables/useExport'

const DEFAULT_LATEX = `\\documentclass{article}
\\usepackage{amsmath}
\\begin{document}
\\section{Monogram Editor}
Type your LaTeX here and use Preview to inspect output.

Inline math: $E = mc^2$

\\[
\\int_0^1 x^2 \\, dx = \\frac{1}{3}
\\]
\\end{document}`

type SaveState = 'idle' | 'saving' | 'saved' | 'error'
type CompileState = 'idle' | 'dirty' | 'compiling' | 'compiled' | 'error'
type ShareState = 'idle' | 'shared' | 'error'

type EditorFileItem = {
  path: string
  name: string
  kind: 'tex' | 'dir' | 'bib' | 'image' | 'asset'
  editable: boolean
  active?: boolean
}

type PendingEditorDraft = {
  latex: string
  name?: string
  sourceFilename?: string
}

const PENDING_EDITOR_DRAFT_KEY = 'monogram-editor-pending-draft'
const EDITOR_LAST_TARGET_KEY = 'monogram-editor-last-target'

type PendingEditorTarget = {
  projectId?: string
  draft?: PendingEditorDraft
}

const route = useRoute()
const router = useRouter()
const { isLoaded, isSignedIn, userId } = useAuth()
const {
  addConvertedProject,
  compileProjectPdf,
  ensureRemoteProjectsLoaded,
  fetchProjectFiles,
  fetchProjectById,
  getProjectById,
  projects,
  updateProjectLatex,
} = useProjects(userId)

const { exportFile, exporting: exportingFile } = useExport()

const code = ref(DEFAULT_LATEX)
const compiledCode = ref(DEFAULT_LATEX)
const activeTab = ref<'preview' | 'source'>('source')
const zoom = ref(100)
const copied = ref(false)
const currentProjectId = ref<string | null>(null)
const currentProjectName = ref('Untitled project')
const currentSourceFilename = ref<string | null>(null)
const activeFilePath = ref<string | null>(null)
const projectFilesMetadata = ref<ProjectFileMeta[] | null>(null)
const saveState = ref<SaveState>('idle')
const compileState = ref<CompileState>('compiled')
const compileErrorMessage = ref('')
const shareState = ref<ShareState>('idle')
const compiledPdfData = ref<Uint8Array | null>(null)
const authErrorMessage = ref('')

const isHydrating = ref(false)
let saveTimer: ReturnType<typeof setTimeout> | null = null
let saveStateTimer: ReturnType<typeof setTimeout> | null = null
let shareTimer: ReturnType<typeof setTimeout> | null = null
let hydrateRequestId = 0
let compileRequestId = 0
let saveRequestId = 0

function setAuthError(message: string) {
  authErrorMessage.value = message
}

function clearAuthError() {
  authErrorMessage.value = ''
}

function autoFixLatexForCompile(input: string): { source: string; changed: boolean } {
  let output = input
  const apply = (next: string) => {
    output = next
  }

  apply(output.replace(/\r\n/g, '\n'))
  apply(output.replace(/\u00a0/g, ' '))
  apply(output.replace(/\t/g, '  '))
  apply(output.replace(/\\MATH/g, 'MATH'))
  apply(output.replace(/\\dx/g, 'dx'))
  apply(output.replace(/\\frac\{([^}]*)\}\[([^\]]*)\]\[([^\]]*)\]/g, '\\frac{$1}{$2}'))
  apply(output.replace(/[“”]/g, '"'))
  apply(output.replace(/[‘’]/g, "'"))

  // Remove common OCR artifacts that break LaTeX compilation.
  apply(output.replace(/[^\x09\x0a\x0d\x20-\x7e]/g, ''))

  if (!/\\end\{document\}/.test(output) && /\\begin\{document\}/.test(output)) {
    apply(`${output.trim()}\n\\end{document}`)
  }

  if (!/\\documentclass/.test(output)) {
    const body = output.trim()
    apply([
      '\\documentclass[12pt]{article}',
      '\\usepackage{amsmath,amssymb,amsfonts}',
      '\\usepackage[utf8]{inputenc}',
      '\\usepackage{geometry}',
      '\\geometry{a4paper, margin=1in}',
      '\\begin{document}',
      body,
      '\\end{document}',
    ].join('\n'))
  }

  return { source: output, changed: output !== input }
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

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
    const text = tex
      .trim()
      .replace(/\\\\/g, '\n')
      .replace(/\$/g, '')
      .replace(/\{/g, '(')
      .replace(/\}/g, ')')
      .slice(0, 120)

    return displayMode
      ? `<div class="my-6 overflow-x-auto rounded border border-black/10 bg-black/5 p-3 font-mono text-xs text-black">${escapeHtml(text)}</div>`
      : `<code class="rounded border border-black/10 bg-black/5 px-1.5 py-0.5 font-mono text-xs text-black">${escapeHtml(text)}</code>`
  }
}

function renderLatexPreview(latex: string): string {
  let src = latex
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

  src = src.replace(/\\section\*?\{([^}]*)\}/g, (_m, title) => {
    return insertSafeBlock(`<h2 class="text-2xl font-bold mt-8 mb-4">${escapeHtml(title)}</h2>`)
  })
  src = src.replace(/\\subsection\*?\{([^}]*)\}/g, (_m, title) => {
    return insertSafeBlock(`<h3 class="text-xl font-semibold mt-6 mb-3">${escapeHtml(title)}</h3>`)
  })
  src = src.replace(/\\subsubsection\*?\{([^}]*)\}/g, (_m, title) => {
    return insertSafeBlock(`<h4 class="text-lg font-medium mt-4 mb-2">${escapeHtml(title)}</h4>`)
  })

  src = src.replace(/\\\[([\s\S]*?)\\\]/g, (_m, tex) => {
    return insertSafeBlock(`<div class="my-6 overflow-x-auto flex justify-center">${safeMathRender(tex, true)}</div>`)
  })
  src = src.replace(/\$\$([\s\S]*?)\$\$/g, (_m, tex) => {
    return insertSafeBlock(`<div class="my-6 overflow-x-auto flex justify-center">${safeMathRender(tex, true)}</div>`)
  })
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
  src = src.replace(/\$([^$]+?)\$/g, (_m, tex) => {
    return insertSafeBlock(safeMathRender(tex, false))
  })

  src = src.replace(/\\begin\{itemize\}([\s\S]*?)\\end\{itemize\}/g, (_m, items) => {
    const processedItems = items
      .split('\\item')
      .filter((item: string) => item.trim())
      .map((item: string) => `<li class="ml-6 mb-2">${item.trim()}</li>`)
      .join('')
    return insertSafeBlock(`<ul class="list-disc my-4">${processedItems}</ul>`)
  })
  src = src.replace(/\\begin\{enumerate\}([\s\S]*?)\\end\{enumerate\}/g, (_m, items) => {
    const processedItems = items
      .split('\\item')
      .filter((item: string) => item.trim())
      .map((item: string) => `<li class="ml-6 mb-2">${item.trim()}</li>`)
      .join('')
    return insertSafeBlock(`<ol class="list-decimal my-4">${processedItems}</ol>`)
  })

  src = src.replace(/\\begin\{center\}([\s\S]*?)\\end\{center\}/g, (_m, content) => {
    return insertSafeBlock(`<div class="my-4 text-center">${content.trim()}</div>`)
  })
  src = src.replace(/\\begin\{quote\}([\s\S]*?)\\end\{quote\}/g, (_m, content) => {
    return insertSafeBlock(`<blockquote class="my-4 border-l-4 border-border pl-4 italic text-muted-foreground">${content.trim()}</blockquote>`)
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
  src = paragraphs
    .map((paragraph) => {
      const trimmed = paragraph.trim()
      if (!trimmed) return ''
      const text = trimmed.replace(/\n/g, ' ')
      return `<p class="mb-4 text-base leading-relaxed">${text}</p>`
    })
    .join('')

  let previous = ''
  while (src !== previous) {
    previous = src
    src = src.replace(/@@SAFE_BLOCK_(\d+)@@/g, (_m, idx) => safeBlocks[Number(idx)] ?? '')
  }

  return src
}

const renderedPreview = computed(() => renderLatexPreview(code.value))

const downloadFilename = computed(() => {
  const source = (currentSourceFilename.value || '').trim()
  if (source.endsWith('.tex')) return source
  const safeName = (currentProjectName.value || 'editor-notes').trim().replace(/\s+/g, '-').toLowerCase()
  return `${safeName || 'editor-notes'}.tex`
})

const routeProjectId = computed(() => {
  const raw = route.query.projectId
  return typeof raw === 'string' && raw ? raw : null
})
const routeWantsDraft = computed(() => route.query.draft === '1')

function consumePendingEditorDraft(): PendingEditorDraft | null {
  if (typeof window === 'undefined') return null
  const raw = window.sessionStorage.getItem(PENDING_EDITOR_DRAFT_KEY)
  if (!raw) return null

  window.sessionStorage.removeItem(PENDING_EDITOR_DRAFT_KEY)
  try {
    const parsed = JSON.parse(raw) as PendingEditorDraft
    if (!parsed?.latex || typeof parsed.latex !== 'string') {
      return null
    }
    return parsed
  } catch {
    return null
  }
}

function consumePendingEditorTarget(): PendingEditorTarget | null {
  if (typeof window === 'undefined') return null
  const raw = window.sessionStorage.getItem(EDITOR_LAST_TARGET_KEY)
  if (!raw) return null

  window.sessionStorage.removeItem(EDITOR_LAST_TARGET_KEY)
  try {
    const parsed = JSON.parse(raw) as PendingEditorTarget
    if (!parsed || typeof parsed !== 'object') return null
    if (parsed.projectId && typeof parsed.projectId !== 'string') return null
    if (parsed.draft && typeof parsed.draft?.latex !== 'string') return null
    return parsed
  } catch {
    return null
  }
}

const pendingEditorTarget = ref<PendingEditorTarget | null>(consumePendingEditorTarget())

const editorFiles = computed<EditorFileItem[]>(() => {
  if (!projectFilesMetadata.value || projectFilesMetadata.value.length === 0) {
    return []
  }

  return projectFilesMetadata.value.map((file) => ({
    path: file.path,
    name: file.path.split('/').pop() || file.path,
    kind: file.kind,
    editable: file.editable,
    active: activeFilePath.value === file.path,
  }))
})

const activeFile = computed<EditorFileItem | null>(() => {
  if (!activeFilePath.value) return null
  return editorFiles.value.find((file) => file.path === activeFilePath.value) ?? null
})

const isActiveFileEditable = computed(() => {
  if (!projectFilesMetadata.value || projectFilesMetadata.value.length === 0) {
    return true
  }
  return Boolean(activeFile.value?.editable && activeFile.value?.kind === 'tex')
})

const activeSourceFilename = computed(() => {
  if (activeFile.value?.path) {
    return activeFile.value.path
  }
  return currentSourceFilename.value || undefined
})

const visibleCode = computed(() => {
  if (isActiveFileEditable.value) {
    return code.value
  }

  if (activeFile.value) {
    return [
      `% ${activeFile.value.path}`,
      `% This file is referenced by the project graph.`,
      `% Editing is currently supported for stored .tex source only.`,
    ].join('\n')
  }

  return code.value
})

const saveStatusLabel = computed(() => {
  if (saveState.value === 'saving') return 'Saving...'
  if (saveState.value === 'saved') return 'Saved'
  if (saveState.value === 'error') return 'Save failed'
  return 'Auto Save'
})

const compileStatusLabel = computed(() => {
  if (compileState.value === 'compiling') return 'Compiling'
  if (compileState.value === 'compiled') return 'Compiled'
  if (compileState.value === 'dirty') return 'Needs recompile'
  if (compileState.value === 'error') return 'Compile failed'
  return 'Ready'
})

const shareLabel = computed(() => {
  if (shareState.value === 'shared') return 'Shared'
  if (shareState.value === 'error') return 'Share failed'
  return 'Share'
})

async function compilePreview() {
  const requestId = ++compileRequestId
  let projectId = currentProjectId.value
  let sourceSnapshot = code.value

  if (!projectId) {
    compileState.value = 'error'
    compileErrorMessage.value = 'No active project selected.'
    compiledPdfData.value = null
    return
  }

  compileState.value = 'compiling'
  compileErrorMessage.value = ''

  const fixed = autoFixLatexForCompile(sourceSnapshot)
  if (fixed.changed) {
    sourceSnapshot = fixed.source
    code.value = fixed.source
  }

  if (projectId.startsWith('local-')) {
    try {
      const promoted = await addConvertedProject({
        name: currentProjectName.value || 'Untitled project',
        latex: code.value,
        sourceFilename: currentSourceFilename.value || currentProjectName.value || 'main.tex',
        sourceKind: 'unknown',
        ownerId: userId.value ?? null,
      })
      if (requestId !== compileRequestId) {
        return
      }

      if (promoted.id.startsWith('local-')) {
        compiledPdfData.value = null
        compileState.value = 'error'
        compileErrorMessage.value = 'Could not save to cloud. Please sign in and try again.'
        setAuthError('Cloud save unavailable — check your connection and sign-in status.')
        setTimeout(() => { if (authErrorMessage.value.includes('Cloud save')) clearAuthError() }, 5000)
        return
      }

      projectId = promoted.id
      currentProjectId.value = promoted.id
      currentProjectName.value = promoted.name
      currentSourceFilename.value = promoted.sourceFilename ?? currentSourceFilename.value
      if (routeProjectId.value !== promoted.id) {
        void router.replace({
          path: '/editor',
          query: {
            ...route.query,
            projectId: promoted.id,
          },
        })
      }
    } catch {
      if (requestId !== compileRequestId) {
        return
      }
      compiledPdfData.value = null
      compileState.value = 'error'
      compileErrorMessage.value = 'Cloud save failed. PDF compile requires a remote project.'
      setAuthError('Cloud save failed. Please try again.')
      return
    }
  }

  try {
    const saved = await updateProjectLatex(projectId, sourceSnapshot)
    if (requestId !== compileRequestId) {
      return
    }
    if (!saved) {
      compiledPdfData.value = null
      compileState.value = 'error'
      compileErrorMessage.value = 'Save failed. Fix save issue before compiling.'
      return
    }
  } catch (error) {
    if (requestId !== compileRequestId) {
      return
    }
    if (error instanceof Error && error.message === AUTH_SESSION_EXPIRED_MESSAGE) {
      setAuthError(AUTH_SESSION_EXPIRED_MESSAGE)
    }
    compiledPdfData.value = null
    compileState.value = 'error'
    compileErrorMessage.value = 'Save failed. Fix save issue before compiling.'
    return
  }

  try {
    const result = await compileProjectPdf(projectId)
    if (requestId !== compileRequestId || projectId !== currentProjectId.value) {
      return
    }

    if (result.ok) {
      clearAuthError()
      compiledPdfData.value = result.pdfData
      compiledCode.value = sourceSnapshot
      compileState.value = 'compiled'
      return
    }

    if (result.error === AUTH_SESSION_EXPIRED_MESSAGE) {
      setAuthError(AUTH_SESSION_EXPIRED_MESSAGE)
    }
    compiledPdfData.value = null
    compileState.value = 'error'
    compileErrorMessage.value = result.error
  } catch (error) {
    if (requestId !== compileRequestId) {
      return
    }
    if (error instanceof Error && error.message === AUTH_SESSION_EXPIRED_MESSAGE) {
      setAuthError(AUTH_SESSION_EXPIRED_MESSAGE)
    }
    compiledPdfData.value = null
    compileState.value = 'error'
    compileErrorMessage.value = error instanceof Error ? error.message : 'Compile request failed. Check your connection.'
  }
}

function pickInitialActiveFile(files: ProjectFileMeta[] | null): string | null {
  if (!files || files.length === 0) {
    return null
  }
  const editableTex = files.find((file) => file.kind === 'tex' && file.editable)
  if (editableTex) return editableTex.path
  return files[0]?.path ?? null
}

async function hydrateProjectFiles(projectId: string | null) {
  if (!projectId) {
    projectFilesMetadata.value = null
    activeFilePath.value = null
    return
  }

  try {
    const files = await fetchProjectFiles(projectId)
    clearAuthError()
    projectFilesMetadata.value = files
    activeFilePath.value = pickInitialActiveFile(files)
  } catch (error) {
    if (error instanceof Error && error.message === AUTH_SESSION_EXPIRED_MESSAGE) {
      setAuthError(AUTH_SESSION_EXPIRED_MESSAGE)
    }
    projectFilesMetadata.value = null
    activeFilePath.value = null
  }
}

function handleSelectFile(path: string) {
  activeFilePath.value = path
}

function handleUpdateEditorValue(nextValue: string) {
  if (!isActiveFileEditable.value) {
    return
  }
  code.value = nextValue
}

async function hydrateFromProject(projectId: string | null) {
  const requestId = ++hydrateRequestId
  if (saveTimer) {
    clearTimeout(saveTimer)
    saveTimer = null
  }

  const direct = projectId ? getProjectById(projectId) : undefined
  let fetched
  try {
    fetched = projectId && (!direct || !direct.latex) ? await fetchProjectById(projectId) : undefined
    clearAuthError()
  } catch (error) {
    if (error instanceof Error && error.message === AUTH_SESSION_EXPIRED_MESSAGE) {
      setAuthError(AUTH_SESSION_EXPIRED_MESSAGE)
    }
    fetched = undefined
  }
  if (requestId !== hydrateRequestId) {
    return
  }

  const fallback = !direct && !fetched ? projects.value[0] : undefined
  const project = direct ?? fetched ?? fallback

  isHydrating.value = true

  if (!project) {
    const pendingDraft = pendingEditorTarget.value?.draft ?? consumePendingEditorDraft()
    if (pendingDraft) {
      pendingEditorTarget.value = null
      currentProjectId.value = null
      currentProjectName.value = pendingDraft.name?.trim() || 'Unsaved conversion'
      currentSourceFilename.value = pendingDraft.sourceFilename ?? null
      activeFilePath.value = null
      projectFilesMetadata.value = null
      code.value = pendingDraft.latex
      compiledCode.value = pendingDraft.latex
      compileState.value = 'dirty'
      compileErrorMessage.value = ''
      compiledPdfData.value = null
      saveState.value = 'idle'
      isHydrating.value = false

      if (routeWantsDraft.value) {
        void router.replace({
          path: '/editor',
          query: {
            ...route.query,
            draft: undefined,
          },
        })
      }
      return
    }

    currentProjectId.value = null
    currentProjectName.value = 'Untitled project'
    currentSourceFilename.value = null
    activeFilePath.value = null
    projectFilesMetadata.value = null
    code.value = DEFAULT_LATEX
    compiledCode.value = DEFAULT_LATEX
    compileState.value = 'idle'
    compileErrorMessage.value = ''
    compiledPdfData.value = null
    saveState.value = 'idle'
    isHydrating.value = false
    return
  }

  currentProjectId.value = project.id
  pendingEditorTarget.value = null
  currentProjectName.value = project.name
  currentSourceFilename.value = project.sourceFilename ?? null
  compileErrorMessage.value = ''
  code.value = project.latex || DEFAULT_LATEX
  compiledCode.value = code.value
  compileState.value = 'dirty'
  saveState.value = 'idle'
  compiledPdfData.value = null
  await hydrateProjectFiles(project.id)
  if (requestId !== hydrateRequestId) {
    return
  }
  isHydrating.value = false

  // Only auto-compile for remote projects; local projects show live preview only
  if (!project.id.startsWith('local-')) {
    await compilePreview()
    if (requestId !== hydrateRequestId) {
      return
    }
  }

  if (!routeProjectId.value && project.id) {
    void router.replace({
      path: '/editor',
      query: {
        ...route.query,
        projectId: project.id,
      },
    })
  }
}

async function runSave(projectId: string, latex: string) {
  const requestId = ++saveRequestId
  saveState.value = 'saving'
  let ok = false
  try {
    ok = await updateProjectLatex(projectId, latex)
    clearAuthError()
  } catch (error) {
    if (error instanceof Error && error.message === AUTH_SESSION_EXPIRED_MESSAGE) {
      setAuthError(AUTH_SESSION_EXPIRED_MESSAGE)
    }
    ok = false
  }
  if (requestId !== saveRequestId) {
    return
  }

  if (projectId !== currentProjectId.value) {
    return
  }

  if (ok) {
    saveState.value = 'saved'
    if (saveStateTimer) clearTimeout(saveStateTimer)
    saveStateTimer = setTimeout(() => {
      if (saveState.value === 'saved') {
        saveState.value = 'idle'
      }
    }, 1200)
    return
  }

  saveState.value = 'error'
}

function scheduleSave(nextCode: string) {
  if (!currentProjectId.value || isHydrating.value) return

  if (saveTimer) clearTimeout(saveTimer)
  saveTimer = setTimeout(() => {
    if (currentProjectId.value) {
      void runSave(currentProjectId.value, nextCode)
    }
  }, 500)
}

function flushPendingSave() {
  if (!saveTimer) return
  clearTimeout(saveTimer)
  saveTimer = null

  if (currentProjectId.value && !isHydrating.value) {
    void runSave(currentProjectId.value, code.value)
  }
}

const resolvedProjectId = computed(() => {
  if (routeWantsDraft.value) return null
  if (routeProjectId.value) return routeProjectId.value
  if (pendingEditorTarget.value?.projectId) return pendingEditorTarget.value.projectId
  const latestRemote = projects.value.find((project) => !project.id.startsWith('local-'))
  return latestRemote?.id ?? projects.value[0]?.id ?? null
})

watch([resolvedProjectId, isLoaded, isSignedIn], ([projectId, loaded, signedIn]) => {
  if (!loaded || !signedIn) return
  void hydrateFromProject(projectId)
}, { immediate: true })

watch(code, (nextCode) => {
  if (!isHydrating.value && isActiveFileEditable.value) {
    compileState.value = 'dirty'
  }
  scheduleSave(nextCode)
})

watch(activeTab, (tab) => {
  if (tab === 'preview' && compileState.value === 'dirty' && currentProjectId.value) {
    void compilePreview()
  }
})

watch(
  [isLoaded, isSignedIn],
  ([loaded, signedIn]) => {
    if (!loaded) return
    if (!signedIn) {
      void router.replace('/')
      return
    }
    void ensureRemoteProjectsLoaded().then(() => {
      clearAuthError()
    }).catch((error) => {
      if (error instanceof Error && error.message === AUTH_SESSION_EXPIRED_MESSAGE) {
        setAuthError(AUTH_SESSION_EXPIRED_MESSAGE)
        return
      }
      clearAuthError()
    })
  },
  { immediate: true },
)

async function handleCopy() {
  await navigator.clipboard.writeText(visibleCode.value)
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 1500)
}

function handleDownload() {
  const blob = new Blob([visibleCode.value], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = downloadFilename.value
  anchor.click()
  URL.revokeObjectURL(url)
}

async function handleDownloadFormat(format: 'tex' | 'html' | 'pdf') {
  if (format === 'tex') {
    handleDownload()
    return
  }

  compileErrorMessage.value = ''

  let projectId = currentProjectId.value
  if (!projectId) {
    try {
      const created = await addConvertedProject({
        name: currentProjectName.value || 'Untitled project',
        latex: code.value,
        sourceFilename: currentSourceFilename.value || 'main.tex',
        sourceKind: 'unknown',
        ownerId: userId.value ?? null,
      })

      if (created.id.startsWith('local-')) {
        compileErrorMessage.value = 'Sign in to enable HTML/PDF export.'
        compileState.value = 'error'
        return
      }

      projectId = created.id
      currentProjectId.value = created.id
      currentProjectName.value = created.name
      currentSourceFilename.value = created.sourceFilename ?? currentSourceFilename.value
      clearAuthError()
      if (routeProjectId.value !== created.id) {
        void router.replace({
          path: '/editor',
          query: {
            ...route.query,
            projectId: created.id,
          },
        })
      }
    } catch {
      compileErrorMessage.value = 'Could not save project. Sign in and try again.'
      compileState.value = 'error'
      return
    }
  }

  // Auto-promote local projects before export
  if (projectId.startsWith('local-')) {
    try {
      const promoted = await addConvertedProject({
        name: currentProjectName.value || 'Untitled project',
        latex: code.value,
        sourceFilename: currentSourceFilename.value || 'main.tex',
        sourceKind: 'unknown',
        ownerId: userId.value ?? null,
      })
      if (promoted.id.startsWith('local-')) {
        compileErrorMessage.value = 'Sign in to enable HTML/PDF export.'
        compileState.value = 'error'
        return
      }
      projectId = promoted.id
      currentProjectId.value = promoted.id
    } catch {
      compileErrorMessage.value = 'Could not save project. Sign in and try again.'
      compileState.value = 'error'
      return
    }
  }

  try {
    const saved = await updateProjectLatex(projectId, code.value)
    if (!saved) {
      compileErrorMessage.value = 'Save failed. Fix save issue before export.'
      compileState.value = 'error'
      return
    }

    await exportFile({
      format,
      texFileId: projectId,
      latex: code.value,
      filename: currentProjectName.value || 'monogram-output',
    })
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Export failed'
    compileErrorMessage.value = `${format.toUpperCase()} export failed: ${message}`
    compileState.value = 'error'
  }
}

async function handleShare() {
  const baseUrl = typeof window !== 'undefined' ? window.location.origin : ''
  const shareUrl = new URL('/editor', baseUrl)

  if (currentProjectId.value) {
    shareUrl.searchParams.set('projectId', currentProjectId.value)
  }

  try {
    if (typeof navigator !== 'undefined' && navigator.share) {
      await navigator.share({
        title: currentProjectName.value || 'Monogram project',
        text: 'Open this LaTeX project in Monogram Editor',
        url: shareUrl.toString(),
      })
    } else {
      await navigator.clipboard.writeText(shareUrl.toString())
    }

    shareState.value = 'shared'
    if (shareTimer) clearTimeout(shareTimer)
    shareTimer = setTimeout(() => {
      shareState.value = 'idle'
    }, 1500)
  } catch {
    shareState.value = 'error'
    if (shareTimer) clearTimeout(shareTimer)
    shareTimer = setTimeout(() => {
      shareState.value = 'idle'
    }, 1800)
  }
}

onUnmounted(() => {
  flushPendingSave()

  if (saveStateTimer) {
    clearTimeout(saveStateTimer)
  }
  if (shareTimer) {
    clearTimeout(shareTimer)
  }
})
</script>

<template>
  <main class="h-screen overflow-hidden bg-background">
    <AppNavbar />

    <section class="h-[calc(100vh-3.5rem)] pt-14 px-0 md:pt-0 md:h-screen md:pr-20">
      <div v-if="authErrorMessage" class="mx-3 mt-2 flex items-center justify-between rounded-sm border border-destructive/30 bg-destructive/10 px-4 py-2 md:mx-5">
        <span class="text-[12px] text-destructive">{{ authErrorMessage }}</span>
        <button type="button" class="ml-4 text-[10px] font-semibold tracking-[0.1em] uppercase text-destructive/70 transition-colors hover:text-destructive" @click="clearAuthError">Dismiss</button>
      </div>
      <div class="h-full overflow-hidden bg-card">
        <LatexEditorPanel
          :model-value="visibleCode"
          :active-tab="activeTab"
          :copied="copied"
          :rendered-preview="renderedPreview"
          :pdf-data="compiledPdfData"
          :pdf-error="compileErrorMessage"
          :zoom="zoom"
          :project-name="currentProjectName"
          :source-filename="activeSourceFilename"
          :files="editorFiles"
          :read-only="!isActiveFileEditable"
          :save-status="saveState"
          :save-status-label="saveStatusLabel"
          :compile-status="compileState"
          :compile-status-label="compileStatusLabel"
          :share-label="shareLabel"
          @update:model-value="handleUpdateEditorValue"
          @update:active-tab="activeTab = $event"
          @update:zoom="zoom = $event"
          @select-file="handleSelectFile"
          @copy="handleCopy"
          @download="handleDownload"
          @download-format="handleDownloadFormat"
          @recompile="compilePreview"
          @share="handleShare"
        />
      </div>
    </section>
  </main>
</template>
