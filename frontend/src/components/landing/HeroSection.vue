<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { motion } from 'motion-v'

const heroRef = ref<HTMLElement | null>(null)
const started = ref(false)

// ── Animation phases ──
// Phase 1: Typewriter — types "monograph" in a monospace cursor style
// Phase 2: Select — highlights the text like a text selection
// Phase 3: Transform — text morphs into the big styled font + mouse glow activates

type Phase = 'idle' | 'typing' | 'selecting' | 'transforming' | 'glowing'
const phase = ref<Phase>('idle')

const fullText = 'monograph'
const typedCount = ref(0)
const displayedText = computed(() => fullText.slice(0, typedCount.value))
const selectWidth = ref(0) // 0–100 percentage
const showFinal = ref(false)

// ── Mouse glow tracking ──
const mouseX = ref(0.5)
const mouseY = ref(0.5)

const glowStyle = computed(() => {
  if (phase.value !== 'glowing') return {}

  const dx = (mouseX.value - 0.5) * 60
  const dy = (mouseY.value - 0.5) * 60

  return {
    textShadow: [
      `${dx * 0.3}px ${dy * 0.3}px 8px hsl(var(--primary) / 0.4)`,
      `${dx * 0.6}px ${dy * 0.6}px 20px hsl(var(--primary) / 0.25)`,
      `${dx}px ${dy}px 40px hsl(var(--primary) / 0.15)`,
      `${dx * 1.4}px ${dy * 1.4}px 70px hsl(var(--primary) / 0.08)`,
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

  // Phase 1: Typing
  phase.value = 'typing'
  typedCount.value = 0
  for (let i = 1; i <= fullText.length; i++) {
    typedCount.value = i
    await sleep(80 + Math.random() * 60) // natural typing speed
  }
  await sleep(400)

  // Phase 2: Selection sweep
  phase.value = 'selecting'
  const steps = 20
  for (let i = 1; i <= steps; i++) {
    selectWidth.value = (i / steps) * 100
    await sleep(18)
  }
  await sleep(500)

  // Phase 3: Transform into final styled text
  phase.value = 'transforming'
  await sleep(100)
  showFinal.value = true
  await sleep(1200) // let Motion spring animation play

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
    { threshold: 0.4 },
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

        <!-- ── Typewriter + Select Phase ── -->
        <div
          v-if="!showFinal"
          class="typewriter-stage"
        >
          <span class="typewriter-text">{{ displayedText }}</span>
          <span
            class="typewriter-cursor"
            :class="{ 'cursor-blink': phase === 'typing' || phase === 'idle' }"
          >|</span>

          <!-- Selection overlay -->
          <div
            v-if="phase === 'selecting'"
            class="select-overlay"
            :style="{ width: selectWidth + '%' }"
          />
        </div>

        <!-- ── Final Transformed Text (with glow) ── -->
        <div v-if="showFinal" class="fall-stage">
          <motion.span
            :initial="{ opacity: 0, y: -80, scale: 0.85, filter: 'blur(8px)' }"
            :animate="{ opacity: 1, y: 0, scale: 1, filter: 'blur(0px)' }"
            :transition="{ type: 'spring', visualDuration: 0.6, bounce: 0.2 }"
            class="fall-word mono-word"
            :style="glowStyle"
          >
            mono
          </motion.span>
          <motion.span
            :initial="{ opacity: 0, y: -80, scale: 0.85, filter: 'blur(8px)' }"
            :animate="{ opacity: 1, y: 0, scale: 1, filter: 'blur(0px)' }"
            :transition="{ type: 'spring', visualDuration: 0.7, bounce: 0.25, delay: 0.15 }"
            class="fall-word graph-word"
            :style="glowStyle"
          >
            graph
          </motion.span>
        </div>

        <motion.p
          :initial="{ opacity: 0, y: 20 }"
          :animate="showFinal ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }"
          :transition="{ duration: 0.6, delay: 0.4 }"
          class="mt-10 max-w-2xl text-center text-lg text-muted-foreground md:text-xl"
        >
          Upload your notes and shape the page around this motion-led identity. Keep iterating on layout while this
          title animation anchors the hero.
        </motion.p>

        <motion.div
          :initial="{ opacity: 0, y: 20 }"
          :animate="showFinal ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }"
          :transition="{ duration: 0.6, delay: 0.6 }"
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
          :transition="{ duration: 0.6, delay: 0.8 }"
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
/* ── Typewriter Phase ── */
.typewriter-stage {
  position: relative;
  display: inline-block;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: clamp(2rem, 6vw, 4rem);
  font-weight: 400;
  color: hsl(var(--foreground));
  line-height: 1.2;
}

.typewriter-text {
  position: relative;
  z-index: 2;
}

.typewriter-cursor {
  color: hsl(var(--primary));
  font-weight: 300;
  margin-left: 2px;
}

.cursor-blink {
  animation: blink 800ms steps(1) infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.select-overlay {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: hsl(var(--primary) / 0.3);
  border-radius: 3px;
  z-index: 1;
  pointer-events: none;
  transition: width 18ms linear;
}

/* ── Final Styled Text ── */
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
  color: hsl(var(--foreground));
  will-change: transform, opacity, filter, text-shadow;
  transition: text-shadow 0.15s ease-out;
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
}
</style>
