<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const steps = [
  {
    iconPath: 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12',
    step: '01',
    title: 'Upload Your Notes',
    description:
      'Take a photo or scan of your handwritten notes and drag it into monograph. We support JPEG, PNG, and WebP.',
  },
  {
    iconPath: 'M6.5 6.5h11v11h-11zM12 2v4M12 18v4M2 12h4M18 12h4',
    step: '02',
    title: 'AI Processes It',
    description:
      'Our AI model reads your handwriting and converts it into structured LaTeX code, preserving mathematical notation.',
  },
  {
    iconPath: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8ZM14 2v6h6M16 13H8M16 17H8M10 9H8',
    step: '03',
    title: 'Edit & Export',
    description:
      'Review the generated LaTeX with live preview. Edit inline, then copy or download the .tex file.',
  },
]

const stepRefs = ref<(HTMLElement | null)[]>([])
const visibleSteps = ref<Set<number>>(new Set())
let observer: IntersectionObserver | null = null

function setStepRef(el: HTMLElement | null, index: number) {
  stepRefs.value[index] = el
}

onMounted(() => {
  observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          const idx = Number(entry.target.getAttribute('data-index'))
          visibleSteps.value = new Set(visibleSteps.value).add(idx)
          observer?.unobserve(entry.target)
        }
      }
    },
    { threshold: 0.2 }
  )
  for (const el of stepRefs.value) {
    if (el) observer.observe(el)
  }
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>

<template>
  <section id="how-it-works" class="relative border-t border-border/50 py-24">
    <div class="mx-auto max-w-5xl px-6">
      <!-- Section header -->
      <div class="mb-16 text-center">
        <p class="mb-3 text-sm font-medium uppercase tracking-widest text-primary">
          How It Works
        </p>
        <h2
          class="mb-4 text-3xl font-bold text-foreground md:text-5xl"
          style="text-wrap: balance"
        >
          Three simple steps
        </h2>
        <p
          class="mx-auto max-w-xl text-muted-foreground"
          style="text-wrap: pretty"
        >
          No setup, no configuration. Upload and get your LaTeX.
        </p>
      </div>

      <!-- Steps -->
      <div class="relative flex flex-col gap-12 md:gap-16">
        <!-- Vertical connector line -->
        <div
          class="absolute left-6 top-0 bottom-0 hidden w-px bg-gradient-to-b from-[hsl(var(--primary)/0.3)] via-[hsl(var(--primary)/0.1)] to-transparent md:left-8 md:block"
        />

        <div
          v-for="(step, i) in steps"
          :key="step.step"
          :ref="(el) => setStepRef(el as HTMLElement | null, i)"
          :data-index="i"
          :class="[
            'relative flex gap-6 transition-all duration-700 md:gap-8',
            visibleSteps.has(i) ? 'translate-x-0 opacity-100' : '-translate-x-8 opacity-0',
          ]"
          :style="{ transitionDelay: `${i * 200}ms` }"
        >
          <!-- Step icon circle -->
          <div
            class="relative z-10 flex h-12 w-12 shrink-0 items-center justify-center rounded-full border border-primary/30 bg-card text-primary md:h-16 md:w-16"
          >
            <svg
              class="h-6 w-6"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path :d="step.iconPath" />
            </svg>
          </div>

          <!-- Content -->
          <div class="flex-1 pt-1 md:pt-3">
            <span class="mb-1 block font-mono text-xs text-primary">{{ step.step }}</span>
            <h3 class="mb-2 text-xl font-semibold text-foreground">{{ step.title }}</h3>
            <p class="max-w-md text-sm leading-relaxed text-muted-foreground">
              {{ step.description }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
