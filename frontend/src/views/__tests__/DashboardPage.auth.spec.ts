import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import DashboardPage from '@/views/DashboardPage.vue'

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

vi.mock('vue-router', () => ({
  useRouter: () => ({
    replace: routerReplace,
    push: vi.fn(),
  }),
}))

vi.mock('@/composables/useProjects', async () => {
  const { ref } = await import('vue')
  return {
    AUTH_SESSION_EXPIRED_MESSAGE: 'Your session expired. Please sign in again.',
    useProjects: () => ({
      projects: ref([]),
      ensureRemoteProjectsLoaded,
    }),
  }
})

describe('DashboardPage auth fallback redirect', () => {
  it('redirects to home when auth is loaded and user is signed out', () => {
    authState.isLoaded = true
    authState.isSignedIn = false

    mount(DashboardPage, {
      global: {
        stubs: {
          AppNavbar: true,
          EmptyState: true,
          ProjectRow: true,
        },
      },
    })

    expect(routerReplace).toHaveBeenCalledWith('/')
    expect(ensureRemoteProjectsLoaded).not.toHaveBeenCalled()
  })
})
