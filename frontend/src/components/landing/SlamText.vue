<script setup lang="ts">
import { ref, onMounted } from 'vue'

const el = ref<HTMLElement | null>(null)
const isVisible = ref(false)

const props = defineProps<{
  text: string
  angle?: number
  delay?: number
  size?: string
  align?: 'left' | 'center' | 'right'
  italic?: boolean
  weight?: string
}>()

const angle = props.angle ?? -5
const delay = props.delay ?? 0
const size = props.size ?? 'text-8xl'
const align = props.align ?? 'left'
const weight = props.weight ?? 'font-bold'

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
  <div ref="el" class="overflow-hidden">
    <div
      class="slam-text leading-[0.85] tracking-[-0.04em]"
      :class="[
        size,
        weight,
        italic ? 'italic' : '',
        align === 'right' ? 'text-right' : align === 'center' ? 'text-center' : 'text-left',
        isVisible ? 'slam-visible' : 'slam-hidden',
      ]"
      :style="{
        '--slam-angle': angle + 'deg',
        '--slam-angle-start': (angle + 8) + 'deg',
        '--slam-delay': delay + 'ms',
        color: 'hsl(var(--foreground))',
        fontFamily: 'var(--font-heading)',
        transformOrigin: align === 'right' ? 'bottom right' : 'bottom left',
      }"
    >
      {{ text }}
    </div>
  </div>
</template>

<style scoped>
.slam-text {
  will-change: transform, opacity;
}

.slam-hidden {
  opacity: 0;
  transform: rotate(var(--slam-angle-start)) translateY(-120%) scale(1.4);
}

.slam-visible {
  opacity: 1;
  transform: rotate(var(--slam-angle)) translateY(0) scale(1);
  transition:
    transform 0.9s cubic-bezier(0.22, 1, 0.36, 1),
    opacity 0.6s cubic-bezier(0.22, 1, 0.36, 1);
  transition-delay: var(--slam-delay);
}
</style>
