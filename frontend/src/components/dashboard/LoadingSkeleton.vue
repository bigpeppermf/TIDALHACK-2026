<template>
  <div class="space-y-8">
    <!-- Project List Skeleton -->
    <div class="space-y-3">
      <div class="mb-4 h-5 w-32 animate-pulse rounded bg-border" />

      <div
        v-for="i in 3"
        :key="'row-' + i"
        class="flex items-center gap-4 rounded-xl bg-card p-4"
      >
        <div class="h-20 w-20 flex-shrink-0 animate-pulse rounded-lg bg-background" />
        <div class="flex flex-1 flex-col gap-2">
          <div class="h-4 w-48 animate-pulse rounded bg-border" />
          <div class="h-3 w-32 animate-pulse rounded bg-secondary" />
          <div class="h-5 w-20 animate-pulse rounded-full bg-secondary" />
        </div>
      </div>
    </div>
  </div>
</template>
