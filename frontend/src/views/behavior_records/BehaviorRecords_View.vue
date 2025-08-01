<template>
  <div>
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
            <v-btn color="success" @click="scanQR">
              <v-icon start>mdi-qrcode-scan</v-icon>
              Scan QR Code
            </v-btn>
          </v-col>
        </v-row>

        <div style="height: 24px"></div>

        <!-- ตารางรายชื่อนักเรียน ห้อง.... -->
        <v-sheet rounded>
          <v-data-table
            :headers="headers"
            :items="behaviorRecords"
            :items-per-page="10"
            :search="search"
            class="custom-table custom-footer"
          >
            <template v-slot:top>
              <v-toolbar flat class="bg-success text-white">
                <v-toolbar-title>
                  <v-icon
                    icon="mdi-clipboard-check-outline"
                    size="x-small"
                    class="me-2"
                    color="white"
                  />
                  ตารางข้อมูลบันทึกสังเกตพฤติกรรม
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
                <td style="color: black">{{ item.student_code }}</td>
                <td style="color: black">{{ item.student_fullname }}</td>
                <td style="color: black">{{ item.classroom_name }}</td>
                <td class="text-center">
                  <v-avatar
                    :color="item.behavior_id ? 'green' : 'black'"
                    size="32"
                    class="elevation-1"
                    style="cursor: pointer"
                    @click="addBehavior(item)"
                  >
                    <v-icon
                      v-if="true"
                      color="white"
                      icon="mdi-check-bold"
                      size="20"
                    />
                    <v-icon
                      v-else
                      color="black"
                      icon="mdi-check-bold"
                      size="20"
                    />
                  </v-avatar>
                </td>
                <td class="text-center">
                  <v-avatar
                    :color="item.behavior_id ? 'red darken-1' : 'grey'"
                    size="32"
                    class="elevation-1"
                    style="cursor: pointer"
                    @click="
                      item.behavior_id ? confirmRemove(item.behavior_id) : ''
                    "
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
          <v-card-title class="text-h6 confirm-delete-title">
            ยืนยันการลบ
          </v-card-title>
          <v-card-text class="confirm-delete-text">
            คุณต้องการลบใช่หรือไม่?
          </v-card-text>
          <v-card-actions class="confirm-delete-actions">
            <v-spacer />
            <!-- ปุ่มยกเลิก -->
            <v-btn
              color="red-darken-1"
              variant="flat"
              class="text-white"
              @click="confirmDeleteDialog = false"
            >
              ยกเลิก
            </v-btn>
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
      <v-dialog v-model="dialog" persistent max-width="850">
        <v-card style="background-color: #ffffff; color: black">
          <v-toolbar flat :color="isEditing ? 'warning' : 'success'">
            <v-card-title class="text-white">
              {{
                isEditing
                  ? "แก้ไขข้อมูลบันทึกสังเกตพฤติกรรม"
                  : "เพิ่มข้อมูลบันทึกสังเกตพฤติกรรม"
              }}
            </v-card-title>
          </v-toolbar>

          <!-- Start Dialog Add/Edit -->
          <v-card-text>
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="currentDateFormatted"
                  label="วันที่"
                  readonly
                  variant="outlined"
                  prepend-inner-icon="mdi-calendar"
                />
              </v-col>
              <v-col cols="12" sm="6"></v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="record.student_fullname"
                  label="ชื่อนักเรียน"
                  readonly
                  variant="outlined"
                  color="success"
                  :rules="[required]"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="record.school_name"
                  label="ศพด."
                  readonly
                  variant="outlined"
                  color="success"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="record.class_name"
                  label="ระดับชั้น"
                  readonly
                  variant="outlined"
                  color="success"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="record.classroom_name"
                  label="ห้อง"
                  readonly
                  variant="outlined"
                  color="success"
                />
              </v-col>
              <v-col cols="12" sm="12">
                <v-card variant="outlined" class="mx-auto" max-width="100%">
                  <v-card-title style="font-size: 1.1rem">
                    พฤติกรรม
                  </v-card-title>
                  <v-card-text>
                    <v-row>
                      <v-col
                        cols="12"
                        sm="2"
                        align-self="center"
                        style="font-size: 1rem"
                      >
                        การดื่มนม
                      </v-col>
                      <v-col cols="12" sm="8">
                        <v-btn-toggle
                          v-model="record.milk_status"
                          mandatory
                          divided
                          color="primary"
                          base-color="#e0e0e0"
                        >
                          <v-btn value="yes" style="font-size: 1rem">
                            ดื่ม
                          </v-btn>
                          <v-btn value="no" style="font-size: 1rem">
                            ไม่ดื่ม
                          </v-btn>
                        </v-btn-toggle>
                      </v-col>
                    </v-row>
                    <v-row>
                      <v-col
                        cols="12"
                        sm="2"
                        align-self="center"
                        style="font-size: 1rem"
                      >
                        อาหารกลางวัน
                      </v-col>
                      <v-col cols="12" sm="8">
                        <v-btn-toggle
                          v-model="record.lunch_status"
                          mandatory
                          divided
                          color="primary"
                          base-color="#e0e0e0"
                        >
                          <v-btn value="refill" style="font-size: 1rem">
                            เติม
                          </v-btn>
                          <v-btn value="clear" style="font-size: 1rem">
                            หมด
                          </v-btn>
                          <v-btn value="leftover" style="font-size: 1rem">
                            ไม่หมด
                          </v-btn>
                        </v-btn-toggle>
                      </v-col>
                    </v-row>
                    <v-row>
                      <v-col
                        cols="12"
                        sm="2"
                        align-self="center"
                        style="font-size: 1rem"
                      >
                        อาหารว่าง
                      </v-col>
                      <v-col cols="12" sm="8">
                        <v-btn-toggle
                          v-model="record.snack_status"
                          mandatory
                          divided
                          color="primary"
                          base-color="#e0e0e0"
                        >
                          <v-btn value="yes" style="font-size: 1rem">
                            ทาน
                          </v-btn>
                          <v-btn value="no" style="font-size: 1rem">
                            ไม่ทาน
                          </v-btn>
                        </v-btn-toggle>
                      </v-col>
                    </v-row>
                    <v-row>
                      <v-col
                        cols="12"
                        sm="2"
                        align-self="center"
                        style="font-size: 1rem"
                      >
                        แปรงฟัน
                      </v-col>
                      <v-col cols="12" sm="8">
                        <v-btn-toggle
                          v-model="record.brushing_status"
                          mandatory
                          divided
                          color="primary"
                          base-color="#e0e0e0"
                        >
                          <v-btn value="yes" style="font-size: 1rem">
                            แปรง
                          </v-btn>
                          <v-btn value="no" style="font-size: 1rem">
                            ไม่แปรง
                          </v-btn>
                        </v-btn-toggle>
                      </v-col>
                    </v-row>
                    <v-row>
                      <v-col
                        cols="12"
                        sm="2"
                        align-self="center"
                        style="font-size: 1rem"
                      >
                        พักผ่อน
                      </v-col>
                      <v-col cols="12" sm="8">
                        <v-btn-toggle
                          v-model="record.sleeping_status"
                          mandatory
                          divided
                          color="primary"
                          base-color="#e0e0e0"
                        >
                          <v-btn value="full" style="font-size: 1rem">
                            หลับนาน
                          </v-btn>
                          <v-btn value="some" style="font-size: 1rem">
                            หลับได้บ้าง
                          </v-btn>
                          <v-btn value="no" style="font-size: 1rem">
                            ไม่หลับ
                          </v-btn>
                        </v-btn-toggle>
                      </v-col>
                    </v-row>
                    <v-row>
                      <v-col
                        cols="12"
                        sm="2"
                        align-self="center"
                        style="font-size: 1rem"
                      >
                        การขับถ่าย
                      </v-col>
                      <v-col cols="12" sm="8">
                        <v-btn-toggle
                          v-model="record.toilet_status"
                          mandatory
                          divided
                          color="primary"
                          base-color="#e0e0e0"
                        >
                          <v-btn value="yes" style="font-size: 1rem">
                            ปกติ
                          </v-btn>
                          <v-btn value="no" style="font-size: 1rem">
                            ไม่ปกติ
                          </v-btn>
                        </v-btn-toggle>
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="record.notes"
                  label="หมายเหตุ"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-if="isEditing"
                  v-model="completed"
                  label="สถานะ"
                  readonly
                  variant="outlined"
                />
              </v-col>
              <!-- รูปภาพ -->
            </v-row>
          </v-card-text>
          <v-divider></v-divider>

          <v-card-actions class="justify-end">
            <v-btn color="red darken-1" variant="flat" @click="dialog = false">
              ยกเลิก
            </v-btn>
            <v-btn
              color="green darken-1"
              variant="flat"
              class="text-white ml-2"
              :disabled="!isBehaviorFormValid"
              @click="save"
            >
              บันทึก
            </v-btn>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "@/utils/axios";
