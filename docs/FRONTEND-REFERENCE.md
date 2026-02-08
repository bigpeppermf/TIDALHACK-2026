# 🎨 Frontend Code Reference — Vue 3

> **Teammate 1's code snippets. Pull what you need as you build.**
> Last updated: Feb 7, 2026 (via Context7 MCP)

---

## Scaffold & Install

```bash
npm create vue@latest
# Pick: TypeScript ✅, Vue Router ✅, Pinia ❌, ESLint ❌ (hackathon speed)

cd frontend
npm install
npm install motion-v katex
npm install -D tailwindcss @tailwindcss/vite

# Initialize shadcn-vue (sets up cn utility, configures paths)
npx shadcn-vue@latest init

# Add the components you'll actually use
npx shadcn-vue@latest add button card input textarea sonner
```

Node.js requirement: `^20.19.0 || >=22.12.0`

```bash
npm run dev   # → http://localhost:5173
```

---

## Vue Router Setup

```typescript
// frontend/src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import ConvertPage from '../views/ConvertPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomePage },
    { path: '/convert', component: ConvertPage }
  ]
})

export default router
```

---

## Motion for Vue — Basics

```bash
npm install motion-v
```

### Fade In on Mount

```vue
<script setup>
import { motion } from 'motion-v'
</script>

<template>
  <motion.div
    :initial="{ opacity: 0, y: 20 }"
    :animate="{ opacity: 1, y: 0 }"
    :transition="{ duration: 0.5 }"
  >
    Content fades in
  </motion.div>
</template>
```

### Hover & Press Gestures

```vue
<motion.button
  :whileHover="{ scale: 1.05 }"
  :whilePress="{ scale: 0.95 }"
  @hoverStart="() => console.log('hover!')"
>
  Click me
</motion.button>
```

### Continuous Rotation (Loading Spinner)

```vue
<motion.div
  :animate="{ rotate: 360 }"
  :transition="{ duration: 2, repeat: Infinity, ease: 'linear' }"
>
  <!-- spinner SVG here -->
</motion.div>
```

### Slide In from Side

```vue
<motion.div
  :initial="{ x: -100, opacity: 0 }"
  :animate="{ x: 0, opacity: 1 }"
  :transition="{ duration: 0.6, ease: 'easeOut' }"
>
  Slides in from the left
</motion.div>
```

### Layout Animation (Expand/Collapse)

```vue
<script setup>
import { ref } from 'vue'
</script>

<template>
  <motion.div layout @click="isOpen = !isOpen">
    <motion.h2 layout>Header</motion.h2>
    {{ isOpen ? 'Expanded content here' : null }}
  </motion.div>
</template>
```

### useMotionValue (No Re-renders)

```vue
<script setup>
import { useMotionValue, motion } from 'motion-v'
import { onMounted } from 'vue'

const x = useMotionValue(0)

onMounted(() => {
  setTimeout(() => x.set(100), 1000)
})
</script>

<template>
  <motion.div :style="{ x }" />
</template>
```

---

## Animation Plan — Quick Reference

| Element | Animation | Key Props |
|---|---|---|
| Upload zone mount | Fade up | `initial={{ opacity: 0, y: 20 }}` → `animate={{ opacity: 1, y: 0 }}` |
| Upload zone hover | Subtle scale | `whileHover={{ scale: 1.02 }}` |
| Loading spinner | Rotate forever | `animate={{ rotate: 360 }}` + `repeat: Infinity` |
| Result panels | Slide in | `initial={{ x: -100 }}` → `animate={{ x: 0 }}` |
| Buttons | Press feedback | `whilePress={{ scale: 0.95 }}` |
| Toast notification | Slide down + fade | `initial={{ y: -50, opacity: 0 }}` |
| Page transition | Fade cross | `initial={{ opacity: 0 }}` on route enter |

---

## KaTeX — LaTeX Rendering

```bash
npm install katex
```

