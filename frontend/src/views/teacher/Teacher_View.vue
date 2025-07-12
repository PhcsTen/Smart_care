<template>
  <!-- App Bar ด้านบน -->
  <AppBar @toggle-drawer="drawer = !drawer" />
  <v-main>
    <v-container>
      <!-- ปุ่มควบคุม -->
      <v-row class="align-center">
        <v-col cols="auto" class="pa-0">
          <v-btn color="red" @click="goBack" class="btn-back">
            <v-icon start>mdi-arrow-left</v-icon> กลับ
          </v-btn>
        </v-col>
        <v-col cols="auto" class="pa-0 ml-3">
          <v-btn color="success" @click="toggleTeacher">
            <v-icon start>mdi-account-badge-outline</v-icon> เพิ่มข้อมูลครู
          </v-btn>
        </v-col>
      </v-row>

      <div style="height: 24px"></div>

      <!-- ตารางข้อมูลครู -->
      <v-sheet rounded>
        <v-data-table
          :headers="headers"
          :items="teachers"
          :items-per-page="10"
          :search="search"
          class="custom-table custom-footer"
        >
          <template v-slot:top>
            <v-toolbar flat class="bg-success text-white">
              <v-toolbar-title>
                <v-icon
                  icon="mdi-account-badge-outline"
                  size="x-small"
                  class="me-2"
                  color="white"
                />
                ตารางข้อมูลครู
              </v-toolbar-title>
              <v-spacer></v-spacer>
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

          <template v-slot:item="{ item, index }">
            <tr
              :style="{
                backgroundColor: index % 2 === 0 ? '#e8f5e9' : '#ffffff',
              }"
            >
              <td style="color: black">{{ index + 1 }}</td>
              <td style="color: black">{{ item.full_name }}</td>
              <td style="color: black">{{ item.email }}</td>
              <td style="color: black">{{ item.phone_number || "-" }}</td>
              <td style="color: black">{{ item.school_name || "-" }}</td>
              <td class="text-center">
                <v-avatar
                  color="yellow darken-2"
                  size="32"
                  class="elevation-1"
                  style="cursor: pointer"
                  @click="editTeacher(item)"
                >
                  <v-icon color="white" icon="mdi-pencil" size="20" />
                </v-avatar>
              </td>
              <td class="text-center">
                <v-avatar
                  color="red darken-1"
                  size="32"
                  class="elevation-1"
                  style="cursor: pointer"
                  @click="confirmRemove(item.teacher_id)"
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
          >คุณต้องการครูใช่หรือไม่?</v-card-text
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

    <!-- Dialog เพิ่ม/แก้ไข -->
    <v-dialog v-model="dialog" persistent max-width="850">
      <v-card style="background-color: #ffffff; color: black">
        <v-toolbar flat :color="isEditing ? 'warning' : 'success'">
          <v-card-title class="text-white">
            {{ isEditing ? "แก้ไขข้อมูลครู" : "เพิ่มข้อมูลครู" }}
          </v-card-title>
        </v-toolbar>

        <v-card-text>
          <v-row>
            <v-col cols="12" sm="4">
              <v-select
                v-model="record.prefix_name"
                :items="['นาย', 'นาง', 'นางสาว']"
                label="คำนำหน้า"
                variant="outlined"
                color="success"
                :rules="[required]"
              />
            </v-col>
            <v-col cols="12" sm="8"></v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="record.first_name"
                label="ชื่อ"
                variant="outlined"
                color="success"
                :rules="[required]"
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="record.last_name"
                label="นามสกุล"
                variant="outlined"
                color="success"
                :rules="[required]"
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="record.email"
                label="อีเมล"
                variant="outlined"
                color="success"
                type="email"
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="record.phone_number"
                label="เบอร์โทรศัพท์"
                variant="outlined"
                color="success"
                type="tel"
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-select
                v-model="record.school_id"
                :items="schools"
                item-title="school_name"
                item-value="school_id"
                label="โรงเรียน"
                variant="outlined"
                color="success"
                :rules="[required]"
              />
            </v-col>
          </v-row>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions class="justify-end">
          <v-btn color="red darken-1" variant="flat" @click="dialog = false"
            >ยกเลิก</v-btn
          >
          <v-btn
            color="green darken-1"
            variant="flat"
            class="text-white ml-2"
            :disabled="!isTeacherFormValid"
            @click="save"
            >บันทึก</v-btn
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
  </v-main>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "@/utils/axios"; // ใช้ instance แทน
import AppBar from "@/views/appbar/AppBar.vue";
import { API_BASE_URL } from "@/assets/config";

// Router
const router = useRouter();

// UI
const drawer = ref(true);
const dialog = ref(false);
const isEditing = ref(false);
const search = ref("");

// Data
const schools = ref([]);
const teachers = ref([]);

// Snackbar แจ้งเตือนสถานะ
const snackbar = ref({
  show: false,
  text: "",
  color: "success",
});

