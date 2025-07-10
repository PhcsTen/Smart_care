<template>
  <AppBar @toggle-drawer="drawer = !drawer" />
  <v-main>
    <v-container>
      <v-row class="align-center">
        <v-col cols="auto" class="pa-0">
          <v-btn color="red" @click="goBack" class="btn-back">
            <v-icon start>mdi-arrow-left</v-icon>
            กลับ
          </v-btn>
        </v-col>
        <v-col cols="auto" class="pa-0 ml-3">
          <v-btn color="success" @click="addTeacher">
            <v-icon start>mdi-account-badge-outline</v-icon>
            เพิ่มข้อมูลครู
          </v-btn>
        </v-col>
      </v-row>

      <div style="height: 24px"></div>

      <v-sheet rounded>
        <v-data-table :headers="headers" :items="teachers" :items-per-page="10" :search="search"
          class="custom-table custom-footer">
          <template v-slot:top>
            <v-toolbar flat class="bg-success text-white">
              <v-toolbar-title>
                <v-icon icon="mdi-account-badge-outline" size="x-small" class="me-2" color="white" />
                ตารางข้อมูลครู
              </v-toolbar-title>
              <v-spacer></v-spacer>
              <v-text-field v-model="search" label="ค้นหา" clearable variant="outlined" hide-details density="compact"
                style="max-width: 300px" />
            </v-toolbar>
          </template>

          <template v-slot:header="{ headers }">
            <tr>
              <th v-for="header in headers" :key="header.key" style="background-color: #43a047; color: white">
                {{ header.title }}
              </th>
            </tr>
          </template>

          <template v-slot:item="{ item, index }">
            <tr :style="{ backgroundColor: index % 2 === 0 ? '#e8f5e9' : '#ffffff' }">
              <td style="color: black">{{ index + 1 }}</td>
              <td style="color: black">{{ item.prefix_name }}{{ item.first_name }} {{ item.last_name }}</td>
              <td style="color: black">{{ item.teacher_position || '-' }}</td>
              <td style="color: black">{{ item.email }}</td>
              <td style="color: black">{{ item.phone_number || '-' }}</td>
              <td class="text-center">
                <v-avatar color="yellow darken-2" size="32" class="elevation-1" style="cursor: pointer"
                  @click="editTeacher(item)">
                  <v-icon color="white" icon="mdi-pencil" size="20" />
                </v-avatar>
              </td>
              <td class="text-center">
                <v-avatar color="red darken-1" size="32" class="elevation-1" style="cursor: pointer"
                  @click="confirmRemove(item.teacher_id)">
                  <v-icon color="white" icon="mdi-delete" size="20" />
                </v-avatar>
              </td>
            </tr>
          </template>
        </v-data-table>
      </v-sheet>
    </v-container>

    <!-- Dialog เพิ่ม/แก้ไข -->
    <v-dialog v-model="dialog" persistent max-width="850">
      <v-card style="background-color: #ffffff; color: black">
        <v-toolbar flat :color="isEditing ? 'warning' : 'success'">
          <v-card-title class="text-white">
            {{ isEditing ? "แก้ไขข้อมูลครู" : "เพิ่มข้อมูลครู" }}
          </v-card-title>
        </v-toolbar>

        <v-card-text :class="isEditing ? 'card-text-warning' : 'card-text-success'">
          <v-row>
            <v-col cols="12" sm="4">
              <v-select v-model="record.prefix_name" :items="['นาย', 'นาง', 'นางสาว']" label="คำนำหน้า"
                variant="outlined" color="success" :rules="[required]" />
            </v-col>
            <v-col cols="12" sm="8"></v-col>
            <v-col cols="12" sm="6">
              <v-text-field v-model="record.first_name" label="ชื่อ" variant="outlined" color="success" :rules="[required]" />
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field v-model="record.last_name" label="นามสกุล" variant="outlined" color="success" :rules="[required]" />
            </v-col>

            <v-col cols="12" sm="6">
              <v-text-field v-model="record.email" label="อีเมล" variant="outlined" color="success" type="email" />
            </v-col>

            <v-col cols="12" sm="6">
              <v-text-field v-model="record.phone_number" label="เบอร์โทรศัพท์" variant="outlined" color="success" type="tel" />
            </v-col>

            <v-col cols="12" sm="12">
              <v-select v-model="record.school_id" :items="schools" item-title="school_name" item-value="school_id"
                label="โรงเรียน" variant="outlined" color="success" :rules="[required]" />
            </v-col>
          </v-row>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions class="justify-end">
          <v-btn color="red darken-1" variant="flat" @click="dialog = false">ยกเลิก</v-btn>
          <v-btn color="green darken-1" variant="flat" class="text-white ml-2" :disabled="!isTeacherFormValid" @click="saveTeacher">
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

