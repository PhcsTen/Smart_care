<template>
  <v-app>
    <v-main class="white-bg">
      <router-view />
      <AppFooter />
    </v-main>
  </v-app>
</template>

<script setup>
import AppFooter from "@/views/footer/AppFooter.vue"; // Footer แยกออกมา
</script>

<style scoped>
.white-bg {
  background-color: white !important;
}
</style>
