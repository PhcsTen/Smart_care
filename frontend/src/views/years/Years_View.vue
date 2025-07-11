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
            <v-icon start>mdi-calendar-clock</v-icon>
            เพิ่มข้อมูลปีการศึกษา
          </v-btn>
        </v-col>
      </v-row>

      <div style="height: 24px"></div>
      <!-- เว้นวรรค -->

      <!-- ตารางข้อมูลสมาชิก -->
      <v-sheet rounded>
        <v-data-table :headers="headers" :items="years" :items-per-page="10" :search="search"
          class="custom-table custom-footer">
          <!-- toolbar ด้านบนของตาราง มีชื่อและช่องค้นหา -->
          <template v-slot:top>
            <v-toolbar flat class="bg-success text-white">
              <v-toolbar-title>
                <v-icon icon="mdi-calendar-clock" size="x-small" class="me-2" color="white" />
                ตารางข้อมูลปีการศึกษา
              </v-toolbar-title>
              <v-spacer></v-spacer>
              <!-- ช่องค้นหา -->
              <v-text-field v-model="search" label="ค้นหา" clearable variant="outlined" hide-details density="compact"
                style="max-width: 300px" />
            </v-toolbar>
          </template>

          <!-- กำหนด header ตารางเอง (สีพื้นหลังและตัวอักษร) -->
          <template v-slot:header="{ headers }">
            <tr>
              <th v-for="header in headers" :key="header.key" style="background-color: #43a047; color: white">
                {{ header.title }}
              </th>
            </tr>
          </template>

          <!-- กำหนดแต่ละแถวข้อมูล -->
          <template v-slot:item="{ item, index }">
            <tr :style="{
              backgroundColor: index % 2 === 0 ? '#e8f5e9' : '#ffffff',
            }">
              <td style="color: black">{{ index + 1 }}</td>
              <!-- ลำดับ -->
              <td style="color: black">{{ item.year_name }}</td>
              <!-- ปีการศึกษา -->
              <td style="color: black">
                {{ formatThaiDate(item.start_date) }}
              </td>
              <!-- วันที่เริ่ม -->
              <td style="color: black">{{ formatThaiDate(item.end_date) }}</td>
              <!-- วันที่สิ้นสุด -->
              <!-- ปุ่มแก้ไข -->
              <!-- @click="() => { console.log(item); edit(item.year_id) }" -->
              <td class="text-center">
                <v-avatar color="yellow-darken-2" size="32" class="elevation-1" style="cursor: pointer"
                  @click="edit(item.academic_year_id)">
                  <v-icon color="white" icon="mdi-pencil" size="20" />
                </v-avatar>
              </td>
              <!-- ปุ่มลบ -->
              <td class="text-center">
                <v-avatar color="red-darken-1" size="32" class="elevation-1" style="cursor: pointer"
                  @click="confirmRemove(item.academic_year_id)">
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
        <v-card-title class="text-h6 confirm-delete-title">ยืนยันการลบ</v-card-title>
        <v-card-text class="confirm-delete-text">คุณต้องการลบผู้ใช้นี้ใช่หรือไม่?</v-card-text>
        <v-card-actions class="confirm-delete-actions">
          <v-spacer />
          <!-- ปุ่มยกเลิก -->
          <v-btn color="red-darken-1" variant="flat" class="text-white"
            @click="confirmDeleteDialog = false">ยกเลิก</v-btn>
          <!-- ปุ่มยืนยันลบ -->
          <v-btn color="green-darken-1" variant="flat" class="text-white" @click="confirmDelete">ลบ</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar แจ้งเตือนสถานะ -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="1000" location="center"
      class="snackbar-fullscreen" transition="slide-y-transition">
      <v-icon icon="mdi-alert-circle-outline" class="mr-2" size="large" color="white" />
      {{ snackbar.text }}
    </v-snackbar>

    <!-- Dialog สำหรับเพิ่ม/แก้ไขข้อมูลผู้ใช้ -->
    <v-dialog v-model="dialog" persistent max-width="850">
      <v-card class="dialog-popup" style="background-color: #ffffff; color: black">
        <v-toolbar flat :color="isEditing ? 'warning' : 'success'">
          <v-card-title class="dialog-title text-white">
            {{ isEditing ? "แก้ไขข้อมูลปีการศึกษา" : "เพิ่มข้อมูลปีการศึกษา" }}
          </v-card-title>
        </v-toolbar>

        <v-card-text :class="isEditing ? 'card-text-warning' : 'card-text-success'">
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field v-model="record.year_name" label="ปีการศึกษา" type="number" variant="outlined"
                color="success" class="custom-input" :rules="[required]" hide-details="auto" />
            </v-col>
            <v-col cols="12" md="6"></v-col>
            <!-- วันที่เริ่มต้น -->
            <v-col cols="12" md="6">
              <v-menu v-model="startMenu" :close-on-content-click="false" transition="scale-transition" offset-y
                max-width="220" min-width="auto">
                <template #activator="{ props }">
                  <v-text-field v-model="formattedStartDate" label="วันที่เริ่มต้น" readonly v-bind="props"
                    variant="outlined" color="success" :rules="[required]" hide-details="auto" />
                </template>
                <v-card>
                  <v-date-picker v-model="startDate" />
                  <v-card-actions>
                    <v-spacer />
                    <v-btn text color="primary" @click="saveStartDate">ตกลง</v-btn>
                  </v-card-actions>
                </v-card>
              </v-menu>
            </v-col>

            <!-- วันที่สิ้นสุด -->
            <v-col cols="12" md="6">
              <v-menu v-model="endMenu" :close-on-content-click="false" transition="scale-transition" offset-y
                max-width="220" min-width="auto">
                <template #activator="{ props }">
                  <v-text-field v-model="formattedEndDate" label="วันที่สิ้นสุด" readonly v-bind="props"
                    variant="outlined" color="success" :rules="[required]" hide-details="auto" />
                </template>
                <v-card>
                  <v-date-picker v-model="endDate" />

                  <v-card-actions>
                    <v-spacer />
                    <v-btn text color="primary" @click="saveEndDate">ตกลง</v-btn>
                  </v-card-actions>
                </v-card>
              </v-menu>
            </v-col>
          </v-row>
        </v-card-text>

        <v-divider />

        <v-card-actions :class="[
          'd-flex justify-end',
          isEditing ? 'action-warning' : 'action-success',
        ]">
          <v-btn color="red-darken-1" variant="flat" class="text-white" @click="dialog = false">
            ยกเลิก
          </v-btn>
          <v-btn color="green-darken-1" variant="flat" class="text-white ml-2" @click="save" :disabled="!isFormValid">
            บันทึก
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-main>
</template>