// ตัวแปรควบคุม Dialog ยืนยันลบ และเก็บ id ที่จะลบ
const confirmDeleteDialog = ref(false);
const deleteId = ref(null);

// Record form
const record = ref({
  teacher_id: null,
  prefix_name: "",
  first_name: "",
  last_name: "",
  email: "",
  phone_number: "",
  school_id: null,
});

// แสดง snackbar แจ้งเตือน
const showSnackbar = (message, type = "success") => {
  snackbar.value.text = message;
  snackbar.value.color = type;
  snackbar.value.show = true;
};

// Table headers
const headers = [
  { title: "ลำดับ", key: "index" },
  { title: "ชื่อ-สกุล", key: "full_name" }, // ใช้ key นี้กับ item.full_name
  { title: "อีเมล", key: "email" },
  { title: "โทรศัพท์", key: "phone_number" },
  { title: "โรงเรียน", key: "school_name" },
  { title: "แก้ไข", key: "edit", align: "center" },
  { title: "ลบ", key: "delete", align: "center" },
];

// Validation
const required = (v) => !!v || "จำเป็นต้องกรอก";
const isTeacherFormValid = computed(() => {
  const r = record.value;
  return r.prefix_name && r.first_name && r.last_name && r.school_id;
});

// โหลดข้อมูลครู พร้อมสร้าง full_name สำหรับการแสดงผลและค้นหา
const fetchTeachers = async () => {
  try {
    const token = localStorage.getItem("access_token");
    const response = await axios.get(`${API_BASE_URL}/teachers_all`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    // เช็กให้แน่ใจว่ามี .teachers
    const data = response.data.teachers || [];
    //console.log("response.data.teachers:", response.data.teachers);

    teachers.value = data.map((t) => ({
      ...t,
      full_name: `${t.prefix_name || ""}${t.first_name || ""} ${
        t.last_name || ""
      }`,
    }));
  } catch (error) {
    console.error("โหลดข้อมูลครูล้มเหลว", error);
  }
};

const fetchSchools = async () => {
  try {
    const token = localStorage.getItem("access_token");
    const response = await axios.get(`${API_BASE_URL}/school`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    schools.value = response.data.schools || [];
  } catch (error) {
    console.error("โหลดข้อมูลโรงเรียนล้มเหลว", error);
  }
};

const toggleTeacher = () => {
  isEditing.value = false;
  record.value = {
    teacher_id: null,
    prefix_name: "",
    first_name: "",
    last_name: "",
    email: "",
    phone_number: "",
    school_id: null,
  };
  dialog.value = true;
};

const editTeacher = (teacher) => {
  isEditing.value = true;
  record.value = { ...teacher };
  dialog.value = true;
};

const confirmRemove = (id) => {
  deleteId.value = id;
  confirmDeleteDialog.value = true;
};

// แก้ไขเมธอด confirmDelete ให้ถูกต้อง
async function confirmDelete() {
  try {
    const token = localStorage.getItem("access_token");
    await axios.delete(`${API_BASE_URL}/teacher/delete/${deleteId.value}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    // แก้ไขจาก teacher.value เป็น teachers.value
    teachers.value = teachers.value.filter((teacher) => teacher.teacher_id !== deleteId.value);
    showSnackbar("ลบครูสำเร็จ!", "success"); // เปลี่ยนจาก "error" เป็น "success"
  } catch (error) {
    showSnackbar("เกิดข้อผิดพลาดในการลบครู", "error");
    console.error("Error deleting teacher:", error);
  } finally {
    confirmDeleteDialog.value = false;
  }
}
const save = async () => {
  try {
    const token = localStorage.getItem("access_token");

    // เตรียมข้อมูล
    const payload = {
      teacher_id: record.value.teacher_id,
      prefix_name: record.value.prefix_name,
      first_name: record.value.first_name,
      last_name: record.value.last_name,
      email: record.value.email,
      phone_number: record.value.phone_number,
      school_id: record.value.school_id,
    };
    const config = {
      headers: {
        "Content-Type": "application/json", // ✅ สำคัญ
        Authorization: `Bearer ${token}`,
      },
    };
    console.log("token :", config);
    console.log("payload :", payload);

    if (isEditing.value) {
      await axios.put(
        `${API_BASE_URL}/teacher/update/${payload.teacher_id}`,
        payload,
        config
      );
    } else {
      await axios.post(`${API_BASE_URL}/teacher/insert`, payload, config);
      showSnackbar("เพิ่มผู้ใช้สำเร็จ!", "success");
    }

    dialog.value = false;
    fetchTeachers(); // โหลดข้อมูลใหม่
  } catch (error) {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      router.push("/login");
    } else {
      console.error("บันทึกข้อมูลไม่สำเร็จ", error);
    }
  }
};

onMounted(() => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    router.push("/login");
    return;
  }
  fetchSchools();
  fetchTeachers();
});

const goBack = () => {
  router.push("/home");
};
</script>
