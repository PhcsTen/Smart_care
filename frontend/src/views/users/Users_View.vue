<template>
  <!-- App Bar ด้านบน มีปุ่ม toggle drawer -->
  <AppBar @toggle-drawer="drawer = !drawer" />

  <!-- ส่วนเนื้อหาหลักของหน้า -->
  <v-main>
    <v-container>
      <!-- แถวปุ่ม กลับ และ เพิ่มข้อมูลสมาชิก -->
      <v-row class="align-center">
        <v-col cols="auto" class="pa-0">
          <!-- ปุ่มกลับ -->
          <v-btn color="red" @click="goBack" class="btn-back">
            <v-icon start>mdi-arrow-left</v-icon>
            กลับ
          </v-btn>
        </v-col>
        <v-col cols="auto" class="pa-0 ml-3">
          <!-- ปุ่มเพิ่มสมาชิก -->
          <v-btn color="success" @click="add">
            <v-icon start>mdi-account-group-outline</v-icon>
            เพิ่มข้อมูลสมาชิก
          </v-btn>
        </v-col>
      </v-row>

      <div style="height: 24px"></div>
      <!-- เว้นวรรค -->

      <!-- ตารางข้อมูลสมาชิก -->
      <v-sheet rounded>
        <v-data-table
          :headers="headers"
          :items="users"
          :items-per-page="10"
          :search="search"
          class="custom-table custom-footer"
        >
          <!-- toolbar ด้านบนของตาราง มีชื่อและช่องค้นหา -->
          <template v-slot:top>
            <v-toolbar flat class="bg-success text-white">
              <v-toolbar-title>
                <v-icon
                  icon="mdi-account-group-outline"
                  size="x-small"
                  class="me-2"
                  color="white"
                />
                ตารางข้อมูลสมาชิก
              </v-toolbar-title>
              <v-spacer></v-spacer>
              <!-- ช่องค้นหา -->
              <v-text-field
                v-model="search"
                label="ค้นหา"
                clearable
                variant="outlined"
                hide-details
                density="compact"
                style="max-width: 300px"
              />
            </v-toolbar>
          </template>

          <!-- กำหนด header ตารางเอง (สีพื้นหลังและตัวอักษร) -->
          <template v-slot:header="{ headers }">
            <tr>
              <th
                v-for="header in headers"
                :key="header.key"
                style="background-color: #43a047; color: white"
              >
                {{ header.title }}
              </th>
            </tr>
          </template>

          <!-- กำหนดแต่ละแถวข้อมูล -->
          <template v-slot:item="{ item, index }">
            <tr
              :style="{
                backgroundColor: index % 2 === 0 ? '#e8f5e9' : '#ffffff',
              }"
            >
              <td style="color: black">{{ index + 1 }}</td>
              <!-- ลำดับ -->
              <td style="color: black">{{ item.user_name }}</td>
              <!-- ชื่อผู้ใช้ -->
              <td style="color: black">{{ item.email }}</td>
              <!-- อีเมล -->
              <td style="color: black">{{ formatDate(item.updated_date) }}</td>
              <!-- วันที่อัพเดต -->
              <!-- ปุ่มแก้ไข -->
              <td class="text-center">
                <v-avatar
                  color="yellow-darken-2"
                  size="32"
                  class="elevation-1"
                  style="cursor: pointer"
                  @click="edit(item.user_id)"
                >
                  <v-icon color="white" icon="mdi-pencil" size="20" />
                </v-avatar>
              </td>
              <!-- ปุ่มลบ -->
              <td class="text-center">
                <v-avatar
                  color="red-darken-1"
                  size="32"
                  class="elevation-1"
                  style="cursor: pointer"
                  @click="confirmRemove(item.user_id)"
                >
                  <v-icon color="white" icon="mdi-delete" size="20" />
                </v-avatar>
              </td>
            </tr>
          </template>
        </v-data-table>
      </v-sheet>
    </v-container>

    <!-- Dialog ยืนยันการลบผู้ใช้ -->
    <v-dialog v-model="confirmDeleteDialog" max-width="400">
      <v-card class="confirm-delete-dialog">
        <v-card-title class="text-h6 confirm-delete-title"
          >ยืนยันการลบ</v-card-title
        >
        <v-card-text class="confirm-delete-text"
          >คุณต้องการลบผู้ใช้นี้ใช่หรือไม่?</v-card-text
        >
        <v-card-actions class="confirm-delete-actions">
          <v-spacer />
          <!-- ปุ่มยกเลิก -->
          <v-btn
            color="red-darken-1"
            variant="flat"
            class="text-white"
            @click="confirmDeleteDialog = false"
            >ยกเลิก</v-btn
          >
          <!-- ปุ่มยืนยันลบ -->
          <v-btn
            color="green-darken-1"
            variant="flat"
            class="text-white"
            @click="confirmDelete"
            >ลบ</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar แจ้งเตือนสถานะ -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      timeout="1000"
      location="center"
      class="snackbar-fullscreen"
      transition="slide-y-transition"
    >
      <v-icon
        icon="mdi-alert-circle-outline"
        class="mr-2"
        size="large"
        color="white"
      />
      {{ snackbar.text }}
    </v-snackbar>

    <!-- Dialog สำหรับเพิ่ม/แก้ไขข้อมูลผู้ใช้ -->
    <v-dialog v-model="dialog" max-width="850">
      <v-card
        class="dialog-popup"
        style="background-color: #ffffff; color: black"
      >
        <!-- Toolbar สีขึ้นอยู่กับสถานะเพิ่ม/แก้ไข -->
        <v-toolbar flat :color="isEditing ? 'warning' : 'success'">
          <v-card-title class="dialog-title text-white">
            {{ isEditing ? "  แก้ไขข้อมูลผู้ใช้" : "  เพิ่มข้อมูลผู้ใช้" }}
          </v-card-title>
        </v-toolbar>
        <!-- ฟอร์มข้อมูล -->
        <v-card-text
          :class="isEditing ? 'card-text-warning' : 'card-text-success'"
        >
          <v-row>
            <v-col cols="12" md="6">
              <!-- ชื่อผู้ใช้ disabled เมื่อ edit -->
              <v-text-field
                v-model="record.user_name"
                label="ชื่อผู้ใช้"
                variant="outlined"
                color="success"
                class="custom-input"
                :rules="[required]"
                :disabled="isEditing"
              />
            </v-col>
            <v-col cols="12" md="6">
              <!-- อีเมล -->
              <v-text-field
                v-model="record.email"
                label="อีเมล"
                variant="outlined"
                color="success"
                class="custom-input"
                :rules="[required, emailRule]"
              />
            </v-col>
            <!-- รหัสผ่าน -->
            <v-col cols="12" md="6">
              <v-text-field
                v-model="record.password"
                label="รหัสผ่าน"
                type="password"
                variant="outlined"
                color="success"
                class="custom-input"
                :rules="isEditing ? [] : [required]"
              />
            </v-col>

            <!-- ยืนยันรหัสผ่าน -->
            <v-col cols="12" md="6">
              <v-text-field
                v-model="record.confirmPassword"
                label="ยืนยันรหัสผ่าน"
                type="password"
                variant="outlined"
                color="success"
                class="custom-input"
                :rules="isEditing ? [] : [required, passwordMatch]"
              />
            </v-col>
          </v-row>
        </v-card-text>

        <v-divider />

        <!-- ปุ่มบันทึกและยกเลิก -->
        <v-card-actions
          :class="[
            'd-flex justify-end',
            isEditing ? 'action-warning' : 'action-success',
          ]"
        >
          <v-btn
            color="red-darken-1"
            variant="flat"
            class="text-white"
            @click="dialog = false"
            >ยกเลิก</v-btn
          >
          <v-btn
            color="green-darken-1"
            variant="flat"
            class="text-white ml-2"
            @click="save"
            :disabled="!isFormValid"
          >
            บันทึก
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-main>
</template>