<script setup>
import { ref, shallowRef, computed, watch, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "@/utils/axios"; // ใช้ instance แทน
import dayjs from "dayjs";
import "dayjs/locale/th";
import buddhistEra from "dayjs/plugin/buddhistEra";
import AppBar from "@/views/appbar/AppBar.vue";
import { API_BASE_URL } from "@/assets/config";
// import dayjs from "@/plugins/dayjs";

// ตัวแปรเวลา
dayjs.locale("th");
dayjs.extend(buddhistEra);

// ตัวแปรพื้นฐาน
const drawer = ref(true);
const router = useRouter();
// const menuItems = menuItemsData;

// const dialog = shallowRef(false);
const dialog = ref(false); // ✅ ไม่ใช้ shallowRef

const isEditing = shallowRef(false);
const search = ref("");
const confirmDeleteDialog = ref(false);
const deleteId = ref(null);

const formatThaiDate = (date) => {
  return dayjs(date).format("ddddที่ D MMMM BBBB");
};

const snackbar = ref({
  show: false,
  text: "",
  color: "success",
});

const DEFAULT_RECORD = {
  year_id: null,
  year_name: "",
  start_date: "",
  end_date: "",
};

const academicYears = ref([]);
const record = ref({ ...DEFAULT_RECORD });
const years = academicYears; // ให้ years = academicYears (ตรงกับตาราง)

const required = (value) => !!value || "จำเป็นต้องกรอก";

const isFormValid = computed(() => {
  return (
    !!record.value.year_name &&
    !!record.value.start_date &&
    !!record.value.end_date
  );
});

// วันที่และเวลา
const startMenu = ref(false);
const endMenu = ref(false);
const startDate = ref("");

const endDate = ref("");

// แสดงวันที่แบบฟอร์แมต
const formattedStartDate = computed(() => {
  return record.value.start_date
    ? dayjs(record.value.start_date).format("ddddที่ D MMMM BBBB")
    : "";
});

const formattedEndDate = computed(() => {
  return record.value.end_date
    ? dayjs(record.value.end_date).format("ddddที่ D MMMM BBBB")
    : "";
});

// sync startDate/startTime ➜ record.start_date
watch([startDate], () => {
  if (startDate.value) {
    const dateStr = dayjs(startDate.value).format("YYYY-MM-DD");
    record.value.start_date = `${dateStr}`;
  }
});

watch(endDate, () => {
  if (endDate.value) {
    const dateStr = dayjs(endDate.value).format("YYYY-MM-DD");
    record.value.end_date = `${dateStr}`;
  }
});

const showSnackbar = (text, color = "success") => {
  snackbar.value = { show: true, text, color };
};

onMounted(() => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    return router.push("/login");
  }
  fetchAcademicYears();
});

