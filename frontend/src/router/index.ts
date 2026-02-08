import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import ConvertPage from '../views/ConvertPage.vue'
import DashboardPage from '../views/DashboardPage.vue'
import SettingsPage from '../views/SettingsPage.vue'
import EditorPage from '../views/EditorPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: HomePage },
    { path: '/convert', component: ConvertPage },
    { path: '/dashboard', component: DashboardPage },
    { path: '/settings', component: SettingsPage },
    { path: '/editor', component: EditorPage },
  ],
})

export default router
