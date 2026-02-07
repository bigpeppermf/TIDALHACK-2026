<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <footer class="border-t border-border/50 py-12">
    <div
      class="mx-auto flex max-w-7xl flex-col items-center justify-between gap-6 px-6 md:flex-row"
    >
      <!-- Logo -->
      <div class="flex items-center gap-2">
        <div class="flex h-7 w-7 items-center justify-center rounded-md bg-primary">
          <span class="font-mono text-xs font-bold text-primary-foreground">S</span>
        </div>
        <span class="text-sm font-semibold text-foreground">ScribeTeX</span>
      </div>

      <!-- Links -->
      <div class="flex gap-6 text-sm text-muted-foreground">
        <a href="#features" class="transition-colors hover:text-foreground">Features</a>
        <RouterLink to="/dashboard" class="transition-colors hover:text-foreground">
          Dashboard
        </RouterLink>
        <RouterLink to="/settings" class="transition-colors hover:text-foreground">
          Settings
        </RouterLink>
        <RouterLink to="/convert" class="transition-colors hover:text-foreground">
          Convert
        </RouterLink>
      </div>

      <!-- Copyright -->
      <p class="text-xs text-muted-foreground">
        Built with AI. All rights reserved.
      </p>
    </div>
  </footer>
</template>
