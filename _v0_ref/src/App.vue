<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import SlamText from './components/SlamText.vue'
import FadeIn from './components/FadeIn.vue'
import LineReveal from './components/LineReveal.vue'
import ScrollMarquee from './components/ScrollMarquee.vue'
import ParallaxSection from './components/ParallaxSection.vue'
import StatsCounter from './components/StatsCounter.vue'
import BentoCard from './components/BentoCard.vue'
import TimelineStep from './components/TimelineStep.vue'

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
  <main style="background-color: #0a0a0a; min-height: 100vh; position: relative;">

    <!-- ============================================ -->
    <!-- SECTION 1: Opening Hero                      -->
    <!-- ============================================ -->
    <section style="min-height: 100vh; display: flex; align-items: center; overflow: hidden; position: relative;">
      <!-- Floating decorative line -->
      <div
        style="position: absolute; top: 0; right: 15%; width: 1px; height: 60vh; background: rgba(138,133,128,0.1);"
        :style="{ transform: 'translateY(' + scrollY * 0.15 + 'px)' }"
      />

      <div style="width: 100%; padding: 80px 24px;">
        <div style="margin-bottom: 32px;">
          <SlamText
            text="mono"
            :angle="-6"
            :delay="200"
            size="text-[18vw] md:text-[16vw]"
            weight="font-black"
          />
        </div>
        <div style="margin-left: 10vw;">
          <SlamText
            text="graph"
            :angle="-6"
            :delay="500"
            size="text-[18vw] md:text-[16vw]"
            weight="font-black"
            :italic="true"
          />
        </div>

        <!-- Subtitle -->
        <div style="margin-top: 80px; margin-left: 2vw;">
          <FadeIn :delay="900">
            <p style="color: #8a8580; font-size: 14px; font-family: 'Inter', sans-serif; letter-spacing: 0.2em; text-transform: uppercase;">
              Design with intention
            </p>
          </FadeIn>
          <FadeIn :delay="1100">
            <p style="color: rgba(138,133,128,0.6); font-size: 14px; font-family: 'Inter', sans-serif; margin-top: 12px; max-width: 420px; line-height: 1.6; letter-spacing: 0.03em;">
              A creative studio where architecture meets digital experience.
              Every detail is considered, every moment crafted.
            </p>
          </FadeIn>
        </div>
      </div>

      <!-- Scroll indicator -->
      <div style="position: absolute; bottom: 40px; left: 50%; transform: translateX(-50%); display: flex; flex-direction: column; align-items: center; gap: 12px;">
        <FadeIn :delay="1500">
          <span style="color: rgba(138,133,128,0.4); font-size: 11px; letter-spacing: 0.3em; text-transform: uppercase; font-family: 'Inter', sans-serif;">Scroll</span>
        </FadeIn>
        <FadeIn :delay="1700">
          <div class="scroll-line" style="width: 1px; height: 48px; background: rgba(138,133,128,0.2);" />
        </FadeIn>
      </div>
    </section>

    <!-- ============================================ -->
    <!-- SECTION 1.5: Stats Bar (NEW)                 -->
    <!-- ============================================ -->
    <section style="overflow: hidden; position: relative;">
      <LineReveal :delay="0" />
      <div style="padding: 80px 48px;">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-12 md:gap-0 max-w-5xl mx-auto">
          <div class="text-center md:border-r" style="border-color: rgba(138,133,128,0.1);">
            <StatsCounter :value="99" suffix="%" label="Accuracy" :delay="0" />
          </div>
          <div class="text-center md:border-r" style="border-color: rgba(138,133,128,0.1);">
            <StatsCounter :value="3" prefix="<" suffix="s" label="Conversion Time" :delay="200" />
          </div>
          <div class="text-center">
            <StatsCounter :value="10" suffix="k+" label="Equations Processed" :delay="400" />
          </div>
        </div>
      </div>
      <LineReveal :delay="200" />
    </section>

    <!-- ============================================ -->
    <!-- SECTION 2: Slam with divider (EXISTING)      -->
    <!-- ============================================ -->
    <section style="min-height: 100vh; display: flex; align-items: center; overflow: hidden; position: relative;">
      <LineReveal :delay="0" style="position: absolute; top: 0; left: 0; right: 0;" />

      <div style="width: 100%; display: grid; grid-template-columns: 1fr 1fr; min-height: 100vh;">
        <!-- Left side -->
        <div style="display: flex; flex-direction: column; justify-content: center; padding: 80px 48px;">
          <SlamText
            text="mono"
            :angle="-4"
            :delay="0"
            size="text-[14vw] md:text-[7vw]"
            weight="font-black"
          />
          <SlamText
            text="graph"
            :angle="-4"
            :delay="200"
            size="text-[14vw] md:text-[7vw]"
            weight="font-black"
            :italic="true"
          />
          <div style="margin-top: 48px;">
            <FadeIn :delay="500">
              <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
                <div style="width: 48px; height: 1px; background: #d4a574;" />
                <span style="color: #d4a574; font-size: 11px; letter-spacing: 0.3em; text-transform: uppercase; font-family: 'Inter', sans-serif;">Studio</span>
              </div>
            </FadeIn>
            <FadeIn :delay="700">
              <p style="color: #8a8580; font-size: 14px; line-height: 1.7; max-width: 380px; font-family: 'Inter', sans-serif;">
                We craft spaces between the tangible and the digital,
                where form follows feeling and every pixel has purpose.
              </p>
            </FadeIn>
          </div>
        </div>

        <!-- Right side -->
        <div style="display: flex; flex-direction: column; justify-content: center; padding: 80px 48px; border-left: 1px solid rgba(138,133,128,0.1);">
          <FadeIn :delay="300">
            <span style="color: rgba(138,133,128,0.15); font-size: 160px; font-family: 'Playfair Display', serif; font-weight: 300; line-height: 1;">
              02
            </span>
          </FadeIn>
          <FadeIn :delay="500">
            <h3 style="color: #f5f0eb; font-size: 28px; font-family: 'Playfair Display', serif; font-style: italic; margin-top: 24px; line-height: 1.3;">
              Where architecture
              <br />
              <span style="color: #d4a574;">meets motion</span>
            </h3>
          </FadeIn>
          <FadeIn :delay="700">
            <p style="color: #8a8580; font-size: 14px; line-height: 1.7; margin-top: 24px; max-width: 380px; font-family: 'Inter', sans-serif;">
              Every project begins with a question. We answer it through
              meticulous design, considered motion, and relentless craft.
            </p>
          </FadeIn>
        </div>
      </div>
    </section>

    <!-- ============================================ -->
    <!-- SECTION 2.5: Features Bento Grid (NEW)       -->
    <!-- ============================================ -->
    <section style="overflow: hidden; position: relative;">
      <LineReveal :delay="0" />

      <div style="padding: 120px 48px;">
        <!-- Section header -->
        <div style="margin-bottom: 80px;">
          <FadeIn :delay="0">
            <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
              <div style="width: 48px; height: 1px; background: #d4a574;" />
              <span style="color: #d4a574; font-size: 11px; letter-spacing: 0.3em; text-transform: uppercase; font-family: 'Inter', sans-serif;">Capabilities</span>
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
            title="Drag & Drop Upload"
            description="Simply drop your handwritten notes. We accept PDF, HTML, and LaTeX formats up to 10MB."
            icon="&#x2191;"
            :delay="0"
            span="md:col-span-2"
          />
          <BentoCard
            title="Gemini OCR Engine"
            description="Neural networks trained on millions of equations recognize your handwriting with remarkable precision."
            icon="&#x26A1;"
            :delay="100"
          />
          <BentoCard
            title="Clean LaTeX Output"
            description="Production-ready LaTeX code, properly formatted and immediately compilable."
            icon="&#123;&#125;"
            :delay="200"
          />
          <BentoCard
            title="Live Preview"
            description="Watch your LaTeX render in real-time as the AI processes each symbol and structure."
            icon="&#x25CE;"
            :delay="300"
            span="md:col-span-2"
          />
          <BentoCard
            title="Export Options"
            description="Download as LaTeX, HTML, or PDF. Share or integrate into your existing workflow."
            icon="&#x2193;"
            :delay="400"
            span="md:col-span-2"
          />
          <BentoCard
            title="Edit & Refine"
            description="Full-featured editor with syntax highlighting, auto-completion, and instant recompilation."
            icon="&#x270E;"
            :delay="500"
          />
        </div>
      </div>
    </section>

    <!-- ============================================ -->
    <!-- SECTION 3: Marquee (EXISTING)                -->
    <!-- ============================================ -->
    <section style="overflow: hidden; padding: 32px 0; position: relative;">
      <LineReveal :delay="0" />
      <ScrollMarquee :scrollY="scrollY" />
      <LineReveal :delay="200" style="margin-top: 32px;" />
    </section>

    <!-- ============================================ -->
    <!-- SECTION 3.5: How It Works Timeline (NEW)     -->
    <!-- ============================================ -->
    <section style="overflow: hidden; position: relative;">
      <div style="padding: 120px 48px;">
        <!-- Section header -->
        <div style="margin-bottom: 80px;">
          <FadeIn :delay="0">
            <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
              <div style="width: 48px; height: 1px; background: #d4a574;" />
              <span style="color: #d4a574; font-size: 11px; letter-spacing: 0.3em; text-transform: uppercase; font-family: 'Inter', sans-serif;">Process</span>
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
            :step="1"
            title="Upload Your Notes"
            description="Drag and drop your notes, equations, or diagrams. We support PDF, HTML, and LaTeX files."
            icon="&#x2191;"
            :delay="0"
          />
          <TimelineStep
            :step="2"
            title="AI Processes It"
            description="Our neural network reads your handwriting, recognizes mathematical structures, and converts everything into clean, semantic LaTeX code."
            icon="&#x26A1;"
            :delay="200"
          />
          <TimelineStep
            :step="3"
            title="Edit & Export"
            description="Review the output in our live editor, make refinements with syntax highlighting and auto-complete, then export as LaTeX, HTML, or PDF."
            icon="&#x2193;"
            :delay="400"
            :isLast="true"
          />
        </div>
      </div>
    </section>

    <!-- ============================================ -->
    <!-- SECTION 4: Two monographs side by side (EXISTING) -->
    <!-- ============================================ -->
    <section style="min-height: 100vh; display: flex; align-items: center; overflow: hidden; position: relative;">
      <LineReveal :delay="0" style="position: absolute; top: 0; left: 0; right: 0;" />

      <div style="width: 100%; padding: 80px 48px;">
        <div style="display: grid; grid-template-columns: 1fr 1fr;">
          <!-- Left monograph -->
          <div>
            <SlamText text="mono" :angle="-8" :delay="0" size="text-[16vw] md:text-[8vw]" weight="font-black" />
            <SlamText text="graph" :angle="-8" :delay="200" size="text-[16vw] md:text-[8vw]" weight="font-black" :italic="true" />
          </div>

          <!-- Right monograph -->
          <div style="text-align: right;">
            <SlamText text="mono" :angle="5" :delay="300" size="text-[16vw] md:text-[8vw]" weight="font-black" align="right" />
            <SlamText text="graph" :angle="5" :delay="500" size="text-[16vw] md:text-[8vw]" weight="font-black" :italic="true" align="right" />
          </div>
        </div>

        <!-- Animated subtext -->
        <div style="margin-top: 80px; display: flex; justify-content: space-between; align-items: flex-end; gap: 48px;">
          <div style="max-width: 420px;">
            <FadeIn :delay="600">
              <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
                <div style="width: 64px; height: 1px; background: #d4a574;" />
                <span style="color: #d4a574; font-size: 11px; letter-spacing: 0.3em; text-transform: uppercase; font-family: 'Inter', sans-serif;">Philosophy</span>
              </div>
            </FadeIn>
            <FadeIn :delay="800">
              <h3 style="color: #f5f0eb; font-size: 24px; font-family: 'Playfair Display', serif; font-style: italic; line-height: 1.4;">
                Two perspectives,
                <span style="color: #e8c9a0;">one vision.</span>
                Duality in design creates tension that captivates.
              </h3>
            </FadeIn>
          </div>

          <div style="max-width: 300px;">
            <FadeIn :delay="1000">
              <p style="color: #8a8580; font-size: 14px; line-height: 1.7; font-family: 'Inter', sans-serif;">
                The interplay of opposing forces - light and dark,
                structure and fluidity - defines our creative DNA.
              </p>
            </FadeIn>
          </div>
        </div>
      </div>
    </section>

    <!-- ============================================ -->
    <!-- SECTION 5: Full bleed monograph (EXISTING)   -->
    <!-- ============================================ -->
    <section style="overflow: hidden; position: relative;">
      <LineReveal :delay="0" />

      <div style="min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80px 24px;">
        <FadeIn :delay="0">
          <span style="color: rgba(138,133,128,0.2); font-size: 11px; letter-spacing: 0.5em; text-transform: uppercase; font-family: 'Inter', sans-serif; margin-bottom: 48px; display: block;">
            Chapter III
          </span>
        </FadeIn>

        <div style="position: relative;">
          <SlamText
            text="monograph"
            :angle="-3"
            :delay="200"
            size="text-[14vw] md:text-[10vw]"
            weight="font-black"
            align="center"
          />

          <!-- Accent line slicing through -->
          <div style="position: absolute; top: 50%; left: -5%; width: 110%; height: 1px;">
            <LineReveal :delay="800" />
          </div>
        </div>

        <div style="margin-top: 80px; text-align: center; max-width: 640px;">
          <FadeIn :delay="600">
            <p style="color: #8a8580; font-size: 16px; line-height: 1.7; font-family: 'Inter', sans-serif;">
              In the space between the concrete and the abstract,
              we find the extraordinary. Monograph is the pursuit
              of perfection in every frame, every transition,
              every breath of white space.
            </p>
          </FadeIn>

          <FadeIn :delay="900">
            <div style="margin-top: 48px; display: flex; align-items: center; justify-content: center; gap: 32px;">
              <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background: #d4a574;" />
                <span style="color: #8a8580; font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase; font-family: 'Inter', sans-serif;">Design</span>
              </div>
              <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background: #e8c9a0;" />
                <span style="color: #8a8580; font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase; font-family: 'Inter', sans-serif;">Motion</span>
              </div>
              <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background: #8a8580;" />
                <span style="color: #8a8580; font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase; font-family: 'Inter', sans-serif;">Craft</span>
              </div>
            </div>
          </FadeIn>
        </div>
      </div>
    </section>

    <!-- ============================================ -->
    <!-- SECTION 5.5: CTA / Conversion Invite (NEW)   -->
    <!-- ============================================ -->
    <section style="overflow: hidden; position: relative;">
      <LineReveal :delay="0" />

      <div style="min-height: 80vh; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 120px 24px; text-align: center;">
        <FadeIn :delay="0">
          <span style="color: rgba(138,133,128,0.2); font-size: 11px; letter-spacing: 0.5em; text-transform: uppercase; font-family: 'Inter', sans-serif; margin-bottom: 48px; display: block;">
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

        <div style="margin-top: 64px; max-width: 520px;">
          <FadeIn :delay="600">
            <p style="color: #8a8580; font-size: 16px; line-height: 1.7; font-family: 'Inter', sans-serif; margin-bottom: 48px;">
              Drop your handwritten notes and watch them transform into
              clean, publication-ready LaTeX in seconds. No setup required.
            </p>
          </FadeIn>

          <FadeIn :delay="800">
            <div style="display: flex; align-items: center; justify-content: center; gap: 20px; flex-wrap: wrap;">
              <!-- Primary CTA -->
              <a
                href="/convert"
                class="cta-primary"
                style="display: inline-flex; align-items: center; gap: 10px; padding: 16px 40px; background: #d4a574; color: #0a0a0a; font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; text-decoration: none; border-radius: 2px; transition: all 0.4s cubic-bezier(0.22, 1, 0.36, 1);"
              >
                <span>Start Converting</span>
                <span style="font-size: 16px;">&#x2192;</span>
              </a>

              <!-- Secondary CTA -->
              <a
                href="#features"
                class="cta-secondary"
                style="display: inline-flex; align-items: center; gap: 10px; padding: 16px 40px; background: transparent; color: #8a8580; font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 500; letter-spacing: 0.1em; text-transform: uppercase; text-decoration: none; border: 1px solid rgba(138,133,128,0.2); border-radius: 2px; transition: all 0.4s cubic-bezier(0.22, 1, 0.36, 1);"
              >
                <span>See How It Works</span>
              </a>
            </div>
          </FadeIn>
        </div>

        <!-- Decorative file type badges -->
        <FadeIn :delay="1100">
          <div style="margin-top: 64px; display: flex; align-items: center; gap: 12px;">
            <span
              v-for="format in ['PDF', 'HTML', 'LaTeX']"
              :key="format"
              style="padding: 6px 16px; border: 1px solid rgba(138,133,128,0.1); border-radius: 100px; color: rgba(138,133,128,0.4); font-size: 11px; letter-spacing: 0.15em; font-family: 'Inter', sans-serif;"
            >
              {{ format }}
            </span>
          </div>
        </FadeIn>
      </div>
    </section>

    <!-- ============================================ -->
    <!-- SECTION 6: Staggered letter cascade (EXISTING) -->
    <!-- ============================================ -->
    <section style="overflow: hidden; position: relative;">
      <LineReveal :delay="0" />

      <div style="min-height: 100vh; display: flex; flex-direction: column; justify-content: center; padding: 80px 48px;">
        <div>
          <SlamText text="M" :angle="-12" :delay="0" size="text-[22vw] md:text-[14vw]" weight="font-black" />
          <SlamText text="O" :angle="-10" :delay="100" size="text-[22vw] md:text-[14vw]" weight="font-black" :italic="true" />
          <SlamText text="N" :angle="-8" :delay="200" size="text-[22vw] md:text-[14vw]" weight="font-black" />
          <SlamText text="O" :angle="-6" :delay="300" size="text-[22vw] md:text-[14vw]" weight="font-black" :italic="true" />
        </div>

        <div style="margin-top: 64px;">
          <FadeIn :delay="600">
            <div style="display: flex; align-items: flex-start; gap: 32px;">
              <div style="width: 96px; height: 1px; background: #d4a574; margin-top: 12px; flex-shrink: 0;" />
              <div style="max-width: 480px;">
                <h3 style="color: #f5f0eb; font-size: 20px; font-family: 'Playfair Display', serif; font-style: italic; line-height: 1.4; margin-bottom: 16px;">
                  Letter by letter, frame by frame
                </h3>
                <p style="color: #8a8580; font-size: 14px; line-height: 1.7; font-family: 'Inter', sans-serif;">
                  Deconstruction reveals the beauty in individual forms.
                  Each character carries weight, rhythm, and intention -
                  a monograph of typographic expression.
                </p>
              </div>
            </div>
          </FadeIn>
        </div>
      </div>
    </section>

    <!-- ============================================ -->
    <!-- SECTION 6.5: Testimonial / Social Proof (NEW) -->
    <!-- ============================================ -->
    <section style="overflow: hidden; position: relative;">
      <LineReveal :delay="0" />

      <div style="padding: 120px 48px;">
        <div class="max-w-4xl mx-auto text-center">
          <FadeIn :delay="0">
            <span style="color: rgba(212,165,116,0.3); font-size: 80px; font-family: 'Playfair Display', serif; line-height: 1;">
              &#x201C;
            </span>
          </FadeIn>

          <FadeIn :delay="200">
            <blockquote
              class="font-display text-2xl md:text-4xl font-normal italic leading-snug"
              style="color: #f5f0eb; margin-top: -20px;"
            >
              It understood my terrible handwriting
              better than I do. Three semesters of notes
              <span style="color: #d4a574;">converted in an afternoon.</span>
            </blockquote>
          </FadeIn>

          <FadeIn :delay="500">
            <div style="margin-top: 48px; display: flex; flex-direction: column; align-items: center; gap: 8px;">
              <div style="width: 40px; height: 1px; background: rgba(212,165,116,0.3); margin-bottom: 8px;" />
              <span style="color: #8a8580; font-size: 13px; font-family: 'Inter', sans-serif; font-weight: 500;">
                Dr. Elise Hartmann
              </span>
              <span style="color: rgba(138,133,128,0.5); font-size: 12px; font-family: 'Inter', sans-serif;">
                Theoretical Physics, ETH Zurich
              </span>
            </div>
          </FadeIn>
        </div>
      </div>

      <LineReveal :delay="400" />
    </section>

    <!-- ============================================ -->
    <!-- SECTION 7: Final statement (EXISTING)        -->
    <!-- ============================================ -->
    <section style="overflow: hidden; position: relative;">
      <LineReveal :delay="0" />

      <div style="min-height: 80vh; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80px 24px;">
        <ParallaxSection :scrollY="scrollY">
          <SlamText
            text="monograph"
            :angle="0"
            :delay="200"
            size="text-[12vw] md:text-[8vw]"
            weight="font-black"
            align="center"
          />
        </ParallaxSection>

        <FadeIn :delay="600">
          <p style="color: rgba(138,133,128,0.4); font-size: 11px; letter-spacing: 0.4em; text-transform: uppercase; font-family: 'Inter', sans-serif; margin-top: 64px;">
            Crafted with obsession
          </p>
        </FadeIn>
      </div>

      <LineReveal :delay="400" />
    </section>

  </main>
</template>

<style>
@keyframes scrollLine {
  0% { transform: scaleY(0); transform-origin: top; }
  50% { transform: scaleY(1); transform-origin: top; }
  50.01% { transform-origin: bottom; }
  100% { transform: scaleY(0); transform-origin: bottom; }
}

.scroll-line {
  animation: scrollLine 2s ease-in-out infinite;
}

.cta-primary:hover {
  background: #e8c9a0 !important;
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(212, 165, 116, 0.2);
}

.cta-secondary:hover {
  color: #f5f0eb !important;
  border-color: rgba(245, 240, 235, 0.3) !important;
}
</style>
