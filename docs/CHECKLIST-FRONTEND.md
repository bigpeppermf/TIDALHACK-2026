# 🎨 Teammate 1 — Frontend Checklist

> **Role:** Frontend Design & Development
> **Stack:** Figma, Vue 3, Motion (motion-v), KaTeX, TailwindCSS
> **Work in:** `src/frontend/`
> **Code ref:** `docs/FRONTEND-REFERENCE.md`

---

## 🏁 Phase 1 — Setup (Hours 0–4)

### With Teammate 2

- [ ] Align on project scope and review docs together
- [ ] Review API contract in `ARCHITECTURE.md` — agree on request/response shapes
- [ ] Confirm both dev servers run without port conflicts (you: `:5173`, them: `:8000`)

### Solo

- [ ] Scaffold Vue 3 project: `npm create vue@latest` in `src/frontend/`
- [ ] Pick: TypeScript ✅, Vue Router ✅, Pinia ❌, ESLint ❌
- [ ] Install deps: `npm install motion-v katex`
- [ ] Install dev deps: `npm install -D tailwindcss`
- [ ] Configure Tailwind
- [ ] Verify `npm run dev` serves on `:5173`
- [ ] Create `VITE_API_URL=http://localhost:8000` in `src/frontend/.env`
- [ ] Set up Vue Router: `/` → `HomePage.vue`, `/convert` → `ConvertPage.vue`
- [ ] Create empty page shells for both routes
- [ ] Start Figma designs: upload screen, loading screen, result screen

**✅ Milestone:** Vue dev server running. Router works. Figma wireframes started.

---

## 🔗 Phase 2 — Core Components (Hours 4–10)

### Upload Flow

- [ ] Build `UploadZone.vue` — drag-and-drop area + file picker button
- [ ] Add image thumbnail preview after file is selected
- [ ] File validation: only jpeg/png/webp, max 10MB, show error if wrong
- [ ] Create `useConvert` composable (see FRONTEND-REFERENCE.md)
- [ ] Wire upload → calls `POST /api/convert` → receives LaTeX string

### Result Display

- [ ] Build `ResultView.vue` — split layout: original image left, LaTeX right
- [ ] Build `LatexPreview.vue` — renders LaTeX with KaTeX
- [ ] Build `LatexEditor.vue` — editable text area (or CodeMirror) for LaTeX source
- [ ] Wire editor `@input` → live KaTeX preview re-render
- [ ] Build `LoadingAnimation.vue` — spinner + status text while API processes

### Export Actions

- [ ] Create `useExport` composable (see FRONTEND-REFERENCE.md)
- [ ] "Copy to Clipboard" button — copies raw LaTeX string
- [ ] "Download .tex" button — saves file locally

### Integration

- [ ] Connect full flow: upload → loading → result → edit → export
- [ ] Test with Teammate 2's live backend (not just mock data)

**✅ Milestone:** Full UI flow works end-to-end with real backend.

---

## ✨ Phase 3 — Polish & Animations (Hours 10–18)

### Motion Animations

- [ ] Upload zone: fade-in on mount (`initial={{ opacity: 0, y: 20 }}`)
- [ ] Upload zone: subtle scale on hover (`whileHover={{ scale: 1.02 }}`)
- [ ] Loading: rotating pen/pencil icon (`animate={{ rotate: 360 }}, repeat: Infinity`)
- [ ] Loading: staged status text ("Reading..." → "Converting..." → "Almost done...")
- [ ] Result panels: slide in from sides (`initial={{ x: -100 }}`)
- [ ] Buttons: press feedback (`whilePress={{ scale: 0.95 }}`)
- [ ] Success toast: slide-down "Copied!" notification
- [ ] Page transitions: fade on route change

### Landing Page

- [ ] Hero section: headline, subtext, call-to-action button
- [ ] Navbar: "ScribeTeX" logo/name + nav links
- [ ] Visual polish: consistent spacing, typography, colors

### Error States

- [ ] API unreachable → friendly "Server offline" message
- [ ] Bad image → "Couldn't read this image" message
- [ ] Gemini error → "Something went wrong, try again" message

### Responsive

- [ ] Test on phone viewport (375px)
- [ ] Stack split-panel to vertical on mobile
- [ ] Touch-friendly upload zone

### Nice-to-Have (if time)

- [ ] Dark mode toggle
- [ ] Context dropdown: Math / Chemistry / Physics / General (sends `?context=` to API)
- [ ] History page: save past conversions in localStorage
- [ ] Camera capture button (mobile)

**✅ Milestone:** App looks demo-ready. Animations are smooth. Edge cases handled.

---

## 🎤 Phase 4 — Demo Prep (Hours 18–24)

- [ ] Test all demo images in the UI (3–5 images)
- [ ] Fix any visual bugs found during testing
- [ ] Help build slide deck (Problem → Solution → Demo → Tech → Future)
- [ ] Ensure app looks great on the demo machine/projector resolution
- [ ] Practice live demo 2–3 times

---

## 🪓 Cut List (drop these first if behind)

1. ❌ Dark mode
2. ❌ History / localStorage
3. ❌ Camera capture
4. ❌ Context dropdown (backend hardcodes "general")
5. ❌ Mobile responsiveness (demo on laptop)
6. ❌ CodeMirror editor (use plain `<textarea>` instead)

## 🛡️ Never Cut

- ✅ Upload → Loading → Result flow
- ✅ KaTeX preview rendering
- ✅ Copy + Download buttons
- ✅ At least 1 "wow" Motion animation (result panels sliding in)
- ✅ Loading animation (makes demo feel polished)

---

## 🏆 Your Demo Day Checklist

- [ ] Frontend running on `:5173`
- [ ] Connected to backend on `:8000`
- [ ] App looks good on demo screen resolution
- [ ] No console errors in browser
- [ ] All demo images load and display correctly
