<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface Feature {
  iconPath: string
  title: string
  description: string
  span?: string
}

const features: Feature[] = [
  {
    iconPath: 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12',
    title: 'Drag & Drop Upload',
    description:
      'Simply drag your handwritten notes into the upload zone. Supports JPEG, PNG, and WebP formats up to 10MB.',
    span: 'md:col-span-2',
  },
  {
    iconPath: 'M13 2 3 14h9l-1 8 10-12h-9l1-8z',
    title: 'AI-Powered OCR',
    description:
      'Powered by Gemini vision models for state-of-the-art handwriting recognition and LaTeX generation.',
  },
  {
    iconPath: 'M16 18 22 12 16 6M8 6 2 12 8 18',
    title: 'Clean LaTeX Output',
    description:
      'Get perfectly formatted LaTeX code ready for your papers, assignments, or publications.',
  },
  {
    iconPath: 'M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7ZM12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z',
    title: 'Live Preview',
    description:
      'See your LaTeX rendered in real-time as you edit. Side-by-side view with your original handwritten notes.',
    span: 'md:col-span-2',
  },
  {
    iconPath: 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3',
    title: 'Export Options',
    description:
      'Download as .tex file or copy raw LaTeX to clipboard instantly. Ready for Overleaf or any LaTeX editor.',
  },
  {
    iconPath: 'M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2M9 2h6v4H9V2Z',
    title: 'Edit & Refine',
    description:
      'Built-in editor lets you tweak the generated LaTeX. Changes reflect instantly in the preview.',
    span: 'md:col-span-3',
  },
]

// Intersection observer for scroll animations
const cardRefs = ref<(HTMLElement | null)[]>([])
const visibleCards = ref<Set<number>>(new Set())
let observer: IntersectionObserver | null = null

function setCardRef(el: HTMLElement | null, index: number) {
  cardRefs.value[index] = el
}

onMounted(() => {
  observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          const idx = Number(entry.target.getAttribute('data-index'))
          visibleCards.value = new Set(visibleCards.value).add(idx)
          observer?.unobserve(entry.target)
        }
      }
    },
    { threshold: 0.15 }
  )
  for (const el of cardRefs.value) {
    if (el) observer.observe(el)
  }
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>

<template>
  <section id="features" class="relative py-24">
    <div class="mx-auto max-w-7xl px-6">
      <!-- Section header -->
      <div class="mb-16 text-center">
        <p class="mb-3 text-sm font-medium uppercase tracking-widest text-primary">
          Features
        </p>
        <h2
          class="mb-4 text-3xl font-bold text-foreground md:text-5xl"
          style="text-wrap: balance"
        >
          Everything you need to convert notes
        </h2>
        <p
          class="mx-auto max-w-2xl text-muted-foreground"
          style="text-wrap: pretty"
        >
          From upload to export, monogram handles the entire workflow with
          precision and speed.
        </p>
      </div>

      <!-- Bento grid -->
      <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div
          v-for="(feature, i) in features"
          :key="feature.title"
          :ref="(el) => setCardRef(el as HTMLElement | null, i)"
          :data-index="i"
          :class="[
            'group relative overflow-hidden rounded-xl border border-border bg-card p-6 transition-all duration-700 hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5',
            feature.span ?? '',
            visibleCards.has(i) ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0',
          ]"
          :style="{ transitionDelay: `${i * 100}ms` }"
        >
          <!-- Hover glow -->
          <div
            class="absolute inset-0 bg-gradient-to-br from-[hsl(var(--primary)/0.05)] via-transparent to-transparent opacity-0 transition-opacity group-hover:opacity-100"
          />

          <div class="relative z-10">
            <div
              class="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary"
            >
              <svg
                class="h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path :d="feature.iconPath" />
              </svg>
            </div>
            <h3 class="mb-2 text-lg font-semibold text-foreground">
              {{ feature.title }}
            </h3>
            <p class="text-sm leading-relaxed text-muted-foreground">
              {{ feature.description }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
