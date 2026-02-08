<script setup lang="ts">
import AppNavbar from '@/components/layout/AppNavbar.vue'
import HeroSection from '@/components/landing/HeroSection.vue'
import FeaturesGrid from '@/components/landing/FeaturesGrid.vue'
import HowItWorks from '@/components/landing/HowItWorks.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
</script>

<template>
  <main class="min-h-screen" style="background-color: hsl(var(--background))">
    <AppNavbar />
    <HeroSection />
    <FeaturesGrid />
    <HowItWorks />
    <AppFooter />
  </main>
</template>
