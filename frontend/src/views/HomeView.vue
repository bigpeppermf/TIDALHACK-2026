<script setup lang="ts">
import AppNavbar from '@/components/AppNavbar.vue'
import HeroSection from '@/components/HeroSection.vue'
import FeaturesGrid from '@/components/FeaturesGrid.vue'
import HowItWorks from '@/components/HowItWorks.vue'
import AppFooter from '@/components/AppFooter.vue'
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
