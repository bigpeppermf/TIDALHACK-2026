# 🎨 → 💻 ScribeTeX Figma-to-Code Workflow

> **Teammate 1 (Frontend) — how to turn Figma designs into Vue components fast**
> Philosophy: **Speed > Perfection**. Ship the demo, not production code.
> Last updated: Feb 7, 2026 (via Context7 MCP)

---

## Overview: Your 24-Hour Timeline

| Block | Hours | Focus | Output |
|---|---|---|---|
| 🎯 Design | 0–3 | Figma wireframes (3 screens max) | Screens + design tokens |
| 🏗️ Scaffold | 3–4 | Vue + Tailwind + Motion setup | Dev server running |
| ⚡ Build | 4–10 | Core components + API wiring | Full flow working |
| ✨ Polish | 10–18 | Figma → Vue pixel match + animations | Demo-ready UI |
| 🎤 Demo | 18–24 | Bug fixes + practice runs | Rehearsed pitch |

---

## Phase 1 — Design in Figma (Hours 0–3)

### What to Design

Only the **3 screens you'll demo**:

1. **Landing / Home** — hero section, CTA "Try it" button
2. **Upload + Loading** — drop zone, file picker, spinner with status text
3. **Result** — split view (original image left, LaTeX right), copy/download buttons

### What NOT to Design

- ❌ Settings pages, user profiles, login screens
- ❌ Every error state (handle in code with simple text)
- ❌ Complex responsive layouts (demo is on a laptop)
- ❌ Hover states or micro-interactions (add with Motion in code)

### Extract Design Tokens (15 min)

Use Figma's **Inspect** panel to grab values. Paste them into your Tailwind CSS config:

```css
/* src/frontend/src/style.css — Tailwind v4 theme */
@import "tailwindcss";

@theme {
  --color-primary: #3B82F6;
  --color-primary-hover: #2563EB;
  --color-secondary: #8B5CF6;
  --color-surface: #1E1E2E;
  --color-surface-light: #2A2A3E;
  --color-text: #E2E8F0;
  --color-text-muted: #94A3B8;
  --color-success: #22C55E;
  --color-error: #EF4444;

  --font-display: "Inter", sans-serif;
  --font-mono: "JetBrains Mono", monospace;

  --radius-lg: 1rem;
  --radius-xl: 1.5rem;
}
```

> **Tailwind v4**: No `tailwind.config.js` needed. Use `@theme` in your CSS file directly with the `@tailwindcss/vite` plugin.

### Export from Figma

- **Icons** → SVG (copy as SVG, paste directly into Vue templates)
- **Logo** → SVG or PNG
- **Hero image** → webp (smaller file size)

Put assets in `src/frontend/public/` or `src/frontend/src/assets/`.

---

## Phase 2 — Scaffold the Project (Hour 3–4)

This is already in your checklist. Quick refresher:

```bash
cd src/frontend
npm create vue@latest .
# TypeScript ✅, Vue Router ✅, Pinia ❌, ESLint ❌

npm install motion-v katex
npm install -D @tailwindcss/vite

# shadcn-vue: pre-built accessible components you own
npx shadcn-vue@latest init
npx shadcn-vue@latest add button card input textarea sonner
```

### Vite Config (Tailwind v4 Plugin)

```typescript
// src/frontend/vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
  ],
})
```

### Import Tailwind in Your CSS

```css
/* src/frontend/src/style.css */
@import "tailwindcss";

@theme {
  /* paste your Figma tokens here */
}
```

```bash
npm run dev  # → http://localhost:5173
```

**✅ Checkpoint:** Dev server running, Tailwind classes work, router has `/` and `/convert`.

---

## Phase 3 — Convert Figma to Vue Components (Hours 4–10)

### The Hybrid Approach (Recommended)

Combine **4 techniques** depending on the component:

| Technique | Use For | Speed |
|---|---|---|
| **shadcn-vue Components** | Buttons, cards, inputs, toasts, dialogs | 🏆 Pre-styled + accessible |
| **AI Generation** | Landing page hero, navbars, unique layouts | ⚡ Fastest for custom UI |
| **Hand-build + Tailwind** | Upload zone, result split view | 🔨 Most control |
| **Component Skeleton + Style** | Take existing skeletons from `FRONTEND-REFERENCE.md`, style to match Figma | 🎯 Best for ScribeTeX |

---

### Technique A: AI-Powered Generation

**When:** Landing page, hero section, generic UI

1. Screenshot your Figma screen
2. Prompt an AI (Claude, v0.dev, or Copilot):
   ```
   Create a Vue 3 component using <script setup> and Tailwind CSS v4
   that matches this screenshot. Use semantic HTML.
   Do NOT use any component library — just Tailwind utilities.
   ```
