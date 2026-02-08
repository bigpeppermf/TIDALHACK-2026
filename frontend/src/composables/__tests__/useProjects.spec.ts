import { describe, expect, it, vi, beforeEach } from 'vitest'

const mockAuthState = vi.hoisted(() => ({
  userId: 'user-a',
  token: 'test-token',
}))

vi.mock('@clerk/vue', async () => {
  const { ref } = await import('vue')
  return {
    useAuth: () => ({
      userId: ref(mockAuthState.userId),
      getToken: ref(async () => mockAuthState.token),
    }),
  }
})

function seedProjects(projects: unknown[]) {
  window.localStorage.setItem('monogram-projects', JSON.stringify(projects))
}

describe('useProjects', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    vi.resetModules()
    window.localStorage.clear()
    mockAuthState.userId = 'user-a'
    mockAuthState.token = 'test-token'
  })

  it('returns projects scoped to the active user', async () => {
    seedProjects([
      {
        id: 'p1',
        name: 'Project A',
        updatedAt: 'now',
        updatedAtIso: new Date().toISOString(),
        status: 'converted',
        latex: 'A',
        ownerId: 'user-a',
      },
      {
        id: 'p2',
        name: 'Project B',
        updatedAt: 'now',
        updatedAtIso: new Date().toISOString(),
        status: 'converted',
        latex: 'B',
        ownerId: 'user-b',
      },
    ])

    const { useProjects } = await import('../useProjects')
    const { projects } = useProjects()

    expect(projects.value).toHaveLength(1)
    expect(projects.value[0]?.id).toBe('p1')
    expect(projects.value[0]?.ownerId).toBe('user-a')
  })

  it('sends clerk bearer token and scopes fetched projects', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(
        JSON.stringify([
          { id: 'r1', filename: 'alpha.tex', created_at: '2026-02-08T00:00:00.000Z' },
          { id: 'r2', filename: 'beta.tex', created_at: '2026-02-08T00:01:00.000Z' },
        ]),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      ),
    )

    const { useProjects } = await import('../useProjects')
    const { projects, fetchRecentProjects } = useProjects()

    await fetchRecentProjects()

    expect(fetchMock).toHaveBeenCalledTimes(1)
    const requestInit = fetchMock.mock.calls[0]?.[1] as RequestInit | undefined
    const authHeader = new Headers(requestInit?.headers).get('Authorization')
    expect(authHeader).toBe('Bearer test-token')

    expect(projects.value).toHaveLength(2)
    expect(projects.value.every((project) => project.ownerId === 'user-a')).toBe(true)
  })
})
