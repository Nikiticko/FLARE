<template>
  <div class="app">
    <TopNavigationBar />
    <router-view />
    <CookieBanner />
  </div>
</template>

<script setup>
import TopNavigationBar from './components/TopNavigationBar.vue'
import CookieBanner from './components/CookieBanner.vue'
</script>

<style scoped>
.app {
  width: 100%;
  min-height: 100vh;
  margin: 0;
  padding: 0;
  overflow-x: hidden;
  overflow-y: auto;
}
</style>
