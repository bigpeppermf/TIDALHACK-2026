<script setup>
import { ref, onMounted } from 'vue'

const el = ref(null)
const isVisible = ref(false)

const props = defineProps({
  title: { type: String, required: true },
  description: { type: String, required: true },
  icon: { type: String, default: '' },
  delay: { type: Number, default: 0 },
  span: { type: String, default: '' },
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
    { threshold: 0.15 }
  )
  observer.observe(el.value)
})
</script>

<template>
  <div
    ref="el"
    class="bento-card group relative overflow-hidden rounded-lg p-8 md:p-10 cursor-default"
    :class="[
      span,
      isVisible ? 'bento-visible' : 'bento-hidden',
    ]"
    :style="{ '--bento-delay': delay + 'ms' }"
  >
    <!-- Background glow on hover -->
    <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-700"
      style="background: radial-gradient(ellipse at 50% 0%, rgba(212,165,116,0.06) 0%, transparent 70%);"
    />

    <!-- Top border accent -->
    <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#d4a574] to-transparent opacity-0 group-hover:opacity-40 transition-opacity duration-500" />

    <!-- Icon area -->
    <div class="relative z-10 mb-6">
      <div
        class="w-12 h-12 rounded-md flex items-center justify-center text-xl transition-all duration-500 group-hover:scale-110"
        style="background: rgba(212,165,116,0.08); border: 1px solid rgba(212,165,116,0.15);"
      >
        <span style="color: #d4a574;" v-html="icon" />
      </div>
    </div>

    <!-- Content -->
    <div class="relative z-10">
      <h3
        class="font-display text-lg md:text-xl font-semibold mb-3 transition-colors duration-300"
        style="color: #f5f0eb;"
      >
        {{ title }}
      </h3>
      <p
        class="text-sm leading-relaxed"
        style="color: #8a8580; font-family: 'Inter', sans-serif;"
      >
        {{ description }}
      </p>
    </div>

    <!-- Corner accent -->
    <div class="absolute bottom-0 right-0 w-24 h-24 opacity-0 group-hover:opacity-100 transition-opacity duration-700"
      style="background: radial-gradient(circle at 100% 100%, rgba(212,165,116,0.04) 0%, transparent 70%);"
    />
  </div>
</template>

<style scoped>
.bento-card {
  background: rgba(245, 240, 235, 0.02);
  border: 1px solid rgba(138, 133, 128, 0.08);
  will-change: transform, opacity;
  transition: border-color 0.4s ease, box-shadow 0.4s ease;
}

.bento-card:hover {
  border-color: rgba(212, 165, 116, 0.2);
  box-shadow: 0 0 40px rgba(212, 165, 116, 0.03);
}

.bento-hidden {
  opacity: 0;
  transform: translateY(50px) scale(0.97);
}

.bento-visible {
  opacity: 1;
  transform: translateY(0) scale(1);
  transition: transform 0.9s cubic-bezier(0.22, 1, 0.36, 1),
              opacity 0.7s cubic-bezier(0.22, 1, 0.36, 1),
              border-color 0.4s ease,
              box-shadow 0.4s ease;
  transition-delay: var(--bento-delay);
}
</style>
