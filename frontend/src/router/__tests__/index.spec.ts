import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('../../views/HomePage.vue', () => ({ default: { template: '<div>home</div>' } }))
vi.mock('../../views/ConvertPage.vue', () => ({ default: { template: '<div>convert</div>' } }))
vi.mock('../../views/DashboardPage.vue', () => ({ default: { template: '<div>dashboard</div>' } }))
vi.mock('../../views/SettingsPage.vue', () => ({ default: { template: '<div>settings</div>' } }))
vi.mock('../../views/EditorPage.vue', () => ({ default: { template: '<div>editor</div>' } }))

import router from '@/router'

function setClerkState({ loaded, isSignedIn }: { loaded: boolean; isSignedIn: boolean }) {
  window.Clerk = {
    loaded,
    isSignedIn,
  } as typeof window.Clerk
}

describe('router auth guard', () => {
  beforeEach(async () => {
    setClerkState({ loaded: true, isSignedIn: false })
    await router.replace('/')
  })

  it('redirects signed-out users from protected routes', async () => {
    await router.push('/dashboard')
    expect(router.currentRoute.value.path).toBe('/')
  })

  it('allows signed-in users to access protected routes', async () => {
    setClerkState({ loaded: true, isSignedIn: true })
    await router.push('/editor')
    expect(router.currentRoute.value.path).toBe('/editor')
  })
})
