<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { motion, AnimatePresence } from 'motion-v'

const heroRef = ref<HTMLElement | null>(null)
const started = ref(false)

// ── Animation phases ──
// Phase 1: Handwritten — "monograph" appears in a handwriting style with an ink stroke effect
// Phase 2: Select — a purple highlight sweeps across, "selecting" the handwritten text
// Phase 3: Fall — text falls from the very TOP of the page, heavy spring with bounce
// Phase 4: Glow — mouse-reactive dramatic purple shadow

type Phase = 'idle' | 'handwriting' | 'selecting' | 'falling' | 'glowing'
const phase = ref<Phase>('idle')

const showHandwritten = ref(false)
const selectWidth = ref(0)
const showFinal = ref(false)
const hideHandwritten = ref(false)

// ── Mouse glow tracking ──
const mouseX = ref(0.5)
const mouseY = ref(0.5)

const glowStyle = computed(() => {
  if (phase.value !== 'glowing') return {}

  const dx = (mouseX.value - 0.5) * 80
  const dy = (mouseY.value - 0.5) * 80

  return {
    textShadow: [
      `${dx * 0.2}px ${dy * 0.2}px 6px hsl(var(--primary) / 0.6)`,
      `${dx * 0.4}px ${dy * 0.4}px 16px hsl(var(--primary) / 0.45)`,
      `${dx * 0.7}px ${dy * 0.7}px 32px hsl(var(--primary) / 0.3)`,
      `${dx}px ${dy}px 55px hsl(var(--primary) / 0.2)`,
      `${dx * 1.3}px ${dy * 1.3}px 80px hsl(var(--primary) / 0.12)`,
      `${dx * 1.6}px ${dy * 1.6}px 120px hsl(var(--primary) / 0.06)`,
    ].join(', '),
  }
})

function onMouseMove(e: MouseEvent) {
  if (!heroRef.value) return
  const rect = heroRef.value.getBoundingClientRect()
  mouseX.value = (e.clientX - rect.left) / rect.width
  mouseY.value = (e.clientY - rect.top) / rect.height
}

// ── Sequencer ──
function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms))
}

async function runSequence() {
  if (started.value) return
  started.value = true

  // Phase 1: Handwritten text appears with ink-stroke reveal
  phase.value = 'handwriting'
  showHandwritten.value = true
  await sleep(1800) // let the stroke animation play

  // Phase 2: Selection sweep over the handwritten text
  phase.value = 'selecting'
  const steps = 24
  for (let i = 1; i <= steps; i++) {
    selectWidth.value = (i / steps) * 100
    await sleep(16)
  }
  await sleep(600)

  // Phase 3: Hide handwritten, show final falling text
  hideHandwritten.value = true
  await sleep(200)
  phase.value = 'falling'
  showFinal.value = true
  await sleep(1600) // spring fall animation

  // Phase 4: Glow active
  phase.value = 'glowing'
}

let observer: IntersectionObserver | null = null