```vue
<!-- frontend/src/components/LatexPreview.vue -->
<script setup>
import { computed } from 'vue'
import katex from 'katex'
import 'katex/dist/katex.min.css'

const props = defineProps<{ latex: string }>()

const rendered = computed(() => {
  try {
    return katex.renderToString(props.latex, {
      throwOnError: false,
      displayMode: true
    })
  } catch (e: any) {
    return `<span class="text-red-500">LaTeX Error: ${e.message}</span>`
  }
})
</script>

<template>
  <div v-html="rendered" class="latex-preview p-4" />
</template>
```

> **Note:** KaTeX renders math beautifully but doesn't handle full `\documentclass` documents. You'll want to strip the preamble for preview, or use KaTeX just for the math portions.

---

## shadcn-vue — Pre-Built UI Components

shadcn-vue gives you polished, accessible components you own (copied into your project, not a dependency).

### Setup

```bash
# Already done in scaffold step — just for reference
npx shadcn-vue@latest init
# Prompts: style (New York or Default), base color, CSS variables (Yes)
```

Components are installed into `frontend/src/components/ui/`.

### Button (variants: default, outline, secondary, ghost, destructive)

```vue
<script setup lang="ts">
import { Button } from '@/components/ui/button'
</script>

<template>
  <!-- Primary CTA -->
  <Button>Convert to LaTeX</Button>

  <!-- Secondary action -->
  <Button variant="outline">Download .tex</Button>

  <!-- Danger -->
  <Button variant="destructive">Clear</Button>

  <!-- Sizes -->
  <Button size="sm">Small</Button>
  <Button size="lg">Large</Button>
  <Button size="icon">✏️</Button>
</template>
```

### Card (for result panels, landing page sections)

```vue
<script setup lang="ts">
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>LaTeX Output</CardTitle>
      <CardDescription>Converted from your handwriting</CardDescription>
    </CardHeader>
    <CardContent>
      <LatexPreview :latex="latex" />
    </CardContent>
    <CardFooter class="flex gap-2">
      <Button @click="copy">Copy</Button>
      <Button variant="outline" @click="download">Download .tex</Button>
    </CardFooter>
  </Card>
</template>
```

### Input & Textarea

```vue
<script setup lang="ts">
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
</script>

<template>
  <!-- Filename input for export -->
  <Input v-model="filename" placeholder="my_notes" />

  <!-- LaTeX editor (alternative to CodeMirror) -->
  <Textarea
    v-model="latex"
    class="font-mono text-sm min-h-[300px]"
    placeholder="LaTeX will appear here..."
  />
</template>
```

### Sonner Toast (for "Copied!" feedback)

```vue
<!-- Add Toaster once in App.vue -->
<script setup lang="ts">
import { Toaster } from '@/components/ui/sonner'
</script>

<template>
  <RouterView />
  <Toaster />
</template>
```

```vue
<!-- Then use toast() anywhere -->
<script setup lang="ts">
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'

function copyLatex() {
  navigator.clipboard.writeText(latex.value)
  toast('Copied to clipboard!', {
    description: 'LaTeX source is ready to paste',
  })
}
</script>

<template>
  <Button @click="copyLatex">📋 Copy LaTeX</Button>
</template>
```

### Adding More Components On-The-Fly

```bash
# Need a dropdown for context selector? Just add it:
npx shadcn-vue@latest add dropdown-menu

# Need a dialog for export options?
npx shadcn-vue@latest add dialog

# Need a tooltip for icon buttons?
npx shadcn-vue@latest add tooltip
```

> **Hackathon tip:** Only `add` components as you need them. Don't install everything upfront.

---

## useConvert Composable

```typescript
// frontend/src/composables/useConvert.ts
import { ref } from 'vue'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function useConvert() {
  const loading = ref(false)
  const latex = ref('')
  const error = ref<string | null>(null)

  async function convert(file: File, context?: string) {
    loading.value = true
    error.value = null
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(
        `${API_URL}/api/convert?context=${context || 'general'}`,
        { method: 'POST', body: formData }
      )
      const data = await res.json()
      if (data.success) {
        latex.value = data.latex
      } else {
        error.value = data.error
      }
    } catch {
      error.value = 'Failed to connect to server'
    } finally {
      loading.value = false
    }
  }

  return { loading, latex, error, convert }
}
```

