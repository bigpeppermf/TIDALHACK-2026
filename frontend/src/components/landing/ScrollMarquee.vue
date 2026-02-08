<script setup lang="ts">
defineProps<{
  scrollY?: number
}>()
</script>

<template>
  <div class="py-12 overflow-hidden">
    <div
      class="flex items-center gap-8 whitespace-nowrap mb-4"
      :style="{ transform: `translateX(${-((scrollY ?? 0) * 0.3) % 2000}px)` }"
    >
      <template v-for="i in 8" :key="'a-' + i">
        <span
          class="text-[10vw] md:text-[7vw] font-black leading-none tracking-[-0.04em]"
          style="color: hsl(var(--foreground) / 0.04); font-family: var(--font-heading)"
        >
          monogram
        </span>
        <span class="text-2xl" style="color: hsl(var(--primary) / 0.2)">✦</span>
      </template>
    </div>
    <div
      class="flex items-center gap-8 whitespace-nowrap"
      :style="{ transform: `translateX(${(((scrollY ?? 0) * 0.3) % 2000) - 1000}px)` }"
    >
      <template v-for="i in 8" :key="'b-' + i">
        <span
          class="text-[10vw] md:text-[7vw] font-black italic leading-none tracking-[-0.04em]"
          style="color: hsl(var(--foreground) / 0.04); font-family: var(--font-heading)"
        >
          monogram
        </span>
        <span class="text-2xl" style="color: hsl(var(--primary) / 0.15)">◆</span>
      </template>
    </div>
  </div>
</template>
