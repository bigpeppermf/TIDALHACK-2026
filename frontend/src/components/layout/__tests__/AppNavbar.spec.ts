import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import AppNavbar from '@/components/layout/AppNavbar.vue'

const mockAuthState = vi.hoisted(() => ({ signedIn: false }))

vi.mock('@clerk/vue', async () => {
  const { defineComponent, h } = await import('vue')

  const SignedIn = defineComponent({
    setup(_, { slots }) {
      return () => (mockAuthState.signedIn ? slots.default?.() : null)
    },
  })

  const SignedOut = defineComponent({
    setup(_, { slots }) {
      return () => (!mockAuthState.signedIn ? slots.default?.() : null)
    },
  })

  const SignInButton = defineComponent({
    setup(_, { slots }) {
      return () => h('div', { 'data-testid': 'sign-in-button' }, slots.default?.())
    },
  })

  const UserButton = defineComponent({
    template: '<div data-testid="user-button" />',
  })

  return { SignedIn, SignedOut, SignInButton, UserButton }
})

function mountNavbar() {
  return mount(AppNavbar, {
    global: {
      stubs: {
        RouterLink: { template: '<a><slot /></a>' },
      },
    },
  })
}

describe('AppNavbar auth controls', () => {
  it('shows login controls when signed out', () => {
    mockAuthState.signedIn = false
    const wrapper = mountNavbar()

    expect(wrapper.findAll('[data-testid="sign-in-button"]').length).toBeGreaterThan(0)
    expect(wrapper.find('[data-testid="user-button"]').exists()).toBe(false)
  })

  it('shows user button when signed in', () => {
    mockAuthState.signedIn = true
    const wrapper = mountNavbar()

    expect(wrapper.find('[data-testid="user-button"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="sign-in-button"]').exists()).toBe(false)
  })
})
