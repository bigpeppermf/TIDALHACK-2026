<script setup lang="ts">
import AppNavbar from '@/components/layout/AppNavbar.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import FeaturesGrid from '@/components/landing/FeaturesGrid.vue'
import HeroSection from '@/components/landing/HeroSection.vue'
import HowItWorks from '@/components/landing/HowItWorks.vue'
</script>

<template>
  <main class="min-h-screen bg-background">
    <AppNavbar />
    <HeroSection />
    <FeaturesGrid />
    <HowItWorks />
    <AppFooter />
  </main>
</template>
