<script setup lang="ts">
import { ref, onMounted } from 'vue'

const el = ref<HTMLElement | null>(null)
const isVisible = ref(false)

const props = defineProps<{
  delay?: number
  direction?: 'up' | 'down' | 'left' | 'right'
}>()

const delay = props.delay ?? 0
const direction = props.direction ?? 'up'

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
    { threshold: 0.1 },
  )
  observer.observe(el.value)
})
</script>

<template>
  <div
    ref="el"
    class="fade-element"
    :class="isVisible ? 'fade-visible' : 'fade-hidden'"
    :style="{
      '--fade-delay': delay + 'ms',
      '--fade-x': direction === 'left' ? '40px' : direction === 'right' ? '-40px' : '0px',
      '--fade-y': direction === 'up' ? '40px' : direction === 'down' ? '-40px' : '0px',
    }"
  >
    <slot />
  </div>
</template>

<style scoped>
.fade-element {
  will-change: transform, opacity;
}

.fade-hidden {
  opacity: 0;
  transform: translate(var(--fade-x), var(--fade-y));
}

.fade-visible {
  opacity: 1;
  transform: translate(0, 0);
  transition:
    transform 0.8s cubic-bezier(0.22, 1, 0.36, 1),
    opacity 0.8s cubic-bezier(0.22, 1, 0.36, 1);
  transition-delay: var(--fade-delay);
}
</style>
