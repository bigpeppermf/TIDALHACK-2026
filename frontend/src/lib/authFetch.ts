import { useAuth } from '@clerk/vue'
import { toValue } from 'vue'
import type { MaybeRefOrGetter } from 'vue'

export function useAuthFetch() {
  const auth = useAuth()

  async function authFetch(input: RequestInfo | URL, init: RequestInit = {}) {
    let token: string | null = null
    const getToken = toValue(auth.getToken as unknown as MaybeRefOrGetter<(() => Promise<string | null>) | undefined>)
    if (getToken) {
      token = await getToken()
    } else if (typeof window !== 'undefined') {
      const clerk = (window as unknown as { Clerk?: { session?: { getToken?: () => Promise<string | null> } } }).Clerk
      if (clerk?.session?.getToken) {
        token = await clerk.session.getToken()
      }
    }
    const headers = new Headers(init.headers || {})

    if (token) {
      headers.set('Authorization', `Bearer ${token}`)
    }

    return fetch(input, {
      ...init,
      headers,
    })
  }

  return { authFetch }
}
