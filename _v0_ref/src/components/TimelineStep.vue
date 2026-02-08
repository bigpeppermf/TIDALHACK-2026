<script setup>
import { ref, onMounted } from 'vue'

const el = ref(null)
const isVisible = ref(false)

const props = defineProps({
  step: { type: Number, required: true },
  title: { type: String, required: true },
  description: { type: String, required: true },
  icon: { type: String, default: '' },
  delay: { type: Number, default: 0 },
  isLast: { type: Boolean, default: false },
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
    { threshold: 0.2 }
  )
  observer.observe(el.value)
})
</script>

<template>
  <div
    ref="el"
    class="timeline-step relative flex gap-8 md:gap-12"
    :class="isVisible ? 'tl-visible' : 'tl-hidden'"
    :style="{ '--tl-delay': delay + 'ms' }"
  >
    <!-- Left: number + line -->
    <div class="flex flex-col items-center flex-shrink-0">
      <!-- Number circle -->
      <div
        class="w-14 h-14 rounded-full flex items-center justify-center relative z-10 transition-all duration-500"
        :style="{
          background: isVisible ? 'rgba(212,165,116,0.1)' : 'rgba(138,133,128,0.05)',
          border: '1px solid ' + (isVisible ? 'rgba(212,165,116,0.3)' : 'rgba(138,133,128,0.1)'),
        }"
      >
        <span
          class="font-display text-xl font-bold"
          :style="{ color: isVisible ? '#d4a574' : '#8a8580' }"
        >
          {{ String(step).padStart(2, '0') }}
        </span>
      </div>

      <!-- Connector line -->
      <div
        v-if="!isLast"
        class="timeline-connector w-px flex-1 mt-4 mb-4"
        :class="isVisible ? 'connector-visible' : 'connector-hidden'"
        :style="{ '--tl-delay': (delay + 300) + 'ms' }"
      />
    </div>

    <!-- Right: content -->
    <div class="pb-16 md:pb-20 pt-1">
      <div
        class="w-10 h-10 rounded-md flex items-center justify-center mb-5 transition-all duration-500"
        style="background: rgba(212,165,116,0.06); border: 1px solid rgba(212,165,116,0.12);"
      >
        <span style="color: #d4a574;" v-html="icon" />
      </div>
      <h3
        class="font-display text-xl md:text-2xl font-semibold mb-3"
        style="color: #f5f0eb;"
      >
        {{ title }}
      </h3>
      <p
        class="text-sm leading-relaxed max-w-md"
        style="color: #8a8580; font-family: 'Inter', sans-serif;"
      >
        {{ description }}
      </p>
    </div>
  </div>
</template>

<style scoped>
.timeline-step {
  will-change: transform, opacity;
}

.tl-hidden {
  opacity: 0;
  transform: translateX(-30px);
}

.tl-visible {
  opacity: 1;
  transform: translateX(0);
  transition: transform 0.9s cubic-bezier(0.22, 1, 0.36, 1),
              opacity 0.7s cubic-bezier(0.22, 1, 0.36, 1);
  transition-delay: var(--tl-delay);
}

.timeline-connector {
  transform-origin: top center;
}

.connector-hidden {
  background: rgba(138, 133, 128, 0.08);
  transform: scaleY(0);
}

.connector-visible {
  transform: scaleY(1);
  transition: transform 1s cubic-bezier(0.22, 1, 0.36, 1);
  transition-delay: var(--tl-delay);
  background: linear-gradient(to bottom, rgba(212,165,116,0.3), rgba(212,165,116,0.05));
}
</style>
