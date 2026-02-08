<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { useUser } from '@clerk/vue'
import FadeIn from '@/components/landing/FadeIn.vue'

const { user } = useUser()
</script>

<template>
  <footer class="relative" style="border-top: 1px solid hsl(var(--border) / 0.3)">
    <div class="py-16 px-6 md:px-12">
      <div class="mx-auto max-w-7xl">
        <!-- Top row -->
        <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-8 mb-12">
          <!-- Logo -->
          <div class="flex items-center gap-3">
            <div
              class="flex h-8 w-8 items-center justify-center overflow-hidden rounded-sm"
              style="background: hsl(var(--primary)); color: hsl(var(--primary-foreground))"
            >
              <img v-if="user?.imageUrl" :src="user.imageUrl" alt="Profile" class="h-full w-full object-cover" />
              <span v-else class="text-xs font-bold" style="font-family: var(--font-heading)">m</span>
            </div>
            <span
              class="text-sm font-semibold text-foreground tracking-wide"
              style="font-family: var(--font-heading)"
            >
              monogram
            </span>
          </div>

          <!-- Links -->
          <div class="flex gap-8">
            <a
              href="#features"
              class="text-[11px] tracking-[0.2em] uppercase text-muted-foreground/50 transition-colors duration-300 hover:text-foreground"
            >
              Features
            </a>
            <RouterLink
              to="/dashboard"
              class="text-[11px] tracking-[0.2em] uppercase text-muted-foreground/50 transition-colors duration-300 hover:text-foreground"
            >
              Dashboard
            </RouterLink>
            <RouterLink
              to="/editor"
              class="text-[11px] tracking-[0.2em] uppercase text-muted-foreground/50 transition-colors duration-300 hover:text-foreground"
            >
              Editor
            </RouterLink>
            <RouterLink
              to="/convert"
              class="text-[11px] tracking-[0.2em] uppercase text-muted-foreground/50 transition-colors duration-300 hover:text-foreground"
            >
              Convert
            </RouterLink>
          </div>
        </div>

        <!-- Bottom divider + copyright -->
        <div style="border-top: 1px solid hsl(var(--border) / 0.2)" class="pt-8 flex items-center justify-between">
          <p class="text-[11px] tracking-[0.15em] text-muted-foreground/30">
            Built with Vue. All rights reserved.
          </p>
          <div class="flex items-center gap-3">
            <div class="w-2 h-2 rounded-full" style="background: hsl(var(--primary) / 0.4)" />
            <span class="text-[11px] tracking-[0.15em] uppercase text-muted-foreground/30">
              Design
            </span>
            <div class="w-2 h-2 rounded-full" style="background: hsl(var(--primary) / 0.25)" />
            <span class="text-[11px] tracking-[0.15em] uppercase text-muted-foreground/30">
              Motion
            </span>
            <div class="w-2 h-2 rounded-full" style="background: hsl(var(--muted-foreground) / 0.3)" />
            <span class="text-[11px] tracking-[0.15em] uppercase text-muted-foreground/30">
              Craft
            </span>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>
