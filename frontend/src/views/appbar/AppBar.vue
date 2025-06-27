<template>
  <v-app-bar app color="#3498db" dark>
    <!-- ปุ่ม toggle drawer -->
    <v-app-bar-nav-icon @click="$emit('toggle-drawer')" />

    <!-- ชื่อแอป -->
    <v-toolbar-title>Smart Care System</v-toolbar-title>
  </v-app-bar>
</template>

<script setup>
import { onMounted } from 'vue'

// รับ emit จาก props
const emit = defineEmits(['toggle-drawer'])

onMounted(() => {
  emit('toggle-drawer')  // เรียก toggle-drawer ตอนโหลดหน้าเลย
})
</script>

<style scoped>
</style>
