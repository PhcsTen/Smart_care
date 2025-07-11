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
          <v-btn color="success" @click="addStudent">
            <v-icon start>mdi-account-school-outline</v-icon>
            เพิ่มข้อมูลนักเรียน
          </v-btn>
        </v-col>
      </v-row>

      <div style="height: 24px"></div>

      <v-sheet rounded>
        <v-data-table :headers="headers" :items="students" :items-per-page="10" :search="search"
          class="custom-table custom-footer">
          <template v-slot:top>
            <v-toolbar flat class="bg-success text-white">
              <v-toolbar-title>
                <v-icon icon="mdi-account-school-outline" size="x-small" class="me-2" color="white" />
                ตารางข้อมูลนักเรียน
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
              <td style="color: black">{{ item.student_code }}</td>
              <td style="color: black">{{ item.full_name }}</td>
              <td style="color: black">{{ item.nickname }}</td>
              <td style="color: black">{{ item.gender }}</td>
              <td style="color: black">{{ item.birth_date }}</td>
              <td style="color: black">{{ item.blood_group }}</td>
              <td style="color: black">{{ item.bmi }}</td>
              <td class="text-center">
                <v-avatar color="yellow-darken-2" size="32" class="elevation-1" style="cursor: pointer"
                  @click="editStudent(item)">
                  <v-icon color="white" icon="mdi-pencil" size="20" />
                </v-avatar>
              </td>
              <td class="text-center">
                <v-avatar color="red-darken-1" size="32" class="elevation-1" style="cursor: pointer"
                  @click="confirmRemove(item.student_id)">
                  <v-icon color="white" icon="mdi-delete" size="20" />
                </v-avatar>
              </td>
            </tr>
          </template>
        </v-data-table>
      </v-sheet>
    </v-container>

    <!-- Dialog เพิ่ม/แก้ไขนักเรียน -->
    <v-dialog v-model="dialog" persistent max-width="850">
      <v-card class="dialog-popup" style="background-color: #ffffff; color: black">
        <v-toolbar flat :color="isEditing ? 'warning' : 'success'">
          <v-card-title class="dialog-title text-white">
            {{ isEditing ? "แก้ไขข้อมูลนักเรียน" : "เพิ่มข้อมูลนักเรียน" }}
          </v-card-title>
        </v-toolbar>

        <v-card-text :class="isEditing ? 'card-text-warning' : 'card-text-success'">
          <v-row>
            <v-col cols="12" sm="4">
              <v-text-field v-model="record.student_code" label="รหัสนักเรียน" variant="outlined" />
            </v-col>
            <v-col cols="12" sm="4">
              <v-select v-model="record.prefix_name" :items="['เด็กชาย', 'เด็กหญิง', 'นาย', 'นางสาว']" label="คำนำหน้า"
                variant="outlined" />
            </v-col>
            <v-col cols="12" sm="4">
              <v-text-field v-model="record.first_name" label="ชื่อ" variant="outlined" />
            </v-col>
            <v-col cols="12" sm="4">
              <v-text-field v-model="record.last_name" label="นามสกุล" variant="outlined" />
            </v-col>
            <v-col cols="12" sm="4">
              <v-text-field v-model="record.nickname" label="ชื่อเล่น" variant="outlined" />
            </v-col>
            <v-col cols="12" sm="4">
              <v-select v-model="record.gender" :items="['ชาย', 'หญิง']" label="เพศ" variant="outlined" />
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field v-model="record.birth_date" label="วันเกิด" type="date" variant="outlined" />
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field v-model="record.blood_group" label="กรุ๊ปเลือด" variant="outlined" />
            </v-col>
          </v-row>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions class="justify-end">
          <v-btn color="red-darken-1" variant="flat" @click="dialog = false">ยกเลิก</v-btn>
          <v-btn color="green-darken-1" variant="flat" class="text-white ml-2" :disabled="!isFormValid"
            @click="saveStudent">บันทึก</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-main>
</template>

<script setup>
import { ref, shallowRef, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from "@/utils/axios"; // ใช้ instance แทน
import AppBar from '@/views/appbar/AppBar.vue';
import { API_BASE_URL } from '@/assets/config';

const dialog = ref(false);
const isEditing = shallowRef(false);
const drawer = ref(true);
const router = useRouter();
const search = ref('');
const students = ref([]);

const headers = [
  { title: 'ลำดับ', key: 'num' },
  { title: 'รหัสนักเรียน', key: 'student_code' },
  { title: 'ชื่อ-นามสกุล', key: 'full_name' },
  { title: 'ชื่อเล่น', key: 'nickname' },
  { title: 'เพศ', key: 'gender' },
  { title: 'วันเกิด', key: 'birth_date' },
  { title: 'หมู่เลือด', key: 'blood_group' },
  { title: 'BMI', key: 'bmi' },
  { title: 'แก้ไข', key: 'edit', align: 'center' },
  { title: 'ลบ', key: 'delete', align: 'center' },
];

const record = ref({
  student_id: null,
  student_code: '',
  prefix_name: '',
  first_name: '',
  last_name: '',
  nickname: '',
  gender: '',
  birth_date: '',
  blood_group: '',
  bmi: '',
});

const isFormValid = computed(() => {
  const r = record.value;
  return r.student_code && r.prefix_name && r.first_name && r.last_name;
});

const fetchStudents = async () => {
  try {
    const token = localStorage.getItem('access_token');
    const response = await axios.get(`${API_BASE_URL}/students`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    students.value = response.data.students || [];
  } catch (error) {
    console.error('ไม่สามารถโหลดข้อมูลนักเรียนได้:', error);
  }
};

onMounted(() => {
  fetchStudents();
});

const goBack = () => router.push('/home');

const addStudent = () => {
  isEditing.value = false;
  record.value = {
    student_id: null,
    student_code: '',
    prefix_name: '',
    first_name: '',
    last_name: '',
    nickname: '',
    gender: '',
    birth_date: '',
    blood_group: '',
    bmi: '',
  };
  dialog.value = true;
};

const editStudent = (student) => {
  isEditing.value = true;
  record.value = { ...student };
  dialog.value = true;
};

const confirmRemove = (id) => {
  if (confirm('คุณแน่ใจหรือไม่ว่าต้องการลบข้อมูลนี้?')) {
    deleteStudent(id);
  }
};

const deleteStudent = async (id) => {
  try {
    const token = localStorage.getItem('access_token');
    await axios.delete(`${API_BASE_URL}/student/delete/${id}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    await fetchStudents();
  } catch (error) {
    console.error('ลบข้อมูลไม่สำเร็จ:', error);
  }
};

const saveStudent = async () => {
  const token = localStorage.getItem('access_token');
  const config = { headers: { Authorization: `Bearer ${token}` } };
  const payload = { ...record.value };

  try {
    if (isEditing.value) {
      await axios.put(`${API_BASE_URL}/student/update/${record.value.student_id}`, payload, config);
    } else {
      await axios.post(`${API_BASE_URL}/student/insert`, payload, config);
    }
    dialog.value = false;
    await fetchStudents();
  } catch (error) {
    console.error('เกิดข้อผิดพลาดในการบันทึก:', error);
  }
};
</script>