const fetchAcademicYears = async () => {
  try {
    const token = localStorage.getItem("access_token");

    // console.log("API token:", token);

    if (!token) {
      throw new Error("ไม่มี token");
    }

    const response = await axios.get(`${API_BASE_URL}/academic_years`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    // console.log("API Response:", response.data.academic_years);
    academicYears.value = response.data.academic_years || [];
  } catch (error) {
    showSnackbar("ดึงข้อมูลล้มเหลว", "error");
    console.error("Error details:", error.response || error.message || error);

    return router.push("/login");

  }
};

const add = () => {
  isEditing.value = false;
  record.value = { ...DEFAULT_RECORD };

  const now = dayjs();
  startDate.value = now.format("YYYY-MM-DD");
  endDate.value = now.add(1, "year").format("YYYY-MM-DD");

  record.value.start_date = `${startDate.value}`;
  record.value.end_date = `${endDate.value}`;
  dialog.value = true;
};

const edit = (id) => {
  isEditing.value = true;
  const found = academicYears.value.find((i) => i.academic_year_id === id); // ✅ แก้ตรงนี้
  if (found) {
    record.value = { ...DEFAULT_RECORD, ...found };

    if (record.value.start_date && record.value.start_date.includes("T")) {
      const [d] = record.value.start_date.split("T");
      startDate.value = d;
    }

    if (record.value.end_date && record.value.end_date.includes("T")) {
      const [d] = record.value.end_date.split("T");
      endDate.value = d;
    }

    dialog.value = true;
  }
};


const saveStartDate = () => {
  startMenu.value = false;
};

const saveEndDate = () => {
  endMenu.value = false;
};

const confirmRemove = (id) => {
  deleteId.value = id;
  confirmDeleteDialog.value = true;

  // console.log("ID:",id)
};

const confirmDelete = async () => {
  try {
    const token = localStorage.getItem("access_token");

    const response = await axios.delete(
      `${API_BASE_URL}/academic_year/delete/${deleteId.value}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );

    console.log("ลบสำเร็จ response:", response);

    // เช็ค status code อย่างปลอดภัย
    if (response.status === 200) {
      showSnackbar("ลบข้อมูลสำเร็จ", "success");

      // โหลดข้อมูลใหม่จาก server
      await fetchAcademicYears();
    } else {
      // ไม่ใช่ 200 ถือว่า fail
      throw new Error("Unexpected status code");
    }
  } catch (error) {
    console.error("❌ ลบข้อมูลไม่สำเร็จ:", error);
    showSnackbar("เกิดข้อผิดพลาดในการลบปีการศึกษา", "error");
  } finally {
    confirmDeleteDialog.value = false;
  }
};


const save = async () => {
  try {
    const token = localStorage.getItem("access_token");
    const payload = {
      year_name: record.value.year_name,
      start_date: record.value.start_date,
      end_date: record.value.end_date,
    };

    const config = {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    };

    // console.log("Updating year with id:", record.value.academic_year_id); // ต้องไม่ใช่ null หรือ undefined

    if (isEditing.value) {
      await axios.put(
        `${API_BASE_URL}/academic_year/update/${record.value.academic_year_id}`,
        payload,
        config
      );
      showSnackbar("แก้ไขข้อมูลสำเร็จ", "success");
    } else {
      await axios.post(`${API_BASE_URL}/academic_year/insert`, payload, config);
      showSnackbar("เพิ่มข้อมูลสำเร็จ", "success");
    }

    dialog.value = false;
    fetchAcademicYears();
  } catch (error) {
    if (error.response?.status === 401) {
      showSnackbar("Session หมดอายุ กรุณาเข้าสู่ระบบใหม่", "error");
      localStorage.removeItem("access_token");
      router.push("/login");
    } else {
      const message =
        error.response?.data?.message || "เกิดข้อผิดพลาดในการบันทึก";
      showSnackbar(message, "error");
    }
  }
};

const goBack = () => {
  router.push("/home");
};

const headers = [
  { title: "ลำดับ", key: "num", sortable: false },
  { title: "ปีการศึกษา", key: "year_name" },
  { title: "วันที่เริ่มต้น", key: "start_date" },
  { title: "วันที่สิ้นสุด", key: "end_date" },
  { title: "แก้ไข", key: "edit", align: "center", sortable: false },
  { title: "ลบ", key: "del", align: "center", sortable: false },
];
</script>

<style scoped></style>
