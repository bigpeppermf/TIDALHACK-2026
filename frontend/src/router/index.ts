import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import ConvertPage from '../views/ConvertPage.vue'
import DashboardPage from '../views/DashboardPage.vue'
import SettingsPage from '../views/SettingsPage.vue'
import EditorPage from '../views/EditorPage.vue'

const AUTH_GUARD_WAIT_MS = 1500

async function waitForClerkLoad(timeoutMs = AUTH_GUARD_WAIT_MS) {
  if (typeof window === 'undefined') {
    return null
  }

  const startedAt = Date.now()
  while (Date.now() - startedAt < timeoutMs) {
    if (window.Clerk?.loaded) {
      return window.Clerk
    }
    await new Promise((resolve) => setTimeout(resolve, 20))
  }

  return window.Clerk ?? null
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: HomePage },
    { path: '/convert', component: ConvertPage },
    { path: '/dashboard', component: DashboardPage, meta: { requiresAuth: true } },
    { path: '/settings', component: SettingsPage, meta: { requiresAuth: true } },
    { path: '/editor', component: EditorPage, meta: { requiresAuth: true } },
  ],
})

router.beforeEach(async (to) => {
  if (!to.meta.requiresAuth) {
    return true
  }

  const clerk = await waitForClerkLoad()
  if (clerk?.loaded && !clerk.isSignedIn) {
    return { path: '/' }
  }

  return true
})

export default router
