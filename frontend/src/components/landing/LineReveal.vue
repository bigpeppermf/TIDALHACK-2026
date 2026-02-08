<script setup lang="ts">
import { ref, onMounted } from 'vue'

const el = ref<HTMLElement | null>(null)
const isVisible = ref(false)

const props = defineProps<{
  delay?: number
  direction?: 'horizontal' | 'vertical'
}>()

const delay = props.delay ?? 0
const direction = props.direction ?? 'horizontal'

onMounted(() => {
  if (!el.value) return
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          isVisible.value = true
          observer.unobserve(entry.target)
        }
      })
    },
    { threshold: 0.05 },
  )
  observer.observe(el.value)
})
</script>

<template>
  <div
    ref="el"
    :class="direction === 'horizontal' ? 'h-px w-full' : 'w-px h-full'"
  >
    <div
      :class="[
        direction === 'horizontal' ? 'h-full w-full line-h' : 'w-full h-full line-v',
        isVisible ? 'scale-full' : 'scale-zero',
      ]"
      :style="{ '--line-delay': delay + 'ms', backgroundColor: 'hsl(var(--border))' }"
    />
  </div>
</template>

<style scoped>
.line-h {
  transform-origin: left center;
  transition: transform 1.2s cubic-bezier(0.22, 1, 0.36, 1);
  transition-delay: var(--line-delay);
}

.line-v {
  transform-origin: top center;
  transition: transform 1.2s cubic-bezier(0.22, 1, 0.36, 1);
  transition-delay: var(--line-delay);
}

.scale-zero.line-h {
  transform: scaleX(0);
}

.scale-zero.line-v {
  transform: scaleY(0);
}

.scale-full.line-h {
  transform: scaleX(1);
}

.scale-full.line-v {
  transform: scaleY(1);
}
</style>
