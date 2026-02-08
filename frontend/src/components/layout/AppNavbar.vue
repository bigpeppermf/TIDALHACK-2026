<script setup lang="ts">
import { SignedIn, SignedOut, SignInButton, UserButton, useUser } from '@clerk/vue'
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { Button } from '@/components/ui/button'

const { user } = useUser()
const mobileOpen = ref(false)

const navLinks = [
  { label: 'Home', to: '/' },
  { label: 'Features', href: '/#features' },
  { label: 'Convert', to: '/convert' },
  { label: 'Editor', to: '/editor' },
  { label: 'Dashboard', to: '/dashboard' },
]
</script>

<template>
  <header class="pointer-events-none fixed inset-0 z-50">
    <!-- Desktop: Fixed right sidebar -->
    <aside
      class="pointer-events-auto absolute right-4 top-16 hidden h-[calc(100vh-5rem)] w-16 flex-col items-center justify-between rounded-xl py-4 md:flex"
      style="
        background: hsl(var(--background) / 0.6);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid hsl(var(--border) / 0.4);
      "
      aria-label="Right navigation"
    >
      <div class="flex flex-col items-center">
        <SignedOut>
          <SignInButton mode="modal">
            <button
              class="flex h-9 w-9 items-center justify-center rounded-md text-[9px] font-semibold tracking-[0.1em] uppercase transition-all duration-300"
              style="
                background: transparent;
                color: hsl(var(--muted-foreground));
                border: 1px solid hsl(var(--border) / 0.4);
              "
            >
              Log in
            </button>
          </SignInButton>
        </SignedOut>
        <SignedIn>
          <UserButton after-sign-out-url="/" />
        </SignedIn>
      </div>

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

      <span
        class="rotate-180 text-[10px] tracking-[0.35em] text-muted-foreground/40"
        style="writing-mode: vertical-rl"
      >
        monogram
      </span>
    </aside>

    <!-- Mobile: Top bar -->
    <div
      class="pointer-events-auto px-4 py-3 md:hidden"
      style="
        background: hsl(var(--background) / 0.82);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-bottom: 1px solid hsl(var(--border) / 0.3);
      "
    >
      <div class="flex items-center justify-between gap-3">
        <RouterLink
          to="/"
          class="text-sm font-semibold tracking-wide text-foreground"
          style="font-family: var(--font-heading)"
        >
          monogram
        </RouterLink>
        <div class="flex items-center gap-2">
          <SignedOut>
            <SignInButton mode="modal">
              <button
                class="px-3 py-1 text-[11px] font-semibold tracking-[0.1em] uppercase rounded-sm border transition-colors"
                style="
                  background: transparent;
                  color: hsl(var(--muted-foreground));
                  border-color: hsl(var(--border));
                "
              >
                Login
              </button>
            </SignInButton>
          </SignedOut>
          <SignedIn>
            <UserButton after-sign-out-url="/" />
          </SignedIn>
          <button
            type="button"
            class="rounded-sm px-2 py-1 text-xs text-muted-foreground transition-colors"
            style="border: 1px solid hsl(var(--border))"
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
            class="rounded-sm px-3 py-1.5 text-[11px] tracking-[0.1em] uppercase text-muted-foreground transition-colors hover:text-foreground"
            style="border: 1px solid hsl(var(--border) / 0.4)"
            @click="mobileOpen = false"
          >
            {{ link.label }}
          </a>
          <RouterLink
            v-else
            :to="link.to!"
            class="rounded-sm px-3 py-1.5 text-[11px] tracking-[0.1em] uppercase text-muted-foreground transition-colors hover:text-foreground"
            style="border: 1px solid hsl(var(--border) / 0.4)"
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
  color: hsl(var(--muted-foreground) / 0.5);
  transition: color 0.3s ease;
}

.vertical-nav-link:hover {
  color: hsl(var(--foreground));
}
</style>
