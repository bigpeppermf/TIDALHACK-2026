<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { Button } from '@/components/ui/button'

const mobileOpen = ref(false)

const navLinks = [
  { label: 'Home', to: '/' },
  { label: 'Features', href: '#features' },
  { label: 'How It Works', href: '#how-it-works' },
  { label: 'Dashboard', to: '/dashboard' },
  { label: 'Settings', to: '/settings' },
]
</script>

<template>
  <header class="pointer-events-none fixed inset-0 z-50">
    <div class="pointer-events-auto absolute top-4 right-4">
      <Button as-child size="sm">
        <RouterLink to="/convert">Login</RouterLink>
      </Button>
    </div>

    <aside
      class="pointer-events-auto absolute right-4 top-16 hidden h-[calc(100vh-5rem)] w-16 flex-col items-center justify-between rounded-xl border border-border/60 bg-[hsl(var(--background)/0.75)] py-4 backdrop-blur-xl md:flex"
      aria-label="Right navigation"
    >
      <RouterLink
        to="/"
        class="flex h-9 w-9 items-center justify-center rounded-md border border-border/60 text-sm font-semibold text-foreground"
        aria-label="monogram home"
      >
        m
      </RouterLink>

      <nav class="flex flex-col items-center gap-3">
        <template v-for="link in navLinks" :key="link.label">
          <a v-if="link.href" :href="link.href" class="vertical-nav-link">
            {{ link.label }}
          </a>
          <RouterLink v-else :to="link.to!" class="vertical-nav-link">
            {{ link.label }}
          </RouterLink>
        </template>
      </nav>

      <span class="rotate-180 text-[10px] tracking-[0.35em] text-muted-foreground [writing-mode:vertical-rl]">
        monogram
      </span>
    </aside>

    <div class="pointer-events-auto border-b border-border/40 bg-[hsl(var(--background)/0.82)] px-4 py-3 backdrop-blur-xl md:hidden">
      <div class="flex items-center justify-between gap-3">
        <RouterLink to="/" class="text-sm font-semibold tracking-wide text-foreground">
          monogram
        </RouterLink>
        <div class="flex items-center gap-2">
          <Button as-child size="sm">
            <RouterLink to="/convert">Login</RouterLink>
          </Button>
          <button
            type="button"
            class="rounded-md border border-border px-2 py-1 text-xs text-foreground"
            :aria-label="mobileOpen ? 'Close menu' : 'Open menu'"
            @click="mobileOpen = !mobileOpen"
          >
            Menu
          </button>
        </div>
      </div>

      <div v-if="mobileOpen" class="mt-3 flex flex-wrap gap-2 pb-1">
        <template v-for="link in navLinks" :key="`mobile-${link.label}`">
          <a
            v-if="link.href"
            :href="link.href"
            class="rounded-md border border-border px-2 py-1 text-xs text-muted-foreground"
            @click="mobileOpen = false"
          >
            {{ link.label }}
          </a>
          <RouterLink
            v-else
            :to="link.to!"
            class="rounded-md border border-border px-2 py-1 text-xs text-muted-foreground"
            @click="mobileOpen = false"
          >
            {{ link.label }}
          </RouterLink>
        </template>
      </div>
    </div>
  </header>
</template>

<style scoped>
.vertical-nav-link {
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  letter-spacing: 0.18em;
  font-size: 0.62rem;
  text-transform: uppercase;
  color: hsl(var(--muted-foreground));
  transition: color 0.2s ease;
}

.vertical-nav-link:hover {
  color: hsl(var(--foreground));
}
</style>