3. Paste the output into your `.vue` file
4. Replace hardcoded colors with your `@theme` tokens: `bg-primary`, `text-text-muted`, etc.
5. Swap placeholder text with real ScribeTeX copy

**AI-friendly components for ScribeTeX:**
- Hero section with headline + CTA
- Navbar with logo and links
- Footer (if time)

---

### Technique B: shadcn-vue Drop-In Components

**When:** Buttons, form inputs, cards, toasts, dialogs — anything that's a standard UI pattern

shadcn-vue gives you polished, accessible components that are **copied into your project** (not a node_modules dependency). Edit them freely.

#### Which shadcn Components to Use for ScribeTeX

| ScribeTeX Feature | shadcn Component | Why |
|---|---|---|
| "Convert" / "Copy" / "Download" buttons | `Button` | 6 variants, consistent styling |
| Result panel wrapper | `Card` + `CardHeader` + `CardContent` + `CardFooter` | Structured layout with title/description |
| LaTeX editor | `Textarea` | Styled, accessible, works with `v-model` |
| Filename input (export) | `Input` | Consistent with the rest of the UI |
| "Copied!" feedback | `Sonner` toast | No need to build custom toast |
| Context selector (nice-to-have) | `DropdownMenu` | `npx shadcn-vue@latest add dropdown-menu` |
| Export options (nice-to-have) | `Dialog` | `npx shadcn-vue@latest add dialog` |

#### Usage Pattern

```vue
<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { toast } from 'vue-sonner'

function onCopy() {
  navigator.clipboard.writeText(latex.value)
  toast('Copied to clipboard!')
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>LaTeX Output</CardTitle>
    </CardHeader>
    <CardContent>
      <Textarea v-model="latex" class="font-mono min-h-[300px]" />
    </CardContent>
    <CardFooter class="gap-2">
      <Button @click="onCopy">📋 Copy</Button>
      <Button variant="outline" @click="download">
        💾 Download .tex
      </Button>
    </CardFooter>
  </Card>
</template>
```

#### Combining shadcn + Motion

Wrap Motion around shadcn components for animations:

```vue
<motion.div :whileHover="{ scale: 1.02 }" :whilePress="{ scale: 0.98 }">
  <Button size="lg">Convert to LaTeX</Button>
</motion.div>
```

> **Rule:** shadcn handles structure + styling, Motion handles animation. Don't fight the shadcn styles — enhance them with motion.

---

### Technique C: Hand-Build with Tailwind

**When:** Core interactive components — upload zone, editor, preview

This is where you'll spend most of your time. Work from the skeletons in [FRONTEND-REFERENCE.md](FRONTEND-REFERENCE.md).

#### Figma → Tailwind Translation Cheat Sheet

| Figma Value | Tailwind Class |
|---|---|
| Padding 4px | `p-1` |
| Padding 8px | `p-2` |
| Padding 12px | `p-3` |
| Padding 16px | `p-4` |
| Padding 24px | `p-6` |
| Padding 32px | `p-8` |
| Padding 48px | `p-12` |
| Gap 8px | `gap-2` |
| Gap 16px | `gap-4` |
| Border radius 8px | `rounded-lg` |
| Border radius 12px | `rounded-xl` |
| Border radius 16px | `rounded-2xl` |
| Font 14px | `text-sm` |
| Font 16px | `text-base` |
| Font 18px | `text-lg` |
| Font 24px | `text-2xl` |
| Font 32px | `text-3xl` |
| Font 48px | `text-5xl` |
| Font weight 500 | `font-medium` |
| Font weight 600 | `font-semibold` |
| Font weight 700 | `font-bold` |
| Opacity 50% | `opacity-50` |
| Shadow | `shadow-md` or `shadow-lg` |
| Flex column | `flex flex-col` |
| Flex row, centered | `flex items-center justify-center` |
| Grid 2 cols | `grid grid-cols-2` |

#### Step-by-Step for Each Component

1. **Open Figma** → select the component layer
2. **Copy layout structure** → write the HTML skeleton in your `.vue` template
3. **Add Tailwind classes** → reference Figma Inspect panel for spacing, colors, font
4. **Add interactivity** → Vue `ref()`, `@click`, `v-model`, `v-if`
5. **Add Motion animations** → only after the component works and looks right

---

### Technique D: Use Your Existing Skeletons

The [FRONTEND-REFERENCE.md](FRONTEND-REFERENCE.md) already has skeletons for every core component. Here's how to use them:

1. Copy the skeleton from the reference doc
2. Style it to match your Figma design using Tailwind classes
3. Wire up the composables (`useConvert`, `useExport`)
4. Add Motion animations last

**Component → Reference mapping:**