import AppBar from "@/views/appbar/AppBar.vue";
import { API_BASE_URL } from "@/assets/config";

// Router
const router = useRouter();

// UI
const drawer = ref(true);
const dialog = ref(false);
const isEditing = ref(false);
const search = ref("");

const currentDateFormatted = ref("");

// Data
const behaviorRecords = ref([]);
const teacherId = ref("1"); // TODO
const completed = ref("บันทึกพฤติกรรมแล้ว");

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
  behavior_id: null,
  student_id: "",
  class_id: "",
  classroom_id: "",
  record_date: "",
  milk_status: "",
  lunch_status: "",
  snack_status: "",
  brushing_status: "",
  sleeping_status: "",
  toilet_status: "",
  notes: "",
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
  { title: "รหัสนักเรียน", key: "student_code" },
  { title: "ชื่อ-สกุล", key: "student_fullname" },
  { title: "ห้อง", key: "classroom_name" },
  { title: "เช็คชื่อ", key: "view", align: "center" },
  { title: "ลบ", key: "delete", align: "center" },
];

// Validation
const required = (v) => !!v || "จำเป็นต้องกรอก";
const isBehaviorFormValid = computed(() => {
  const r = record.value;
  return (
    r.student_id &&
    r.class_id &&
    r.classroom_id &&
    r.milk_status &&
    r.lunch_status &&
    r.snack_status &&
    r.brushing_status &&
    r.sleeping_status &&
    r.toilet_status
  );
});

