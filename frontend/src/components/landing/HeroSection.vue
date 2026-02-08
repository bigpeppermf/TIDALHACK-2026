<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import SlamText from './SlamText.vue'
import FadeIn from './FadeIn.vue'

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
</script>

<template>

  <section
    class="relative flex min-h-screen items-center overflow-hidden"
    style="background-color: hsl(var(--background))"
  >
    <!-- Floating decorative line -->
    <div
      class="absolute top-0 right-[12%] w-px h-[60vh] hidden md:block"
      style="background: hsl(var(--border) / 0.18)"
      :style="{ transform: 'translateY(' + scrollY * 0.12 + 'px)' }"
    />

    <div class="w-full max-w-7xl mx-auto px-4 md:px-10 py-24 flex flex-col items-center">
      <!-- Slam title -->
      <div class="flex flex-col items-center w-full">
        <SlamText
          text="mono"
          :angle="-6"
          :delay="200"
          size="text-[16vw] md:text-[10vw] lg:text-[9vw]"
          weight="font-black"
        />
        <SlamText
          text="gram"
          :angle="-6"
          :delay="500"
          size="text-[16vw] md:text-[10vw] lg:text-[9vw]"
          weight="font-black"
          :italic="true"
        />
      </div>

      <!-- Subtitle & CTA -->
      <div class="mt-14 w-full max-w-xl flex flex-col items-center text-center">
        <FadeIn :delay="900">
          <p class="text-xs md:text-sm tracking-[0.18em] uppercase text-muted-foreground font-semibold">
            Handwriting to LaTeX, instantly
          </p>
        </FadeIn>
        <FadeIn :delay="1100">
          <p class="mt-4 text-base md:text-lg leading-relaxed text-muted-foreground/70 font-normal">
            Upload your handwritten notes and watch them transform into clean, publication-ready LaTeX in seconds. Powered by AI.
          </p>
        </FadeIn>

        <!-- CTA Buttons -->
        <FadeIn :delay="1300">
          <div class="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4 w-full">
            <RouterLink
              to="/convert"
              class="cta-primary inline-flex items-center justify-center gap-2.5 px-8 py-3 bg-primary text-primary-foreground text-[15px] font-semibold tracking-[0.12em] uppercase rounded-md shadow-sm hover:scale-[1.03] transition-all duration-300"
              style="transition-timing-function: cubic-bezier(0.22, 1, 0.36, 1)"
            >
              <span>Start Converting</span>
              <span class="text-lg">→</span>
            </RouterLink>
            <a
              href="#how-it-works"
              class="cta-secondary inline-flex items-center justify-center gap-2.5 px-8 py-3 bg-transparent text-muted-foreground text-[15px] font-medium tracking-[0.12em] uppercase border border-border rounded-md hover:bg-secondary/30 hover:text-foreground transition-all duration-300"
              style="transition-timing-function: cubic-bezier(0.22, 1, 0.36, 1)"
            >
              <span>See How It Works</span>
            </a>
          </div>
        </FadeIn>

        <!-- File type badges -->
        <FadeIn :delay="1500">
          <div class="mt-8 flex flex-wrap items-center justify-center gap-2">
            <span
              v-for="format in ['PDF', 'HTML', 'LaTeX']"
              :key="format"
              class="px-3 py-1 rounded-full text-[11px] tracking-[0.13em] border border-border/30 text-muted-foreground/50 font-medium"
            >
              {{ format }}
            </span>
          </div>
        </FadeIn>
      </div>
    </div>

    <!-- Scroll indicator -->
    <div class="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2">
      <FadeIn :delay="1700">
        <span class="text-[11px] tracking-[0.3em] uppercase text-muted-foreground/40 font-medium">
          Scroll
        </span>
      </FadeIn>
      <FadeIn :delay="1900">
        <div class="scroll-line w-px h-10" style="background: hsl(var(--border) / 0.22)" />
      </FadeIn>
    </div>
  </section>

</template>
