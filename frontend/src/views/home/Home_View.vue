<template>
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
// import menuItemsData from "@/views/menu/menuItemsData";
import AppBar from "@/views/appbar/AppBar.vue";

const drawer = ref(true);
const router = useRouter();

onMounted(() => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    router.push("/login");
  }
});
const services = [
  // {
  //   index: "1",
  //   name: "เซ็คชื่อ/ตรวจสุขภาพเด็ก",
  //   icon: "mdi-home",
  //   color: "success",
  //   background: "#e0f7fa",
  //   router: "",
  // },
  // {
  //   index: "2",
  //   name: "บันทึกกิจกรรมประจำวัน",
  //   color: "info",
  //   icon: "mdi-eye",
  //   router: "",
  // },
  // {
  //   index: "3",
  //   name: "อาหารกลางวัน",
  //   color: "orange darken-2",
  //   icon: "mdi-chat",
  //   router: "",
  // },
  // {
  //   index: "4",
  //   name: "บันทึกสังเกตพฤติกรรม",
  //   color: "purple",
  //   icon: "mdi-chart-bar",
  //   router: "",
  // },
  // {
  //   index: "5",
  //   name: "แหล่งเรียนรู้",
  //   color: "#9370DB", // Medium Purple (Hex)
  //   icon: "mdi-chart-bar",
  //   router: "",
  // },
  // {
  //   index: "6",
  //   name: "โครงการฯ",
  //   color: "#E6E6FA", // Lavender
  //   icon: "mdi-plus",
  //   router: "",
  // },
  // {
  //   index: "7",
  //   name: "แบบบันทึกพัฒนาการเด็ก",
  //   color: "#9400D3", // Dark Violet
  //   icon: "mdi-bell",
  //   router: "",
  // },
  // {
  //   index: "8",
  //   name: "บันทึกนำ้หนักส่วนสูง",
  //   color: "red",
  //   icon: "mdi-file-document",
  //   router: "",
  // },
  {
    index: "9",
    name: "นักเรียน",
    color: "#03a9f4",
    icon: "mdi-account-school-outline",
    router: "/students",
  },
  {
    index: "10",
    name: "ครู",
    color: "#ff5800",
    icon: "mdi-account-badge-outline",
    router: "/teacher",
  },
  {
    index: "11",
    name: "ห้องเรียน/ระดับชั้น",
    color: "#f500ff",
    icon: "mdi-google-classroom",
    router: "/classrooms",
  },
  {
    index: "12",
    name: "ปีการศึกษา",
    color: "#ffffff",
    icon: "mdi-calendar-clock",
    router: "/years",
  },
  {
    index: "13",
    name: "สมาชิก",
    color: "#00ff00",
    icon: "mdi-account-group-outline",
    router: "/users",
  },
  {
    index: "14",
    name: "ตั้งค่า",
    color: "#00ffff",
    icon: "mdi-cog",
    router: "",
  },
  
];
</script>

<style scoped>
</style>
