<template>
  <v-navigation-drawer
    v-model="drawer"
    expand-on-hover
    rail
    app
    style="background-color: "
  >
    <v-list>
      <v-list-item>
        <template #prepend>
          <v-avatar size="40">
            <v-img src="@/assets/image/logo.png" alt="Logo" />
          </v-avatar>
        </template>
        <v-list-item-title>เด็กๆ</v-list-item-title>
        <v-list-item-subtitle>Smart Care Home</v-list-item-subtitle>
      </v-list-item>
    </v-list>

    <v-divider></v-divider>

    <!-- เมนูหลักจาก menuItemsData -->
    <v-list density="compact" nav>
      <v-list-item
        v-for="(item, i) in menuItems"
        :key="i"
        @click="handleMenuClick(item)"
      >
        <template #prepend>
          <v-icon>{{ item.icon }}</v-icon>
        </template>
        <v-list-item-title>{{ item.title }}</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-navigation-drawer>
  <!-- บริการหลักในหน้า Home -->
  <v-container>
    <v-row class="mt-4" justify="center">
      <v-col
        v-for="service in services"
        :key="service.index"
        cols="12"
        sm="6"
        md="4"
        lg="3"
      >
        <v-card class="mx-auto menu-bg" max-width="200" elevation="6">
          <v-card-actions class="justify-center">
            <v-icon dark size="48" :color="service.color">{{
              service.icon
            }}</v-icon>
          </v-card-actions>

          <v-card-title class="text-center">{{ service.name }}</v-card-title>

          <v-card-actions class="justify-center">
            <v-btn
              :to="service.router"
              :color="service.color"
              variant="elevated"
            >
              คลิก
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>

  <!-- ใช้ App Bar ที่แยกไว้-->
  <AppBar @toggle-drawer="drawer = !drawer" />

  <!-- Router View สำหรับเนื้อหาที่เปลี่ยน (เช่น Add) -->
  <v-main>
    <router-view />
  </v-main>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import menuItemsData from "@/views/menu/menuItemsData";
import AppBar from "@/views/appbar/AppBar.vue";

const drawer = ref(true);
const router = useRouter();

onMounted(() => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    router.push("/login");
  }
});

const menuItems = menuItemsData;

const logout = () => {
  localStorage.removeItem("access_token");
  router.push("/login");
};

const handleMenuClick = (item) => {
  if (item.click === "logout") {
    logout();
  } else if (item.href) {
    router.push(item.href);
  }
};
const services = [
  {
    index: "1",
    name: "เซ็คชื่อ/ตรวจสุขภาพเด็ก",
    icon: "mdi-home",
    color: "success",
    background: "#e0f7fa",
    router: "",
  },
  {
    index: "2",
    name: "บันทึกกิจกรรมประจำวัน",
    color: "info",
    icon: "mdi-eye",
    router: "",
  },
  {
    index: "3",
    name: "อาหารกลางวัน",
    color: "orange darken-2",
    icon: "mdi-chat",
    router: "",
  },
  {
    index: "4",
    name: "บันทึกสังเกตพฤติกรรม",
    color: "purple",
    icon: "mdi-chart-bar",
    router: "",
  },
  {
    index: "5",
    name: "แหล่งเรียนรู้",
    color: "#9370DB", // Medium Purple (Hex)
    icon: "mdi-chart-bar",
    router: "",
  },
  {
    index: "6",
    name: "โครงการฯ",
    color: "#E6E6FA", // Lavender
    icon: "mdi-plus",
    router: "",
  },
  {
    index: "7",
    name: "แบบบันทึกพัฒนาการเด็ก",
    color: "#9400D3", // Dark Violet
    icon: "mdi-bell",
    router: "",
  },
  {
    index: "8",
    name: "บันทึกนำ้หนักส่วนสูง",
    color: "red",
    icon: "mdi-file-document",
    router: "",
  },
  {
    index: "9",
    name: "ข้อมูลเด็กนักเรียน",
    color: "red",
    icon: "mdi-file-document",
    router: "",
  },
  {
    index: "10",
    name: "ข้อมูลครู",
    color: "red",
    icon: "mdi-file-document",
    router: "",
  },
  {
    index: "11",
    name: "ข้อมูลบ้านนักเรียน",
    color: "red",
    icon: "mdi-file-document",
    router: "",
  },
  {
    index: "12",
    name: "แบบรายงาน",
    color: "red",
    icon: "mdi-file-document",
    router: "",
  },
];
</script>

<style scoped></style>
