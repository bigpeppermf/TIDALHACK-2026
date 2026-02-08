<script setup lang="ts">
import { ref, onMounted } from 'vue'

const el = ref<HTMLElement | null>(null)
const isVisible = ref(false)

const props = defineProps<{
  step: number
  title: string
  description: string
  iconPath: string
  delay?: number
  isLast?: boolean
}>()

const delay = props.delay ?? 0

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
    { threshold: 0.2 },
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
          background: isVisible ? 'hsl(var(--primary) / 0.1)' : 'hsl(var(--muted) / 0.3)',
          border: '1px solid ' + (isVisible ? 'hsl(var(--primary) / 0.3)' : 'hsl(var(--border))'),
        }"
      >
        <span
          class="text-xl font-bold"
          :style="{
            color: isVisible ? 'hsl(var(--primary))' : 'hsl(var(--muted-foreground))',
            fontFamily: 'var(--font-heading)',
          }"
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
        style="background: hsl(var(--primary) / 0.06); border: 1px solid hsl(var(--primary) / 0.12)"
      >
        <svg
          class="h-5 w-5"
          style="color: hsl(var(--primary))"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path :d="iconPath" />
        </svg>
      </div>
      <h3
        class="text-xl md:text-2xl font-semibold mb-3 text-foreground"
        style="font-family: var(--font-heading)"
      >
        {{ title }}
      </h3>
      <p class="text-sm leading-relaxed max-w-md text-muted-foreground">
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
  transition:
    transform 0.9s cubic-bezier(0.22, 1, 0.36, 1),
    opacity 0.7s cubic-bezier(0.22, 1, 0.36, 1);
  transition-delay: var(--tl-delay);
}

.timeline-connector {
  transform-origin: top center;
}

.connector-hidden {
  background: hsl(var(--border));
  transform: scaleY(0);
}

.connector-visible {
  transform: scaleY(1);
  transition: transform 1s cubic-bezier(0.22, 1, 0.36, 1);
  transition-delay: var(--tl-delay);
  background: linear-gradient(to bottom, hsl(var(--primary) / 0.3), hsl(var(--primary) / 0.05));
}
</style>