<script setup>
import { ref, shallowRef, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import AppBar from "@/views/appbar/AppBar.vue";
import { API_BASE_URL } from "@/assets/config";

// ตัวแปรควบคุมเมนู drawer เปิด/ปิด
const drawer = ref(true);

// ตัวแปร router สำหรับเปลี่ยนหน้า
const router = useRouter();

// ควบคุม Dialog เพิ่ม/แก้ไขข้อมูล
const dialog = shallowRef(false);
const isEditing = shallowRef(false);

// รายการเมนู ดึงมาจากไฟล์แยก
// const menuItems = menuItemsData;

// ค่าตั้งต้นสำหรับฟอร์มข้อมูลผู้ใช้
const DEFAULT_RECORD = {
  user_id: null,
  user_name: "",
  email: "",
  password: "",
  confirmPassword: "",
};

// ตัวแปรเก็บข้อมูลผู้ใช้ทั้งหมด (จาก API)
const users = ref([]);

// ตัวแปรเก็บข้อมูลผู้ใช้ที่กำลังเพิ่ม/แก้ไข
const record = ref({ ...DEFAULT_RECORD });

// ค้นหา
const search = ref("");

// ตัวแปรควบคุม Dialog ยืนยันลบ และเก็บ id ที่จะลบ
const confirmDeleteDialog = ref(false);
const deleteId = ref(null);

// Snackbar แจ้งเตือนสถานะ
const snackbar = ref({
  show: false,
  text: "",
  color: "success",
});

// ฟังก์ชันตรวจสอบฟิลด์ที่ต้องกรอก
const required = (value) => !!value || "จำเป็นต้องกรอก";

// ตรวจสอบรูปแบบอีเมล
const emailRule = (value) => {
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return pattern.test(value) || "อีเมลไม่ถูกต้อง";
};

// ตรวจสอบรหัสผ่านตรงกัน
const passwordMatch = (value) =>
  value === record.value.password || "รหัสผ่านไม่ตรงกัน";

// ตรวจสอบว่าแบบฟอร์มผ่าน validation หรือไม่
const isFormValid = computed(() => {
  const baseValid = record.value.user_name && record.value.email;

  if (isEditing.value) {
    // ถ้าแก้ไข → ถ้ากรอกรหัสผ่านใหม่ ต้องตรงกับ confirmPassword
    if (record.value.password || record.value.confirmPassword) {
      return (
        baseValid &&
        record.value.password &&
        record.value.confirmPassword &&
        record.value.password === record.value.confirmPassword
      );
    }
    return baseValid; // ไม่กรอกรหัสผ่านใหม่ → ผ่านได้
  } else {
    // เพิ่ม → ต้องกรอกครบ
    return (
      baseValid &&
      record.value.password &&
      record.value.confirmPassword &&
      record.value.password === record.value.confirmPassword
    );
  }
});

// ฟังก์ชันแปลงวันที่ให้อ่านง่ายแบบไทย
const formatDate = (dateString) => {
  if (!dateString) return "-";
  const date = new Date(dateString);
  return date.toLocaleDateString("th-TH", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};

// แสดง snackbar แจ้งเตือน
const showSnackbar = (message, type = "success") => {
  snackbar.value.text = message;
  snackbar.value.color = type;
  snackbar.value.show = true;
};

// เมื่อ component โหลดขึ้นมา
onMounted(() => {
  // ตรวจสอบว่ามี token หรือไม่ ถ้าไม่มีให้ไปหน้า login
  const token = localStorage.getItem("access_token");
  if (!token) {
    router.push("/login");
  }
  // โหลดข้อมูลผู้ใช้จาก API
  fetchUsers();
});

// ดึงข้อมูลผู้ใช้จาก API
const fetchUsers = async () => {
  try {
    const token = localStorage.getItem("access_token");
    // console.log("API token:", token);
    const response = await axios.get(`${API_BASE_URL}/user`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    // console.log("API Response:", response.data.users);
    users.value = response.data.users;
  } catch (error) {
    console.error("Error fetching users:", error);
    showSnackbar("เกิดข้อผิดพลาดในการดึงข้อมูลผู้ใช้", "error");

    return router.push("/login");
    
  }
};

// เตรียมเปิดฟอร์มเพิ่มข้อมูล
function add() {
  isEditing.value = false;
  record.value = { ...DEFAULT_RECORD };
  dialog.value = true;
}

// เตรียมเปิดฟอร์มแก้ไขข้อมูล โดยดึงข้อมูลผู้ใช้ตาม id
function edit(id) {
  isEditing.value = true;
  const found = users.value.find((user) => user.user_id === id);
  if (found) {
    const password = ""; // หรือจะใส่ค่าจาก found.password ก็ได้ (ถ้าจำเป็น)
    record.value = {
      ...DEFAULT_RECORD,
      ...found,
      password,
      confirmPassword: password,
    };
    dialog.value = true;
  }
}

// เปิด dialog ยืนยันลบ พร้อมเก็บ id ที่ต้องการลบ
function confirmRemove(id) {
  deleteId.value = id;
  confirmDeleteDialog.value = true;
}

// ลบผู้ใช้จริงๆ หลังยืนยัน
async function confirmDelete() {
  try {
    const token = localStorage.getItem("access_token");
    await axios.delete(`${API_BASE_URL}/user/delete/${deleteId.value}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    // ลบ user ออกจาก array ทันที
    users.value = users.value.filter((user) => user.user_id !== deleteId.value);
    showSnackbar("ลบผู้ใช้สำเร็จ!", "error");
  } catch (error) {
    showSnackbar("เกิดข้อผิดพลาดในการลบผู้ใช้", "error");
    console.error("Error deleting user:", error);
  } finally {
    confirmDeleteDialog.value = false;
  }
}

// บันทึกข้อมูลผู้ใช้ (เพิ่มหรือแก้ไข)
async function save() {
  try {
    const token = localStorage.getItem("access_token");

    // เตรียมข้อมูล
    const payload = {
      user_name: record.value.user_name,
      email: record.value.email,
    };

    // เพิ่มเฉพาะตอนเพิ่ม หรือกรอก password ใหม่
    if (!isEditing.value || record.value.password) {
      payload.password = record.value.password;
    }

    const config = {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    };

    if (isEditing.value) {
      // console.log("payload before update:", payload);
      // แก้ไข
      await axios.put(
        `${API_BASE_URL}/user/update/${record.value.user_id}`, // ✅ URL ที่ถูกต้อง
        payload,
        config
      );
      showSnackbar("แก้ไขผู้ใช้สำเร็จ!", "success");
    } else {
      // เพิ่ม
      await axios.post(`${API_BASE_URL}/user/insert`, payload, config);
      showSnackbar("เพิ่มผู้ใช้สำเร็จ!", "success");
    }

    dialog.value = false;
    fetchUsers(); // โหลดข้อมูลใหม่
  } catch (error) {
    // Token หมดอายุ
    if (error.response?.status === 401) {
      showSnackbar("Session หมดอายุ กรุณาเข้าสู่ระบบใหม่", "error");
      localStorage.removeItem("access_token");
      window.location.href = "/login";
      return;
    }

    // ⚠️ แสดงข้อความจาก backend (เช่น "Username already exists")
    if (error.response) {
      const serverMessage =
        error.response.data?.error ||
        error.response.data?.message ||
        "เกิดข้อผิดพลาดในการบันทึกข้อมูล";
      showSnackbar(serverMessage, "error");

      console.error("❌ Error saving user:", {
        status: error.response.status,
        message: serverMessage,
        data: error.response.data,
      });
    } else {
      showSnackbar("เกิดข้อผิดพลาดที่ระบบเครือข่าย", "error");
      console.error("❌ Network error:", error.message);
    }
  }
}

// ฟังก์ชันปุ่มกลับไปหน้าหลัก
const goBack = () => {
  router.push("/home");
};

// กำหนดหัวตาราง
const headers = [
  { title: "ลำดับ", key: "num", sortable: false },
  { title: "ชื่อผู้ใช้", key: "user_name" },
  { title: "อีเมล", key: "email" },
  { title: "วันที่อัปเดต", key: "updated_date" },
  { title: "แก้ไข", key: "edit", align: "center", sortable: false },
  { title: "ลบ", key: "del", align: "center", sortable: false },
];
</script>

<style scoped></style>
