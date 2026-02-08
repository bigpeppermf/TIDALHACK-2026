<script setup>
import { ref, onMounted, watch } from 'vue'

const el = ref(null)
const isVisible = ref(false)
const displayValue = ref(0)

const props = defineProps({
  value: { type: Number, required: true },
  suffix: { type: String, default: '' },
  prefix: { type: String, default: '' },
  label: { type: String, required: true },
  delay: { type: Number, default: 0 },
  duration: { type: Number, default: 1800 },
})

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
    { threshold: 0.3 }
  )
  observer.observe(el.value)
})

watch(isVisible, (val) => {
  if (!val) return
  setTimeout(() => {
    const start = performance.now()
    const animate = (now) => {
      const elapsed = now - start
      const progress = Math.min(elapsed / props.duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      displayValue.value = Math.round(eased * props.value)
      if (progress < 1) requestAnimationFrame(animate)
    }
    requestAnimationFrame(animate)
  }, props.delay)
})
</script>

<template>
  <div
    ref="el"
    class="stat-item"
    :class="isVisible ? 'stat-visible' : 'stat-hidden'"
    :style="{ '--stat-delay': delay + 'ms' }"
  >
    <span
      class="font-display text-[12vw] md:text-[4vw] font-black leading-none tracking-tight"
      style="color: #f5f0eb;"
    >
      {{ prefix }}{{ displayValue }}{{ suffix }}
    </span>
    <span
      class="block mt-3 text-xs tracking-[0.3em] uppercase"
      style="color: #8a8580; font-family: 'Inter', sans-serif;"
    >
      {{ label }}
    </span>
  </div>
</template>

<style scoped>
.stat-item {
  will-change: transform, opacity;
}
.stat-hidden {
  opacity: 0;
  transform: translateY(30px);
}
.stat-visible {
  opacity: 1;
  transform: translateY(0);
  transition: transform 0.8s cubic-bezier(0.22, 1, 0.36, 1),
              opacity 0.6s cubic-bezier(0.22, 1, 0.36, 1);
  transition-delay: var(--stat-delay);
}
</style>
