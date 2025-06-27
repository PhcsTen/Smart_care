<template>
  <v-main class="vector-bg center-content">
    <div class="login-container">
      <div class="logo">
        <img
          src="@/assets/image/logo.png"
          alt="Company logo"
          width="180"
          height="180"
        />
      </div>

      <h2 class="login-title">เข้าสู่ระบบ</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <input
            type="text"
            id="username"
            v-model="username"
            required
            placeholder="Username"
            class="vector-input"
          />
        </div>
        <div class="form-group">
          <input
            type="password"
            id="password"
            v-model="password"
            required
            placeholder="Password"
            class="vector-input"
          />
        </div>
        <button type="submit" :disabled="loading" class="vector-button">
          {{ loading ? "Processing..." : "LOGIN" }}
        </button>
      </form>

      <p class="forgot-password">Forgot Password?</p>
      <p v-if="message" class="message">{{ message }}</p>
    </div>
  </v-main>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import { API_BASE_URL } from "@/assets/config";

const username = ref("");
const password = ref("");
const message = ref("");
const loading = ref(false);

const router = useRouter();

const handleLogin = async () => {
  loading.value = true;
  message.value = "";

  try {
    const res = await axios.post(`${API_BASE_URL}/login`, {
      username: username.value,
      password: password.value,
    });

    if (res.data.access_token) {
      localStorage.setItem("access_token", res.data.access_token);
      const user = await getCurrentUser();
      if (user) {
        localStorage.setItem("user_data", JSON.stringify(user));
        await router.push("/home");
      } else {
        message.value = "ไม่สามารถโหลดข้อมูลผู้ใช้";
      }
    } else {
      message.value = "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง";
    }
  } catch (err) {
    if (err.response && err.response.data?.message) {
      message.value = err.response.data.message;
    } else {
      message.value = "เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์";
    }
  } finally {
    loading.value = false;
  }
};

//ดึงข้อมูลผู้ใช้ที่ Login
async function getCurrentUser() {
  try {
    const token = localStorage.getItem("access_token");
    console.log("🔑 Token:", token);

    if (!token) throw new Error("Token not found");

    const response = await axios.get(`${API_BASE_URL}/user/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const user = response.data;
    console.log("✅ ข้อมูลผู้ใช้:", user);

    // ✅ บันทึกข้อมูลผู้ใช้ลง localStorage
    localStorage.setItem("user", JSON.stringify(user));

    return user;

  } catch (error) {
    const msg = error.response?.data?.message || error.message || "Unknown error";
    console.error("⛔ ดึงข้อมูลผู้ใช้ล้มเหลว:", msg);

    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      await router.push("/login");
    }

    return null;
  }
}

</script>

<style scoped></style>
