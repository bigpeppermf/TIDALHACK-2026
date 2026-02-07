<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'

type Stage = { text: string; duration: number }

const stages: [Stage, ...Stage[]] = [
  { text: 'Reading your handwriting...', duration: 1800 },
  { text: 'Recognizing equations...', duration: 2200 },
  { text: 'Converting to LaTeX...', duration: 2000 },
  { text: 'Almost done...', duration: 1500 },
]

const stageIndex = ref(0)
const dots = ref('')
const rotation = ref(0)
const currentStage = computed<Stage>(
  () => stages[stageIndex.value] ?? stages[stages.length - 1]!,
)

const timers: ReturnType<typeof setTimeout>[] = []
let dotsInterval: ReturnType<typeof setInterval> | null = null
let rotInterval: ReturnType<typeof setInterval> | null = null

function advanceStage() {
  if (stageIndex.value >= stages.length - 1) return
  const timer = setTimeout(() => {
    stageIndex.value = Math.min(stageIndex.value + 1, stages.length - 1)
    advanceStage()
  }, currentStage.value.duration)
  timers.push(timer)
}

onMounted(() => {
  advanceStage()

  dotsInterval = setInterval(() => {
    dots.value = dots.value.length >= 3 ? '' : dots.value + '.'
  }, 500)

  rotInterval = setInterval(() => {
    rotation.value += 360
  }, 2000)
})

onUnmounted(() => {
  for (const t of timers) clearTimeout(t)
  if (dotsInterval) clearInterval(dotsInterval)
  if (rotInterval) clearInterval(rotInterval)
})

function progressWidth(): string {
  return `${((stageIndex.value + 1) / stages.length) * 100}%`
}
</script>

<template>
  <div class="flex flex-col items-center gap-8 py-16">
    <!-- Spinning pen icon -->
    <div class="relative">
      <div class="absolute -inset-4 rounded-full bg-primary/10 blur-xl" />
      <div
        class="relative flex h-20 w-20 items-center justify-center rounded-2xl border border-border bg-card"
        :style="{
          transform: `rotate(${rotation}deg)`,
          transition: 'transform 2s cubic-bezier(0.4, 0, 0.2, 1)',
        }"
      >
        <svg
          viewBox="0 0 24 24"
          fill="none"
          class="h-8 w-8 text-primary"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z" />
        </svg>
      </div>
    </div>

    <!-- Progress bar -->
    <div class="w-full max-w-xs">
      <div class="h-1 w-full overflow-hidden rounded-full bg-secondary">
        <div
          class="h-full rounded-full bg-primary transition-all duration-1000 ease-out"
          :style="{ width: progressWidth() }"
        />
      </div>
    </div>

    <!-- Status text -->
    <div class="text-center">
      <p class="text-lg font-medium text-foreground">
        {{ currentStage.text }}
      </p>
      <p class="mt-1 font-mono text-sm text-muted-foreground">
        Processing{{ dots }}
      </p>
    </div>

    <!-- Step indicators -->
    <div class="flex gap-3">
      <div
        v-for="(stage, i) in stages"
        :key="stage.text"
        :class="[
          'h-2 w-2 rounded-full transition-all duration-500',
          i <= stageIndex ? 'scale-100 bg-primary' : 'scale-75 bg-[hsl(var(--border))]',
        ]"
      />
    </div>
  </div>
</template>
