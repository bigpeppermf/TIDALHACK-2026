<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const mobileOpen = ref(false)

const navLinks = [
  { label: 'Features', href: '#features' },
  { label: 'How It Works', href: '#how-it-works' },
  { label: 'Dashboard', to: '/dashboard' },
  { label: 'Settings', to: '/settings' },
]
</script>

<template>
  <header
    class="fixed top-0 left-0 right-0 z-50 border-b border-border/50 bg-[hsl(var(--background)/0.8)] backdrop-blur-xl"
  >
    <nav class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
      <!-- Logo -->
      <RouterLink to="/" class="flex items-center gap-2">
        <div
          class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary"
        >
          <span class="font-mono text-sm font-bold text-primary-foreground">S</span>
        </div>
        <span class="text-lg font-semibold tracking-tight text-foreground">
          ScribeTeX
        </span>
      </RouterLink>

      <!-- Desktop links -->
      <div class="hidden items-center gap-8 md:flex">
        <template v-for="link in navLinks" :key="link.label">
          <a
            v-if="link.href"
            :href="link.href"
            class="text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            {{ link.label }}
          </a>
          <RouterLink
            v-else
            :to="link.to!"
            class="text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            {{ link.label }}
          </RouterLink>
        </template>
      </div>

      <!-- CTA -->
      <div class="hidden items-center gap-3 md:flex">
        <RouterLink
          to="/convert"
          class="rounded-md px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          Sign In
        </RouterLink>
        <RouterLink
          to="/convert"
          class="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-[hsl(var(--primary)/0.9)]"
        >
          Get Started
        </RouterLink>
      </div>

      <!-- Mobile toggle -->
      <button
        type="button"
        class="text-foreground md:hidden"
        :aria-label="mobileOpen ? 'Close menu' : 'Open menu'"
        @click="mobileOpen = !mobileOpen"
      >
        <svg
          v-if="!mobileOpen"
          class="h-5 w-5"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M4 6h16M4 12h16M4 18h16" />
        </svg>
        <svg
          v-else
          class="h-5 w-5"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M18 6 6 18M6 6l12 12" />
        </svg>
      </button>
    </nav>

    <!-- Mobile menu -->
    <div
      v-if="mobileOpen"
      class="border-t border-border/50 bg-[hsl(var(--background)/0.95)] backdrop-blur-xl md:hidden"
    >
      <div class="flex flex-col gap-1 px-6 py-4">
        <template v-for="link in navLinks" :key="link.label">
          <a
            v-if="link.href"
            :href="link.href"
            class="rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
            @click="mobileOpen = false"
          >
            {{ link.label }}
          </a>
          <RouterLink
            v-else
            :to="link.to!"
            class="rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
            @click="mobileOpen = false"
          >
            {{ link.label }}
          </RouterLink>
        </template>
        <div class="mt-3 flex flex-col gap-2">
          <RouterLink
            to="/convert"
            class="px-3 py-2 text-sm text-muted-foreground"
            @click="mobileOpen = false"
          >
            Sign In
          </RouterLink>
          <RouterLink
            to="/convert"
            class="rounded-md bg-primary px-3 py-2 text-center text-sm font-medium text-primary-foreground"
            @click="mobileOpen = false"
          >
            Get Started
          </RouterLink>
        </div>
      </div>
    </div>
  </header>
</template>
