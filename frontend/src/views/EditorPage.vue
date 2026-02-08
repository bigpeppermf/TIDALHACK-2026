<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import katex from 'katex'
import { useRoute, useRouter } from 'vue-router'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import LatexEditorPanel from '@/components/convert/LatexEditorPanel.vue'
import { useProjects } from '@/composables/useProjects'

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
  name: string
  kind: 'tex' | 'dir' | 'bib' | 'md'
  active?: boolean
}

const route = useRoute()
const router = useRouter()
const ownerId = typeof window === 'undefined' ? null : window.localStorage.getItem('clerk-user-id')
const {
  ensureRemoteProjectsLoaded,
  fetchProjectById,
  getProjectById,
  projects,
  updateProjectLatex,
} = useProjects(ownerId)

const code = ref(DEFAULT_LATEX)
const compiledCode = ref(DEFAULT_LATEX)
const activeTab = ref<'preview' | 'source'>('source')
const zoom = ref(100)
const copied = ref(false)
const currentProjectId = ref<string | null>(null)
const currentProjectName = ref('tidalhack-paper')
const currentSourceFilename = ref<string | null>(null)
const saveState = ref<SaveState>('idle')
const compileState = ref<CompileState>('compiled')
const shareState = ref<ShareState>('idle')

const isHydrating = ref(false)
let saveTimer: ReturnType<typeof setTimeout> | null = null
let saveStateTimer: ReturnType<typeof setTimeout> | null = null
let shareTimer: ReturnType<typeof setTimeout> | null = null

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

    return katex.renderToString(cleanedTex, {
      displayMode,
      throwOnError: false,
      strict: false,
      output: 'htmlAndMathml',
      errorColor: '#000',
      trust: false,
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
  src = src.replace(/\\begin\{(align\*?|equation\*?|gather\*?)\}([\s\S]*?)\\end\{\1\}/g, (_m, _env, tex) => {
    return insertSafeBlock(`<div class="my-6 overflow-x-auto flex justify-center">${safeMathRender(tex, true)}</div>`)
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

  src = src.replace(/\\textbf\{([^}]*)\}/g, (_m, text) => insertSafeBlock(`<strong>${escapeHtml(text)}</strong>`))
  src = src.replace(/\\textit\{([^}]*)\}/g, (_m, text) => insertSafeBlock(`<em>${escapeHtml(text)}</em>`))
  src = src.replace(/\\emph\{([^}]*)\}/g, (_m, text) => insertSafeBlock(`<em>${escapeHtml(text)}</em>`))
  src = src.replace(/\\texttt\{([^}]*)\}/g, (_m, text) => insertSafeBlock(`<code class="font-mono text-sm">${escapeHtml(text)}</code>`))

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

  src = src.replace(/@@SAFE_BLOCK_(\d+)@@/g, (_m, idx) => safeBlocks[Number(idx)] ?? '')

  return src
}

const renderedPreview = computed(() => renderLatexPreview(compiledCode.value))

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

const editorFiles = computed<EditorFileItem[]>(() => {
  const filename = (currentSourceFilename.value || '').trim()
  if (!filename) return []
  return [{ name: filename, kind: 'tex', active: true }]
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
  compileState.value = 'compiling'

  try {
    await Promise.resolve()
    compiledCode.value = code.value
    compileState.value = 'compiled'
  } catch (error) {
    compileState.value = 'error'
  }
}

async function hydrateFromProject(projectId: string | null) {
  const direct = projectId ? getProjectById(projectId) : undefined
  const fetched = projectId && (!direct || !direct.latex) ? await fetchProjectById(projectId) : undefined
  const fallback = !direct && !fetched ? projects.value[0] : undefined
  const project = direct ?? fetched ?? fallback

  isHydrating.value = true

  if (!project) {
    currentProjectId.value = null
    currentProjectName.value = 'tidalhack-paper'
    currentSourceFilename.value = null
    code.value = DEFAULT_LATEX
    compiledCode.value = DEFAULT_LATEX
    compileState.value = 'compiled'
    saveState.value = 'idle'
    isHydrating.value = false
    return
  }

  currentProjectId.value = project.id
  currentProjectName.value = project.name
  currentSourceFilename.value = project.sourceFilename ?? null
  code.value = project.latex || DEFAULT_LATEX
  compiledCode.value = code.value
  compileState.value = 'compiled'
  saveState.value = 'idle'
  isHydrating.value = false

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
  saveState.value = 'saving'
  const ok = await updateProjectLatex(projectId, latex)

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

watch(
  () => [routeProjectId.value, projects.value.length] as const,
  ([projectId]) => {
    void hydrateFromProject(projectId)
  },
  { immediate: true },
)

watch(code, (nextCode) => {
  if (!isHydrating.value) {
    compileState.value = 'dirty'
  }
  scheduleSave(nextCode)
})

onMounted(() => {
  void ensureRemoteProjectsLoaded()
  void compilePreview()
})

async function handleCopy() {
  await navigator.clipboard.writeText(code.value)
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 1500)
}

function handleDownload() {
  const blob = new Blob([code.value], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = downloadFilename.value
  anchor.click()
  URL.revokeObjectURL(url)
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
  <main class="min-h-screen bg-background">
    <AppNavbar />

    <section class="h-screen px-3 pb-3 pt-20 md:px-5">
      <div class="mx-auto h-full max-w-[1500px] overflow-hidden rounded-2xl border border-border bg-card">
        <LatexEditorPanel
          :model-value="code"
          :active-tab="activeTab"
          :copied="copied"
          :rendered-preview="renderedPreview"
          :zoom="zoom"
          :project-name="currentProjectName"
          :source-filename="currentSourceFilename || undefined"
          :files="editorFiles"
          :save-status="saveState"
          :save-status-label="saveStatusLabel"
          :compile-status="compileState"
          :compile-status-label="compileStatusLabel"
          :share-label="shareLabel"
          @update:model-value="code = $event"
          @update:active-tab="activeTab = $event"
          @update:zoom="zoom = $event"
          @copy="handleCopy"
          @download="handleDownload"
          @recompile="compilePreview"
          @share="handleShare"
        />
      </div>
    </section>
  </main>
</template>
