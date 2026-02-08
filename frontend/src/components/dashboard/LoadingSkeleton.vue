<template>
  <div class="space-y-8">
    <!-- Comparison Grid Skeleton -->
    <div class="grid grid-cols-2 gap-6">
      <div
        v-for="i in 2"
        :key="'panel-' + i"
        class="flex flex-col overflow-hidden rounded-xl border border-[#2d2d38] bg-[#1a1a1f]"
      >
        <!-- Header skeleton -->
        <div class="flex items-center justify-between border-b border-[#2d2d38] bg-[#131316] px-4 py-3">
          <div class="h-4 w-36 animate-pulse rounded bg-[#2d2d38]" />
          <div class="flex gap-2">
            <div class="h-7 w-7 animate-pulse rounded bg-[#2d2d38]" />
            <div class="h-7 w-7 animate-pulse rounded bg-[#2d2d38]" />
          </div>
        </div>

        <!-- Content skeleton -->
        <div class="flex min-h-[500px] items-center justify-center bg-[#0a0a0b] p-8">
          <div class="w-full max-w-lg space-y-4 rounded bg-[#131316] p-10">
            <div class="mb-6 h-6 w-48 animate-pulse rounded bg-[#2d2d38]" />
            <div class="h-4 w-full animate-pulse rounded bg-[#1a1a1f]" />
            <div class="h-4 w-5/6 animate-pulse rounded bg-[#1a1a1f]" />
            <div class="h-4 w-4/5 animate-pulse rounded bg-[#1a1a1f]" />
            <div class="h-4 w-full animate-pulse rounded bg-[#1a1a1f]" />
            <div class="h-4 w-3/4 animate-pulse rounded bg-[#1a1a1f]" />
          </div>
        </div>

        <!-- Footer skeleton -->
        <div class="flex items-center justify-between border-t border-[#2d2d38] bg-[#131316] px-4 py-3">
          <div class="flex gap-4">
            <div class="h-4 w-24 animate-pulse rounded bg-[#2d2d38]" />
            <div class="h-4 w-20 animate-pulse rounded bg-[#2d2d38]" />
          </div>
          <div class="h-8 w-28 animate-pulse rounded bg-[#2d2d38]" />
        </div>
      </div>
    </div>

    <!-- Project List Skeleton -->
    <div class="space-y-3">
      <div class="mb-4 h-5 w-32 animate-pulse rounded bg-[#2d2d38]" />

      <div
        v-for="i in 3"
        :key="'row-' + i"
        class="flex items-center gap-4 rounded-xl bg-[#131316] p-4"
      >
        <div class="h-20 w-20 flex-shrink-0 animate-pulse rounded-lg bg-[#0a0a0b]" />
        <div class="flex flex-1 flex-col gap-2">
          <div class="h-4 w-48 animate-pulse rounded bg-[#2d2d38]" />
          <div class="h-3 w-32 animate-pulse rounded bg-[#1a1a1f]" />
          <div class="h-5 w-20 animate-pulse rounded-full bg-[#1a1a1f]" />
        </div>
      </div>
    </div>
  </div>
</template>
