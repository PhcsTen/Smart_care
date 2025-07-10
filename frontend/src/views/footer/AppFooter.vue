<template>
  <v-footer app height="50" class="custom-footer">
    <a
      v-for="item in items"
      :key="item.title"
      :href="item.href"
      :title="item.title"
      class="d-inline-block mx-2 social-links text-decoration-none text-white"
      rel="noopener noreferrer"
      target="_blank"
    >
      <v-icon :icon="item.icon" :size="item.icon === '$vuetify' ? 24 : 16" />
      {{ item.title }}
    </a>

    <div
      class="text-caption"
      style="position: absolute; right: 16px; color: #cccccc"
    >
      &copy; 2025-{{ new Date().getFullYear() }}
      <span class="d-none d-sm-inline-block">Smart Care System</span>
      —
      <a
        class="text-decoration-none"
        href="https://www.google.com/"
        rel="noopener noreferrer"
        target="_blank"
        style="color: #ffffff"
      >
        Tech Five Studio
      </a>
    </div>
  </v-footer>
</template>

<script setup>
const items = [
  {
    title: "คู่มือ",
    icon: "mdi-file-pdf-box",
    href: "", // ลิงก์คู่มือ
  },
];
</script>

<style scoped></style>
