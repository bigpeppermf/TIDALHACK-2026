<script setup lang="ts">
import { ref } from 'vue'
import AppNavbar from '@/components/layout/AppNavbar.vue'

const sections = [
  { iconPath: 'M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2M12 3a4 4 0 1 0 0 8 4 4 0 0 0 0-8Z', label: 'Profile', id: 'profile' },
  { iconPath: 'M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0 3 3L22 7l-3-3m-3.5 3.5L19 4', label: 'API Keys', id: 'api' },
  { iconPath: 'M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9M10.3 21a1.94 1.94 0 0 0 3.4 0', label: 'Notifications', id: 'notifications' },
  { iconPath: 'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20ZM12 8v4l3 3', label: 'Appearance', id: 'appearance' },
  { iconPath: 'M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10Z', label: 'Language', id: 'language' },
]

const activeSection = ref('profile')

const notifications = [
  { label: 'Conversion complete', desc: 'Notify when a conversion finishes', enabled: ref(true) },
  { label: 'Error alerts', desc: 'Get notified when something fails', enabled: ref(true) },
  { label: 'Weekly summary', desc: 'Receive a weekly usage report', enabled: ref(false) },
]
</script>

<template>
  <div class="relative min-h-screen bg-background">
    <AppNavbar />
    <div class="fixed inset-0 bg-grid-pattern opacity-20" />

    <div class="relative z-10 mx-auto flex max-w-5xl gap-8 px-6 pt-10 pb-10">
      <!-- Sidebar nav -->
      <aside class="hidden w-48 shrink-0 md:block">
        <nav class="flex flex-col gap-1">
          <button
            v-for="section in sections"
            :key="section.id"
            type="button"
            :class="[
              'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
              activeSection === section.id
                ? 'bg-secondary text-foreground'
                : 'text-muted-foreground hover:bg-secondary/50 hover:text-foreground',
            ]"
            @click="activeSection = section.id"
          >
            <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path :d="section.iconPath" />
            </svg>
            {{ section.label }}
          </button>
        </nav>
      </aside>

      <!-- Content -->
      <div class="flex-1 rounded-xl border border-border bg-card p-6 md:p-8">
        <!-- Profile -->
        <div v-if="activeSection === 'profile'" class="flex flex-col gap-6">
          <div>
            <h2 class="text-xl font-semibold text-foreground">Profile</h2>
            <p class="text-sm text-muted-foreground">Manage your account information.</p>
          </div>
          <hr class="border-border" />
          <div class="grid max-w-md gap-4">
            <div class="flex flex-col gap-2">
              <label for="name" class="text-sm font-medium text-foreground">Display Name</label>
              <input
                id="name"
                type="text"
                placeholder="Your name"
                class="rounded-md border border-border bg-secondary px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
              />
            </div>
            <div class="flex flex-col gap-2">
              <label for="email" class="text-sm font-medium text-foreground">Email</label>
              <input
                id="email"
                type="email"
                placeholder="you@example.com"
                class="rounded-md border border-border bg-secondary px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
              />
            </div>
          </div>
          <button
            type="button"
            class="w-fit rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-[hsl(var(--primary)/0.9)]"
          >
            Save Changes
          </button>
        </div>

        <!-- API Keys -->
        <div v-if="activeSection === 'api'" class="flex flex-col gap-6">
          <div>
            <h2 class="text-xl font-semibold text-foreground">API Keys</h2>
            <p class="text-sm text-muted-foreground">Manage API keys for backend integration.</p>
          </div>
          <hr class="border-border" />
          <div class="rounded-lg border border-border bg-secondary/50 p-4">
            <p class="text-sm text-muted-foreground">
              No API keys configured yet. This will connect to your backend.
            </p>
          </div>
        </div>

        <!-- Notifications -->
        <div v-if="activeSection === 'notifications'" class="flex flex-col gap-6">
          <div>
            <h2 class="text-xl font-semibold text-foreground">Notifications</h2>
            <p class="text-sm text-muted-foreground">Configure how you receive updates.</p>
          </div>
          <hr class="border-border" />
          <div class="flex flex-col gap-4">
            <div
              v-for="item in notifications"
              :key="item.label"
              class="flex items-center justify-between rounded-lg border border-border p-4"
            >
              <div>
                <p class="text-sm font-medium text-foreground">{{ item.label }}</p>
                <p class="text-xs text-muted-foreground">{{ item.desc }}</p>
              </div>
              <button
                type="button"
                :class="[
                  'relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2 focus:ring-offset-[hsl(var(--background))]',
                  item.enabled.value ? 'bg-primary' : 'bg-[hsl(var(--input))]',
                ]"
                role="switch"
                :aria-checked="item.enabled.value"
                @click="item.enabled.value = !item.enabled.value"
              >
                <span
                  :class="[
                    'pointer-events-none inline-block h-5 w-5 rounded-full bg-[hsl(var(--background))] shadow ring-0 transition duration-200',
                    item.enabled.value ? 'translate-x-5' : 'translate-x-0',
                  ]"
                />
              </button>
            </div>
          </div>
        </div>

        <!-- Appearance -->
        <div v-if="activeSection === 'appearance'" class="flex flex-col gap-6">
          <div>
            <h2 class="text-xl font-semibold text-foreground">Appearance</h2>
            <p class="text-sm text-muted-foreground">Customize how monogram looks.</p>
          </div>
          <hr class="border-border" />
          <div class="rounded-lg border border-border bg-secondary/50 p-4">
            <p class="text-sm text-muted-foreground">
              Dark mode is currently the default. Theme switching coming soon.
            </p>
          </div>
        </div>

        <!-- Language -->
        <div v-if="activeSection === 'language'" class="flex flex-col gap-6">
          <div>
            <h2 class="text-xl font-semibold text-foreground">Language</h2>
            <p class="text-sm text-muted-foreground">Select your preferred language.</p>
          </div>
          <hr class="border-border" />
          <div class="rounded-lg border border-border bg-secondary/50 p-4">
            <p class="text-sm text-muted-foreground">
              English is the only supported language at this time.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