onMounted(() => {
  observer = new IntersectionObserver(
    ([entry]) => {
      if (entry?.isIntersecting) {
        runSequence()
      }
    },
    { threshold: 0.3 },
  )
  if (heroRef.value) observer.observe(heroRef.value)
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>

<template>
  <section
    ref="heroRef"
    class="relative flex min-h-screen items-center overflow-hidden"
    @mousemove="onMouseMove"
  >
    <div class="absolute inset-0 bg-grid-pattern opacity-20" />

    <div class="relative z-10 mx-auto flex w-full max-w-7xl justify-center px-6 pt-24 pb-16">
      <div class="flex max-w-4xl flex-col items-center text-center">

        <!-- ── Phase 1 & 2: Handwritten + Selection ── -->
        <div
          v-if="showHandwritten && !hideHandwritten"
          class="handwritten-stage"
        >
          <svg class="handwritten-svg" viewBox="0 0 600 100" xmlns="http://www.w3.org/2000/svg">
            <text
              x="50%"
              y="70"
              text-anchor="middle"
              class="handwritten-text-svg"
            >
              monograph
            </text>
          </svg>

          <!-- Selection overlay -->
          <div
            v-if="phase === 'selecting'"
            class="select-overlay"
            :style="{ width: selectWidth + '%' }"
          />
        </div>

        <!-- ── Phase 3 & 4: Fall from Top + Glow ── -->
        <div v-if="showFinal" class="fall-stage">
          <motion.span
            :initial="{ opacity: 0, y: '-60vh', scale: 0.7, filter: 'blur(12px)', rotate: -8 }"
            :animate="{ opacity: 1, y: 0, scale: 1, filter: 'blur(0px)', rotate: 0 }"
            :transition="{
              type: 'spring',
              stiffness: 80,
              damping: 12,
              mass: 1.2,
              velocity: 2,
            }"
            class="fall-word mono-word"
            :style="glowStyle"
          >
            mono
          </motion.span>
          <motion.span
            :initial="{ opacity: 0, y: '-65vh', scale: 0.7, filter: 'blur(12px)', rotate: 5 }"
            :animate="{ opacity: 1, y: 0, scale: 1, filter: 'blur(0px)', rotate: 0 }"
            :transition="{
              type: 'spring',
              stiffness: 70,
              damping: 11,
              mass: 1.4,
              velocity: 2,
              delay: 0.12,
            }"
            class="fall-word graph-word"
            :style="glowStyle"
          >
            graph
          </motion.span>
        </div>

        <motion.p
          :initial="{ opacity: 0, y: 20 }"
          :animate="showFinal ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }"
          :transition="{ duration: 0.6, delay: 0.6 }"
          class="mt-10 max-w-2xl text-center text-lg text-muted-foreground md:text-xl"
        >
          Upload your notes and shape the page around this motion-led identity. Keep iterating on layout while this
          title animation anchors the hero.
        </motion.p>

        <motion.div
          :initial="{ opacity: 0, y: 20 }"
          :animate="showFinal ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }"
          :transition="{ duration: 0.6, delay: 0.8 }"
          class="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row"
        >
          <RouterLink
            to="/convert"
            class="inline-flex items-center gap-2 rounded-md bg-primary px-6 py-3 text-sm font-medium text-primary-foreground transition-colors hover:bg-[hsl(var(--primary)/0.9)]"
          >
            Start Converting
          </RouterLink>
          <a
            href="#how-it-works"
            class="inline-flex items-center gap-2 rounded-md border border-border bg-transparent px-6 py-3 text-sm font-medium text-foreground transition-colors hover:bg-secondary"
          >
            See How It Works
          </a>
        </motion.div>

        <motion.div
          :initial="{ opacity: 0, y: 20 }"
          :animate="showFinal ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }"
          :transition="{ duration: 0.6, delay: 1.0 }"
          class="mt-14 grid grid-cols-3 gap-8 border-t border-border/50 pt-8"
        >
          <div class="flex flex-col items-center gap-1">
            <span class="text-2xl font-bold text-foreground md:text-3xl">99%</span>
            <span class="text-xs text-muted-foreground md:text-sm">Accuracy</span>
          </div>
          <div class="flex flex-col items-center gap-1">
            <span class="text-2xl font-bold text-foreground md:text-3xl">&lt;3s</span>
            <span class="text-xs text-muted-foreground md:text-sm">Conversion</span>
          </div>
          <div class="flex flex-col items-center gap-1">
            <span class="text-2xl font-bold text-foreground md:text-3xl">10k+</span>
            <span class="text-xs text-muted-foreground md:text-sm">Equations</span>
          </div>
        </motion.div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* ── Handwritten Phase ── */
.handwritten-stage {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 120px;
}

.handwritten-svg {
  width: clamp(320px, 60vw, 600px);
  height: 100px;
  overflow: visible;
}

.handwritten-text-svg {
  font-family: 'Caveat', 'Dancing Script', 'Segoe Script', 'Comic Sans MS', cursive;
  font-size: 64px;
  font-weight: 700;
  fill: none;
  stroke: hsl(var(--foreground));
  stroke-width: 1.5;
  stroke-dasharray: 800;
  stroke-dashoffset: 800;
  animation: stroke-write 1.4s cubic-bezier(0.4, 0, 0.2, 1) forwards,
             stroke-fill 0.4s ease-in 1.2s forwards;
}

@keyframes stroke-write {
  to {
    stroke-dashoffset: 0;
  }
}

@keyframes stroke-fill {
  to {
    fill: hsl(var(--foreground));
    stroke-width: 0;
  }
}

.select-overlay {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: hsl(var(--primary) / 0.35);
  border-radius: 4px;
  z-index: 1;
  pointer-events: none;
  transition: width 16ms linear;
}

/* ── Fall Stage ── */
.fall-stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  transform: rotate(-23deg);
  transform-origin: center center;
}

.fall-word {
  display: block;
  line-height: 0.86;
  font-family: 'NBAkademieProMono400', 'JetBrains Mono', ui-monospace, monospace;
  color: hsl(var(--foreground));
  will-change: transform, opacity, filter, text-shadow;
  transition: text-shadow 0.12s ease-out;
}

.mono-word {
  font-size: clamp(4.5rem, 17vw, 12rem);
  font-weight: 400;
}

.graph-word {
  margin-top: 0.3rem;
  font-size: clamp(6rem, 24vw, 16rem);
  font-weight: 500;
}

@media (max-width: 768px) {
  .fall-stage {
    transform: rotate(-14deg);
  }

  .handwritten-text-svg {
    font-size: 48px;
  }
}
</style>
