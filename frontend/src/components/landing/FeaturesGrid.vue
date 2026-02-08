<script setup lang="ts">
import SlamText from './SlamText.vue'
import FadeIn from './FadeIn.vue'
import BentoCard from './BentoCard.vue'
import LineReveal from './LineReveal.vue'
import ScrollMarquee from './ScrollMarquee.vue'
import { ref, onMounted, onUnmounted } from 'vue'

const scrollY = ref(0)

function onScroll() {
  scrollY.value = window.scrollY
}

onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
})

const features = [
  {
    iconPath: 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12',
    title: 'Drag & Drop Upload',
    description:
      'Simply drop your handwritten notes. We accept PDF, HTML, and LaTeX formats up to 10MB.',
    span: 'md:col-span-2',
  },
  {
    iconPath: 'M13 2 3 14h9l-1 8 10-12h-9l1-8z',
    title: 'Gemini OCR Engine',
    description:
      'Neural networks trained on millions of equations recognize your handwriting with remarkable precision.',
  },
  {
    iconPath: 'M16 18 22 12 16 6M8 6 2 12 8 18',
    title: 'Clean LaTeX Output',
    description:
      'Production-ready LaTeX code, properly formatted and immediately compilable.',
  },
  {
    iconPath: 'M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7ZM12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z',
    title: 'Live Preview',
    description:
      'Watch your LaTeX render in real-time as the AI processes each symbol and structure.',
    span: 'md:col-span-2',
  },
  {
    iconPath: 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3',
    title: 'Export Options',
    description:
      'Download as LaTeX, HTML, or PDF. Share or integrate into your existing workflow.',
    span: 'md:col-span-2',
  },
  {
    iconPath: 'M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2M9 2h6v4H9V2Z',
    title: 'Edit & Refine',
    description:
      'Full-featured editor with syntax highlighting, auto-completion, and instant recompilation.',
  },
]
</script>

<template>
  <!-- Features Section -->
  <section id="features" class="overflow-hidden relative">
    <LineReveal :delay="0" />

    <div class="py-28 md:py-32 px-6 md:px-12">
      <!-- Section header -->
      <div class="mb-20">
        <FadeIn :delay="0">
          <div class="flex items-center gap-4 mb-6">
            <div class="w-12 h-px bg-primary" />
            <span class="text-primary text-[11px] tracking-[0.3em] uppercase">
              Capabilities
            </span>
          </div>
        </FadeIn>
        <SlamText
          text="Features"
          :angle="-3"
          :delay="100"
          size="text-[14vw] md:text-[6vw]"
          weight="font-black"
        />
      </div>

      <!-- Bento grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-5 max-w-6xl">
        <BentoCard
          v-for="(feature, i) in features"
          :key="feature.title"
          :title="feature.title"
          :description="feature.description"
          :icon-path="feature.iconPath"
          :delay="i * 100"
          :span="feature.span"
        />
      </div>
    </div>
  </section>

  <!-- Marquee -->
  <section class="overflow-hidden relative py-8">
    <LineReveal :delay="0" />
    <ScrollMarquee :scroll-y="scrollY" />
    <LineReveal :delay="200" />
  </section>
</template>
