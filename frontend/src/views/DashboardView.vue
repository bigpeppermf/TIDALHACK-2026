<script setup lang="ts">
import { RouterLink } from 'vue-router'

const stats = [
  { iconPath: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8ZM14 2v6h6M16 13H8M16 17H8M10 9H8', label: 'Total Conversions', value: '47' },
  { iconPath: 'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20ZM12 6v6l4 2', label: 'Avg. Time', value: '2.4s' },
  { iconPath: 'M22 12h-4l-3 9L9 3l-3 9H2', label: 'This Week', value: '12' },
  { iconPath: 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12', label: 'Images Processed', value: '53' },
]

const recentConversions = [
  { id: 1, name: 'Calculus Notes p.1', date: '2 hours ago', chars: 1240 },
  { id: 2, name: 'Physics Equations', date: '5 hours ago', chars: 890 },
  { id: 3, name: 'Linear Algebra HW', date: '1 day ago', chars: 2100 },
  { id: 4, name: 'Chemistry Formulas', date: '2 days ago', chars: 650 },
  { id: 5, name: 'Statistics Notes', date: '3 days ago', chars: 1800 },
]
</script>

<template>
  <div class="relative min-h-screen bg-background">
    <div class="fixed inset-0 bg-grid-pattern opacity-20" />

    <!-- Top bar -->
    <div class="relative z-10 border-b border-border/50 bg-[hsl(var(--background)/0.8)] backdrop-blur-xl">
      <div class="mx-auto flex max-w-7xl items-center gap-4 px-6 py-4">
        <RouterLink
          to="/"
          class="flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m12 19-7-7 7-7M19 12H5" />
          </svg>
          Home
        </RouterLink>
        <div class="h-4 w-px bg-[hsl(var(--border))]" />
        <span class="text-sm font-medium text-foreground">Dashboard</span>
        <div class="ml-auto">
          <RouterLink
            to="/convert"
            class="inline-flex items-center gap-2 rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground transition-colors hover:bg-[hsl(var(--primary)/0.9)]"
          >
            <svg class="h-3.5 w-3.5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M5 12h14M12 5v14" />
            </svg>
            New Conversion
          </RouterLink>
        </div>
      </div>
    </div>

    <div class="relative z-10 mx-auto max-w-7xl px-6 py-10">
      <!-- Stats grid -->
      <div class="mb-10 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div
          v-for="stat in stats"
          :key="stat.label"
          class="rounded-xl border border-border bg-card p-5 transition-colors hover:border-primary/20"
        >
          <div class="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path :d="stat.iconPath" />
            </svg>
          </div>
          <p class="text-2xl font-bold text-foreground">{{ stat.value }}</p>
          <p class="text-sm text-muted-foreground">{{ stat.label }}</p>
        </div>
      </div>

      <!-- Recent conversions -->
      <div class="rounded-xl border border-border bg-card">
        <div class="flex items-center justify-between border-b border-border px-5 py-4">
          <h2 class="text-lg font-semibold text-foreground">Recent Conversions</h2>
          <span class="text-xs text-muted-foreground">Placeholder data</span>
        </div>
        <div class="divide-y divide-[hsl(var(--border))]">
          <div
            v-for="item in recentConversions"
            :key="item.id"
            class="flex items-center justify-between px-5 py-4 transition-colors hover:bg-secondary/50"
          >
            <div class="flex items-center gap-4">
              <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-secondary text-muted-foreground">
                <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8ZM14 2v6h6M16 13H8M16 17H8M10 9H8" />
                </svg>
              </div>
              <div>
                <p class="text-sm font-medium text-foreground">{{ item.name }}</p>
                <p class="text-xs text-muted-foreground">{{ item.date }}</p>
              </div>
            </div>
            <span class="font-mono text-xs text-muted-foreground">
              {{ item.chars }} chars
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
