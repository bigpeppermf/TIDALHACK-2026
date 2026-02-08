import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { clerkPlugin } from '@clerk/vue'

import App from './App.vue'
import router from './router'
import 'katex/dist/katex.min.css'
import './assets/main.css'

const publishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!publishableKey) {
  throw new Error('Missing VITE_CLERK_PUBLISHABLE_KEY in frontend environment.')
}

const app = createApp(App)

app.use(createPinia())
app.use(clerkPlugin, {
  publishableKey,
})
app.use(router)

app.mount('#app')
