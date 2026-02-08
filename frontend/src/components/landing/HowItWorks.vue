<script setup lang="ts">
import SlamText from './SlamText.vue'
import FadeIn from './FadeIn.vue'
import TimelineStep from './TimelineStep.vue'
import LineReveal from './LineReveal.vue'
import { RouterLink } from 'vue-router'

const steps = [
  {
    iconPath: 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12',
    title: 'Upload Your Notes',
    description:
      'Drag and drop your notes, equations, or diagrams. We support PDF, HTML, and LaTeX files.',
  },
  {
    iconPath: 'M13 2 3 14h9l-1 8 10-12h-9l1-8z',
    title: 'AI Processes It',
    description:
      'Our neural network reads your handwriting, recognizes mathematical structures, and converts everything into clean, semantic LaTeX code.',
  },
  {
    iconPath: 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3',
    title: 'Edit & Export',
    description:
      'Review the output in our live editor, make refinements with syntax highlighting and auto-complete, then export as LaTeX, HTML, or PDF.',
  },
]
</script>

<template>
  <!-- How It Works -->
  <section id="how-it-works" class="overflow-hidden relative">
    <div class="py-28 md:py-32 px-6 md:px-12">
      <!-- Section header -->
      <div class="mb-20">
        <FadeIn :delay="0">
          <div class="flex items-center gap-4 mb-6">
            <div class="w-12 h-px bg-primary" />
            <span class="text-primary text-[11px] tracking-[0.3em] uppercase">
              Process
            </span>
          </div>
        </FadeIn>
        <SlamText
          text="How it"
          :angle="-3"
          :delay="100"
          size="text-[14vw] md:text-[6vw]"
          weight="font-black"
        />
        <SlamText
          text="works"
          :angle="-3"
          :delay="250"
          size="text-[14vw] md:text-[6vw]"
          weight="font-black"
          :italic="true"
        />
      </div>

      <!-- Timeline -->
      <div class="max-w-2xl ml-4 md:ml-16">
        <TimelineStep
          v-for="(step, i) in steps"
          :key="step.title"
          :step="i + 1"
          :title="step.title"
          :description="step.description"
          :icon-path="step.iconPath"
          :delay="i * 200"
          :is-last="i === steps.length - 1"
        />
      </div>
    </div>
  </section>

  <!-- Final CTA -->
  <section class="overflow-hidden relative">
    <div
      class="min-h-[80vh] flex flex-col items-center justify-center px-6 py-28 text-center"
    >
      <FadeIn :delay="0">
        <span
          class="text-[11px] tracking-[0.5em] uppercase text-muted-foreground/20 mb-12 block"
        >
          Ready?
        </span>
      </FadeIn>

      <SlamText
        text="Start"
        :angle="-4"
        :delay="100"
        size="text-[16vw] md:text-[8vw]"
        weight="font-black"
        align="center"
      />
      <SlamText
        text="Converting"
        :angle="-4"
        :delay="300"
        size="text-[16vw] md:text-[8vw]"
        weight="font-black"
        :italic="true"
        align="center"
      />

      <div class="mt-16 max-w-[520px]">
        <FadeIn :delay="600">
          <p class="text-base leading-relaxed text-muted-foreground mb-12">
            Drop your handwritten notes and watch them transform into
            clean, publication-ready LaTeX in seconds. No setup required.
          </p>
        </FadeIn>

        <FadeIn :delay="800">
          <div class="flex items-center justify-center gap-5 flex-wrap">
            <RouterLink
              to="/convert"
              class="cta-primary inline-flex items-center gap-2.5 px-10 py-4 bg-primary text-primary-foreground text-[13px] font-semibold tracking-[0.1em] uppercase rounded-sm transition-all duration-400"
              style="transition-timing-function: cubic-bezier(0.22, 1, 0.36, 1)"
            >
              <span>Start Converting</span>
              <span class="text-base">→</span>
            </RouterLink>
            <a
              href="#features"
              class="cta-secondary inline-flex items-center gap-2.5 px-10 py-4 bg-transparent text-muted-foreground text-[13px] font-medium tracking-[0.1em] uppercase border border-border rounded-sm transition-all duration-400"
              style="transition-timing-function: cubic-bezier(0.22, 1, 0.36, 1)"
            >
              <span>See How It Works</span>
            </a>
          </div>
        </FadeIn>
      </div>

      <!-- File type badges -->
      <FadeIn :delay="1100">
        <div class="mt-16 flex items-center gap-3">
          <span
            v-for="format in ['PDF', 'HTML', 'LaTeX']"
            :key="format"
            class="px-4 py-1.5 rounded-full text-[11px] tracking-[0.15em] border border-border/30 text-muted-foreground/40"
          >
            {{ format }}
          </span>
        </div>
      </FadeIn>
    </div>
  </section>

  <!-- Final brand statement -->
  <section class="overflow-hidden relative">
    <LineReveal :delay="0" />

    <div
      class="min-h-[60vh] flex flex-col items-center justify-center px-6 py-20"
    >
      <SlamText
        text="monogram"
        :angle="0"
        :delay="200"
        size="text-[12vw] md:text-[8vw]"
        weight="font-black"
        align="center"
      />

      <FadeIn :delay="600">
        <p class="text-[11px] tracking-[0.4em] uppercase text-muted-foreground/40 mt-16">
          Crafted with obsession
        </p>
      </FadeIn>
    </div>

    <LineReveal :delay="400" />
  </section>
</template>