const dialog = ref(false);
const isEditing = shallowRef(false);

const drawer = ref(true);
const router = useRouter();
const search = ref("");
const teachers = ref([]);
const schools = ref([]);

const snackbar = ref({ show: false, text: "", color: "success" });

const headers = [
  { title: "ลำดับ", key: "index" },
  { title: "ชื่อ-สกุล", key: "full_name" },
  { title: "อีเมล", key: "email" },
  { title: "โทรศัพท์", key: "phone_number" },
  { title: "แก้ไข", key: "edit", align: "center" },
  { title: "ลบ", key: "delete", align: "center" },
];

const record = ref({
  teacher_id: null,
  prefix_name: "",
  first_name: "",
  last_name: "",
  email: "",
  phone_number: "",
  school_id: null,
});

const required = (v) => !!v || "จำเป็นต้องกรอก";

const showSnackbar = (text, color = "success") => {
  snackbar.value = { show: true, text, color };
};

const isTeacherFormValid = computed(() => {
  const r = record.value;
  return r.prefix_name && r.first_name && r.last_name && r.school_id;
});

const fetchTeachers = async () => {
  try {
    const token = localStorage.getItem("access_token");
    const response = await axios.get(`${API_BASE_URL}/teachers_all`, {
      headers: { Authorization: `Bearer ${token}` },
      withCredentials: true,
    });
    teachers.value = response.data;
  } catch (error) {
    console.error("Error fetching teachers:", error);
    showSnackbar("ไม่สามารถโหลดข้อมูลครูได้", "error");
  }
};

// const fetchSchools = async () => {
//   try {
//     const token = localStorage.getItem("access_token");
//     const response = await axios.get(`${API_BASE_URL}/schools`, {
//       headers: { Authorization: `Bearer ${token}` },
//       withCredentials: true,
//     });
//     schools.value = response.data;
//   } catch (error) {
//     console.error("Error fetching schools:", error);
//   }
// };

onMounted(() => {
  fetchTeachers();
  // fetchSchools();
});

const goBack = () => {
  router.push("/home");
};

const addTeacher = () => {
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
  if (confirm("คุณแน่ใจหรือไม่ว่าต้องการลบข้อมูลนี้?")) {
    deleteTeacher(id);
  }
};

const deleteTeacher = async (id) => {
  try {
    const token = localStorage.getItem("access_token");
    await axios.delete(`${API_BASE_URL}/teacher/delete/${id}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    await fetchTeachers();
  } catch (error) {
    console.error("ลบข้อมูลไม่สำเร็จ:", error);
  }
};

const saveTeacher = async () => {
  const token = localStorage.getItem("access_token");
  const config = { headers: { Authorization: `Bearer ${token}` } };
  const payload = { ...record.value };

  try {
    if (isEditing.value) {
      await axios.put(`${API_BASE_URL}/teacher/update/${record.value.teacher_id}`, payload, config);
    } else {
      await axios.post(`${API_BASE_URL}/teacher/insert`, payload, config);
    }
    dialog.value = false;
    await fetchTeachers();
  } catch (error) {
    console.error("เกิดข้อผิดพลาดในการบันทึก:", error);
  }
};
</script>
