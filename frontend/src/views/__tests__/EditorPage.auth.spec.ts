import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

const authState = vi.hoisted(() => ({
  isLoaded: true,
  isSignedIn: false,
  userId: 'user-a' as string | null,
}))

const routerReplace = vi.hoisted(() => vi.fn())
const ensureRemoteProjectsLoaded = vi.hoisted(() => vi.fn(async () => {}))

vi.mock('@clerk/vue', async () => {
  const { ref } = await import('vue')
  return {
    useAuth: () => ({
      isLoaded: ref(authState.isLoaded),
      isSignedIn: ref(authState.isSignedIn),
      userId: ref(authState.userId),
    }),
  }
})

vi.mock('katex', () => ({
  default: {
    renderToString: () => '<span></span>',
  },
}))

vi.mock('@/components/convert/LatexEditorPanel.vue', () => ({
  default: {
    template: '<div data-testid="editor-panel" />',
  },
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({
    replace: routerReplace,
    push: vi.fn(),
  }),
  useRoute: () => ({
    query: {},
  }),
}))

vi.mock('@/composables/useProjects', () => ({
  AUTH_SESSION_EXPIRED_MESSAGE: 'Your session expired. Please sign in again.',
  useProjects: () => ({
    compileProjectPdf: vi.fn(async () => ({ ok: false as const, error: 'Not signed in' })),
    ensureRemoteProjectsLoaded,
    fetchProjectFiles: vi.fn(async () => null),
    fetchProjectById: vi.fn(async () => undefined),
    getProjectById: vi.fn(() => undefined),
    projects: { value: [] },
    updateProjectLatex: vi.fn(async () => true),
  }),
}))

describe('EditorPage auth fallback redirect', () => {
  it('redirects to home when auth is loaded and user is signed out', async () => {
    authState.isLoaded = true
    authState.isSignedIn = false
    const { default: EditorPage } = await import('@/views/EditorPage.vue')

    mount(EditorPage, {
      global: {
        stubs: {
          AppNavbar: true,
          LatexEditorPanel: true,
        },
      },
    })

    expect(routerReplace).toHaveBeenCalledWith('/')
    expect(ensureRemoteProjectsLoaded).not.toHaveBeenCalled()
  })
})