const formatThaiDate = (date) => {
  const day = String(date.getDate()).padStart(2, "0");
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const year = date.getFullYear() + 543;
  return `${day}/${month}/${year}`;
};

const fetchStudentBehaviorRecords = async () => {
  try {
    const token = localStorage.getItem("access_token");
    const response = await axios.get(
      `${API_BASE_URL}/student_behavior_records/${teacherId.value}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );
    console.log("fetchStudentBehaviorRecords:", response.data);
    behaviorRecords.value = response.data.behavior_records || [];
  } catch (error) {
    console.error("โหลดข้อมูลนักเรียนล้มเหลว", error);
  }
};

const scanQR = () => {
  console.log("Scan QR Code");
};

const addBehavior = (behaviorReacord) => {
  if (behaviorReacord.behavior_id) {
    isEditing.value = true;
  } else {
    isEditing.value = false;
  }
  record.value = { ...behaviorReacord };
  dialog.value = true;
  console.log("Add behavior:", record.value);
};

const confirmRemove = (id) => {
  deleteId.value = id;
  confirmDeleteDialog.value = true;
};

// แก้ไขเมธอด confirmDelete ให้ถูกต้อง
async function confirmDelete() {
  try {
    const token = localStorage.getItem("access_token");
    await axios.delete(
      `${API_BASE_URL}/behavior_records/delete/${deleteId.value}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    showSnackbar("ลบข้อมูลสำเร็จ!", "success");
    fetchStudentBehaviorRecords();
  } catch (error) {
    showSnackbar("เกิดข้อผิดพลาดในการลบข้อมูล", "error");
    console.error("Error deleting data:", error);
  } finally {
    confirmDeleteDialog.value = false;
  }
}
const save = async () => {
  try {
    const token = localStorage.getItem("access_token");

    // เตรียมข้อมูล
    const payload = {
      behavior_id: record.value.behavior_id,
      student_id: record.value.student_id,
      class_id: record.value.class_id,
      classroom_id: record.value.classroom_id,
      record_date: record.value.record_date,
      milk_status: record.value.milk_status,
      lunch_status: record.value.lunch_status,
      snack_status: record.value.snack_status,
      brushing_status: record.value.brushing_status,
      sleeping_status: record.value.sleeping_status,
      toilet_status: record.value.toilet_status,
      notes: record.value.notes,
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
        `${API_BASE_URL}/behavior_records/update/${payload.behavior_id}`,
        payload,
        config
      );
      showSnackbar("อัปเดตข้อมูลบันทึกสังเกตพฤติกรรมสำเร็จ!", "success");
    } else {
      await axios.post(
        `${API_BASE_URL}/behavior_records/insert`,
        payload,
        config
      );
      showSnackbar("เพิ่มข้อมูลบันทึกสังเกตพฤติกรรมสำเร็จ!", "success");
    }

    dialog.value = false;
    fetchStudentBehaviorRecords();
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

  fetchStudentBehaviorRecords();

  const today = new Date();
  currentDateFormatted.value = formatThaiDate(today);
});

const goBack = () => {
  router.push("/home");
};
</script>