| Component | Skeleton in Reference | Composable |
|---|---|---|
| `UploadZone.vue` | UploadZone skeleton | `useConvert` |
| `LoadingAnimation.vue` | LoadingAnimation skeleton | — |
| `ResultView.vue` | ResultView skeleton | `useExport` |
| `LatexPreview.vue` | Full implementation | — |
| `LatexEditor.vue` | Build from scratch (it's a `<textarea>`) | — |

---

## Phase 4 — Add Motion Animations (Hours 10–14)

### Rule: Animations Go LAST

Build → Style → Animate. Never the reverse.

### The ScribeTeX Animation Sequence

This is the narrative your demo tells through motion:

```
User lands on page
  └─ Hero fades in (opacity 0→1, y 20→0)
      └─ CTA button pulses subtly

User clicks "Try it" → /convert
  └─ Page cross-fades (route transition)
      └─ Upload zone fades up

User drops an image
  └─ Thumbnail scales in (scale 0→1)
      └─ "Convert" button appears (fade in)

User clicks "Convert"
  └─ Upload zone exits (opacity→0, y→-20)
      └─ Loading spinner appears
          └─ Pencil rotates (360°, infinite)
          └─ Status text cycles: "Reading..." → "Converting..." → "Done!"

Results arrive
  └─ Loading exits
      └─ Left panel slides in (x: -50→0)
      └─ Right panel slides in (x: 50→0, delay 0.1s)
          └─ LaTeX renders with KaTeX

User interacts with result
  └─ Copy button: whilePress scale 0.95 → toast slides down
  └─ Download button: whilePress scale 0.95
```

### Implementation — Staggered Children

Use Motion's `variants` + `stagger` for the result view:

```vue
<script setup>
import { motion } from 'motion-v'
import { stagger } from 'motion-v'

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      delayChildren: stagger(0.15)
    }
  }
}

const slideFromLeft = {
  hidden: { x: -50, opacity: 0 },
  show: { x: 0, opacity: 1 }
}

const slideFromRight = {
  hidden: { x: 50, opacity: 0 },
  show: { x: 0, opacity: 1 }
}
</script>

<template>
  <motion.div
    :variants="container"
    initial="hidden"
    animate="show"
    class="grid grid-cols-2 gap-6"
  >
    <motion.div :variants="slideFromLeft" class="...">
      <img :src="imageUrl" class="rounded-xl shadow-lg" />
    </motion.div>
    <motion.div :variants="slideFromRight" class="...">
      <LatexEditor v-model="latex" />
      <LatexPreview :latex="latex" />
    </motion.div>
  </motion.div>
</template>
```

### Spring Physics for "Wow" Moments

Use springs instead of easing for organic feel:

```vue
<!-- Bouncy card entrance -->
<motion.div
  :initial="{ scale: 0, opacity: 0 }"
  :animate="{ scale: 1, opacity: 1 }"
  :transition="{
    type: 'spring',
    visualDuration: 0.5,
    bounce: 0.3
  }"
>
  Result card
</motion.div>
```

```vue
<!-- Snappy button press -->
<motion.button
  :whileHover="{ scale: 1.05 }"
  :whilePress="{ scale: 0.92 }"
  :transition="{
    type: 'spring',
    stiffness: 400,
    damping: 17
  }"
>
  Copy LaTeX
</motion.button>
```

### Toast Notification (Copied!)

```vue
<script setup>
import { ref } from 'vue'
import { motion, AnimatePresence } from 'motion-v'

const showToast = ref(false)

function flashToast() {
  showToast.value = true
  setTimeout(() => (showToast.value = false), 2000)
}
</script>

<template>
  <AnimatePresence>
    <motion.div
      v-if="showToast"
      :initial="{ y: -50, opacity: 0 }"
      :animate="{ y: 0, opacity: 1 }"
      :exit="{ y: -50, opacity: 0 }"
      :transition="{ type: 'spring', damping: 20, stiffness: 300 }"
      class="fixed top-4 right-4 bg-success text-white px-4 py-2 rounded-lg shadow-lg"
    >
      ✅ Copied to clipboard!
    </motion.div>
  </AnimatePresence>
</template>
```

---

## Phase 5 — Polish Pass (Hours 14–18)

### The 30-Minute Polish Checklist

Run through this once your flow works end-to-end:

- [ ] **Colors match Figma** — compare side-by-side, tweak `@theme` values
- [ ] **Typography is consistent** — same font sizes, weights across all screens
- [ ] **Spacing is even** — check padding/margins, use Tailwind's spacing scale
- [ ] **No layout jumps** — content doesn't shift when loading/results appear
- [ ] **Loading state feels smooth** — no blank white screen between states
- [ ] **Buttons have hover/press feedback** — Motion `whileHover` / `whilePress`
- [ ] **Error messages are friendly** — no raw error strings from the API
- [ ] **Console is clean** — no red errors in DevTools

### Emergency UI Shortcuts

If you're behind schedule:

| Problem | Shortcut | Time |
|---|---|---|
| No landing page | Skip it. Go straight to `/convert` as home. | Saves 1–2 hrs |
| Ugly layout | Wrap everything in `max-w-4xl mx-auto p-8` | 30 seconds |
| No loading animation | Use a simple `v-if` with text: "Converting..." | 2 minutes |
| No animations at all | Just `transition-all duration-200` on interactive elements | 5 minutes |
| Colors look off | Use a pre-made palette from [realtime colors](https://www.realtimecolors.com) | 10 minutes |
| No toast | `window.alert("Copied!")` — it works in a demo 🤷 | 10 seconds |

---

## Figma → Code Translation Examples

### Example 1: Figma Button → shadcn + Motion

**Figma specs:** Blue fill (#3B82F6), 16px padding horizontal, 8px vertical, 8px border-radius, white text, 16px font, semibold

```vue
<!-- Option A: shadcn Button (fastest — already styled) -->
<script setup lang="ts">
import { Button } from '@/components/ui/button'
</script>

<template>
  <motion.div :whileHover="{ scale: 1.03 }" :whilePress="{ scale: 0.97 }">
    <Button>Convert to LaTeX</Button>
  </motion.div>
</template>
```

```vue
<!-- Option B: Hand-built with Tailwind (if you need full control) -->
<motion.button
  :whileHover="{ scale: 1.03 }"
  :whilePress="{ scale: 0.97 }"
  class="bg-primary hover:bg-primary-hover text-white font-semibold
         px-4 py-2 rounded-lg transition-colors"
>
  Convert to LaTeX
</motion.button>
```

### Example 2: Figma Card → shadcn Card or Tailwind

**Figma specs:** Dark surface (#1E1E2E), 24px padding, 16px border-radius, subtle shadow

```vue
<!-- Option A: shadcn Card (structured, accessible) -->
<script setup lang="ts">
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>{{ title }}</CardTitle>
      <CardDescription>{{ description }}</CardDescription>
    </CardHeader>
    <CardContent>
      <slot />
    </CardContent>
  </Card>
</template>
```

```vue
<!-- Option B: Raw Tailwind (for custom layouts) -->
<div class="bg-surface rounded-2xl p-6 shadow-lg">
  <h3 class="text-text font-semibold text-lg mb-2">{{ title }}</h3>
  <p class="text-text-muted text-sm">{{ description }}</p>
</div>
```

### Example 3: Figma Split Layout → Vue Grid

**Figma specs:** Two equal columns, 24px gap, full viewport height minus nav

```vue
<div class="grid grid-cols-2 gap-6 h-[calc(100vh-4rem)] p-6">
  <div class="bg-surface rounded-2xl p-6 overflow-auto">
    <!-- Left: image -->
  </div>
  <div class="bg-surface rounded-2xl p-6 overflow-auto">
    <!-- Right: LaTeX -->
  </div>
</div>
```

---

## Deployment (Last Resort — Hour 20+)

If you want a live URL for the demo:

```bash
# Option 1: Vercel (fastest)
npm i -g vercel
cd src/frontend
vercel

# Option 2: Netlify
npm run build
# drag dist/ folder to netlify.com/drop
```

> **But honestly:** for a hackathon demo, just run `npm run dev` locally. Don't waste time on deployment unless judges specifically ask for a live link.

---

## The Golden Rules

1. **If it works in the demo, it works.** Don't chase perfection.
2. **Build → Style → Animate.** Never animate something that doesn't function yet.
3. **AI for boilerplate, hand-code for core.** Generate the landing page, build the upload zone yourself.
4. **Figma is reference, not spec.** Match the vibe, not the exact pixels.
5. **3 great animations > 20 mediocre ones.** Pick your "wow" moments.
6. **Tailwind v4 `@theme` is your single source of truth** for colors and spacing.
7. **Test the demo flow 5 times** before presenting. Catch bugs before judges do.
8. **If you're stuck on styling for 15+ minutes, move on.** Come back during polish.

---

## Quick Reference Links

| Resource | URL |
|---|---|
| shadcn-vue docs | https://www.shadcn-vue.com/docs |
| shadcn-vue components | https://www.shadcn-vue.com/docs/components |
| Tailwind CSS docs | https://tailwindcss.com/docs |
| Motion for Vue docs | https://motion.dev/docs/vue |
| KaTeX supported functions | https://katex.org/docs/supported |
| Vue 3 SFC guide | https://vuejs.org/guide/scaling-up/sfc |
| Figma → Tailwind spacing | 4px = `1`, 8px = `2`, 16px = `4`, 32px = `8` |
| Your code snippets | [FRONTEND-REFERENCE.md](FRONTEND-REFERENCE.md) |
| API contract | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Your task checklist | [CHECKLIST-FRONTEND.md](CHECKLIST-FRONTEND.md) |