---

## useExport Composable

```typescript
// frontend/src/composables/useExport.ts

export function useExport() {
  function downloadTex(latex: string, filename = 'notes') {
    const blob = new Blob([latex], { type: 'application/x-tex' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${filename}.tex`
    a.click()
    URL.revokeObjectURL(url)
  }

  async function copyToClipboard(text: string) {
    await navigator.clipboard.writeText(text)
  }

  return { downloadTex, copyToClipboard }
}
```

---

## Component Skeleton Ideas

### UploadZone

```vue
<template>
  <motion.div
    :initial="{ opacity: 0, y: 20 }"
    :animate="{ opacity: 1, y: 0 }"
    :whileHover="{ scale: 1.02 }"
    class="border-2 border-dashed rounded-xl p-12 text-center cursor-pointer"
    @dragover.prevent="isDragging = true"
    @dragleave="isDragging = false"
    @drop.prevent="onDrop"
    @click="openFilePicker"
  >
    <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="onFileSelect" />
    <p>📄 Drop your handwritten notes here</p>
    <p class="text-sm text-gray-400">or click to browse</p>
  </motion.div>
</template>
```

### LoadingAnimation

```vue
<template>
  <div class="flex flex-col items-center gap-4">
    <motion.div
      :animate="{ rotate: 360 }"
      :transition="{ duration: 2, repeat: Infinity, ease: 'linear' }"
      class="text-4xl"
    >
      ✏️
    </motion.div>
    <motion.p
      :initial="{ opacity: 0 }"
      :animate="{ opacity: 1 }"
      :transition="{ delay: 0.3 }"
    >
      {{ statusText }}
    </motion.p>
  </div>
</template>
```

### ResultView (Split Layout)

```vue
<template>
  <div class="grid grid-cols-2 gap-4">
    <!-- Left: original image -->
    <motion.div :initial="{ x: -50, opacity: 0 }" :animate="{ x: 0, opacity: 1 }">
      <img :src="imageUrl" class="rounded-lg shadow" />
    </motion.div>
    
    <!-- Right: LaTeX output -->
    <motion.div :initial="{ x: 50, opacity: 0 }" :animate="{ x: 0, opacity: 1 }">
      <LatexEditor v-model="latex" />
      <LatexPreview :latex="latex" />
    </motion.div>
  </div>
</template>
```

---

## Figma → Vue Workflow

1. **Design screens in Figma** — upload, loading, result, landing
2. **Export** — icons as SVG, images as webp
3. **Map** Figma layers to Vue components 1:1
4. **Tailwind** — translate Figma spacing/colors to utility classes
5. **Motion** — add animations last, on top of working styled components

---

## Frontend Dependencies Summary

```json
{
  "dependencies": {
    "vue": "^3.5.0",
    "vue-router": "^4.4.0",
    "motion-v": "latest",
    "katex": "^0.16.0",
    "reka-ui": "latest",
    "class-variance-authority": "latest",
    "clsx": "latest",
    "tailwind-merge": "latest",
    "vue-sonner": "latest"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^6.0.0",
    "tailwindcss": "^4.0.0",
    "@tailwindcss/vite": "latest",
    "typescript": "^5.5.0"
  }
}
```

---

## Tips

- Build components **without** Motion first → add animations after it works
- Use `VITE_API_URL` env var so you never hardcode `localhost:8000`
- KaTeX is for **preview only** — the real output is the raw `.tex` string
- Test upload with a small jpeg first before handling edge cases
- Tailwind makes hackathon styling 10x faster — don't write custom CSS
- **shadcn-vue components are yours** — they live in `src/components/ui/`, edit them freely
- Use shadcn `Button` for all buttons, `Card` for panels, `Textarea` for the LaTeX editor
- Use Sonner `toast()` instead of building a custom toast — it's already styled
- Wrap Motion animations **around** shadcn components: `<motion.div><Button>...</Button></motion.div>`
