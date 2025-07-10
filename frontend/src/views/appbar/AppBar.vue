<template>
  <v-app-bar app color="#3498db" dark>
    <!-- ปุ่ม toggle drawer -->
    <!-- <v-app-bar-nav-icon @click="$emit('toggle-drawer')" /> -->
    <template #prepend>
      <v-avatar size="40">
        <v-img src="@/assets/image/logo.png" alt="Logo" />
      </v-avatar>
    </template>

    <!-- ชื่อแอป -->
    <v-toolbar-title>Smart Care System</v-toolbar-title>
    <!-- logout -->
    <v-spacer></v-spacer>

    <!-- ปุ่ม Logout -->
    <v-btn icon @click="logout" title="ออกจากระบบ">
      <v-icon>mdi-logout</v-icon>
    </v-btn>
  </v-app-bar>
</template>

<script setup>
import { onMounted } from "vue";
import { useRouter } from 'vue-router'

const router = useRouter()

const logout = () => {
  localStorage.removeItem('token') // ลบ token
  router.push('/login')            // กลับไปหน้า login
}
// รับ emit จาก props
const emit = defineEmits(["toggle-drawer"]);

onMounted(() => {
  emit("toggle-drawer"); // เรียก toggle-drawer ตอนโหลดหน้าเลย
});
</script>

<style scoped></style>
