<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  scrollY: { type: Number, default: 0 },
  speed: { type: Number, default: 0.08 },
})

const el = ref(null)
const elTop = ref(0)

const updatePosition = () => {
  if (el.value) {
    const rect = el.value.getBoundingClientRect()
    elTop.value = rect.top + window.scrollY
  }
}

onMounted(() => {
  updatePosition()
  window.addEventListener('resize', updatePosition)
})

onUnmounted(() => {
  window.removeEventListener('resize', updatePosition)
})

const parallaxY = computed(() => {
  const diff = props.scrollY - elTop.value + window.innerHeight
  return diff * props.speed
})
</script>

<template>
  <div
    ref="el"
    :style="{ transform: `translateY(${parallaxY}px)`, willChange: 'transform' }"
  >
    <slot />
  </div>
</template>
