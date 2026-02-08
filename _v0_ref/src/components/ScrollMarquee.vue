<script setup>
const props = defineProps({
  scrollY: { type: Number, default: 0 },
})
</script>

<template>
  <div class="py-12 overflow-hidden">
    <div
      class="flex items-center gap-8 whitespace-nowrap mb-4"
      :style="{ transform: `translateX(${-(scrollY * 0.3) % 2000}px)` }"
    >
      <template v-for="i in 8" :key="'a-' + i">
        <span class="text-[10vw] md:text-[7vw] font-display font-black leading-none tracking-[-0.04em]" style="color: rgba(245, 240, 235, 0.05)">
          monograph
        </span>
        <span style="color: rgba(212, 165, 116, 0.2)" class="text-2xl">&#x2726;</span>
      </template>
    </div>
    <div
      class="flex items-center gap-8 whitespace-nowrap"
      :style="{ transform: `translateX(${((scrollY * 0.3) % 2000) - 1000}px)` }"
    >
      <template v-for="i in 8" :key="'b-' + i">
        <span class="text-[10vw] md:text-[7vw] font-display font-black italic leading-none tracking-[-0.04em]" style="color: rgba(245, 240, 235, 0.05)">
          monograph
        </span>
        <span style="color: rgba(232, 201, 160, 0.2)" class="text-2xl">&#x25C6;</span>
      </template>
    </div>
  </div>
</template>
