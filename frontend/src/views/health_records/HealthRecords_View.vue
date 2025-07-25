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
            <v-btn color="success" @click="toggleHealth">
              <v-icon start>mdi-plus-box</v-icon>
              เพิ่มข้อมูลตรวจสุขภาพ
            </v-btn>
          </v-col>
        </v-row>

        <div style="height: 24px"></div>

        <!-- ตารางรายชื่อนักเรียน ห้อง.... -->
        <v-sheet rounded>
          <v-data-table
            :headers="headers"
            :items="healthRecords"
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
                  ตารางข้อมูลตรวจสุขภาพ
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
                    :color="item.health_id ? 'green' : 'black'"
                    size="32"
                    class="elevation-1"
                    style="cursor: pointer"
                    @click="addHealth(item)"
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
                    :color="item.health_id ? 'red darken-1' : 'grey'"
                    size="32"
                    class="elevation-1"
                    style="cursor: pointer"
                    @click="item.health_id ? confirmRemove(item.health_id) : ''"
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
                isEditing ? "แก้ไขข้อมูลตรวจสุขภาพ" : "เพิ่มข้อมูลตรวจสุขภาพ"
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
              <v-col cols="12" sm="6">{{ record.student_id }}</v-col>
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
                  v-model="record.body_temperature"
                  label="อุณหภูมิร่างกาย"
                  variant="outlined"
                  color="success"
                />
              </v-col>
              <v-col cols="12" sm="12">
                <v-card variant="outlined" class="mx-auto" max-width="100%">
                  <v-card-title style="font-size: 1.1rem">
                    สถานะการมาเรียน
                  </v-card-title>
                  <v-card-text>
                    <v-btn-toggle
                      v-model="record.attendance_status"
                      mandatory
                      divided
                      color="primary"
                      base-color="#e0e0e0"
                    >
                      <v-btn value="present" style="font-size: 1rem">
                        เข้าเรียน
                      </v-btn>
                      <v-btn value="home" style="font-size: 1rem">
                        กลับบ้าน
                      </v-btn>
                      <v-btn value="absent" style="font-size: 1rem">
                        ขาด
                      </v-btn>
                      <v-btn value="leave" style="font-size: 1rem"> ลา </v-btn>
                      <v-btn value="sick" style="font-size: 1rem"> ป่วย </v-btn>
                    </v-btn-toggle>
                    {{ record.attendance_status }}
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" sm="12">
                <v-card variant="outlined" class="mx-auto" max-width="100%">
                  <v-card-title style="font-size: 1.1rem">
                    ตรวจร่างกายนักเรียน
                  </v-card-title>
                  <v-card-text>
                    <v-row>
                      <v-col
                        cols="12"
                        sm="2"
                        align-self="center"
                        style="font-size: 1rem"
                      >
                        ตรวจเล็บ
                      </v-col>
                      <v-col cols="12" sm="8">
                        <v-btn-toggle
                          v-model="record.nails_status"
                          mandatory
                          divided
                          color="primary"
                          base-color="#e0e0e0"
                        >
                          <v-btn :value="true">
                            <v-icon icon="mdi-check-bold" />
                          </v-btn>
                          <v-btn :value="false">
                            <v-icon icon="mdi-close-thick" />
                          </v-btn>
                        </v-btn-toggle>
                        {{ record.nails_status }}
                      </v-col>
                    </v-row>
                    <v-row>
                      <v-col
                        cols="12"
                        sm="2"
                        align-self="center"
                        style="font-size: 1rem"
                      >
                        ตรวจผม
                      </v-col>
                      <v-col cols="12" sm="8">
                        <v-btn-toggle
                          v-model="record.hair_status"
                          mandatory
                          divided
                          color="primary"
                          base-color="#e0e0e0"
                        >
                          <v-btn :value="true">
                            <v-icon icon="mdi-check-bold" />
                          </v-btn>
                          <v-btn :value="false">
                            <v-icon icon="mdi-close-thick" />
                          </v-btn>
                        </v-btn-toggle>
                        {{ record.hair_status }}
                      </v-col>
                    </v-row>
                    <v-row>
                      <v-col
                        cols="12"
                        sm="2"
                        align-self="center"
                        style="font-size: 1rem"
                      >
                        ตรวจฟัน
                      </v-col>
                      <v-col cols="12" sm="8">
                        <v-btn-toggle
                          v-model="record.teeth_status"
                          mandatory
                          divided
                          color="primary"
                          base-color="#e0e0e0"
                        >
                          <v-btn :value="true">
                            <v-icon icon="mdi-check-bold" />
                          </v-btn>
                          <v-btn :value="false">
                            <v-icon icon="mdi-close-thick" />
                          </v-btn>
                        </v-btn-toggle>
                        {{ record.teeth_status }}
                      </v-col>
                    </v-row>
                    <v-row>
                      <v-col
                        cols="12"
                        sm="2"
                        align-self="center"
                        style="font-size: 1rem"
                      >
                        ตรวจร่างกาย
                      </v-col>
                      <v-col cols="12" sm="8">
                        <v-btn-toggle
                          v-model="record.body_status"
                          mandatory
                          divided
                          color="primary"
                          base-color="#e0e0e0"
                        >
                          <v-btn :value="true">
                            <v-icon icon="mdi-check-bold" />
                          </v-btn>
                          <v-btn :value="false">
                            <v-icon icon="mdi-close-thick" />
                          </v-btn>
                        </v-btn-toggle>
                        {{ record.body_status }}
                      </v-col>
                    </v-row>
                    <v-row>
                      <v-col
                        cols="12"
                        sm="2"
                        align-self="center"
                        style="font-size: 1rem"
                      >
                        ตรวจตา
                      </v-col>
                      <v-col cols="12" sm="8">
                        <v-btn-toggle
                          v-model="record.eye_status"
                          mandatory
                          divided
                          color="primary"
                          base-color="#e0e0e0"
                        >
                          <v-btn :value="true">
                            <v-icon icon="mdi-check-bold" />
                          </v-btn>
                          <v-btn :value="false">
                            <v-icon icon="mdi-close-thick" />
                          </v-btn>
                        </v-btn-toggle>
                        {{ record.eye_status }}
                      </v-col>
                    </v-row>
                    <v-row>
                      <v-col
                        cols="12"
                        sm="2"
                        align-self="center"
                        style="font-size: 1rem"
                      >
                        ตรวจจมูก
                      </v-col>
                      <v-col cols="12" sm="8">
                        <v-btn-toggle
                          v-model="record.nose_status"
                          mandatory
                          divided
                          color="primary"
                          base-color="#e0e0e0"
                        >
                          <v-btn :value="true">
                            <v-icon icon="mdi-check-bold" />
                          </v-btn>
                          <v-btn :value="false">
                            <v-icon icon="mdi-close-thick" />
                          </v-btn>
                        </v-btn-toggle>
                        {{ record.nose_status }}
                      </v-col>
                    </v-row>
                    <v-row>
                      <v-col
                        cols="12"
                        sm="2"
                        align-self="center"
                        style="font-size: 1rem"
                      >
                        ตรวจหู
                      </v-col>
                      <v-col cols="12" sm="8">
                        <v-btn-toggle
                          v-model="record.ear_status"
                          mandatory
                          divided
                          color="primary"
                          base-color="#e0e0e0"
                        >
                          <v-btn :value="true">
                            <v-icon icon="mdi-check-bold" />
                          </v-btn>
                          <v-btn :value="false">
                            <v-icon icon="mdi-close-thick" />
                          </v-btn>
                        </v-btn-toggle>
                        {{ record.ear_status }}
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" sm="12">
                <v-text-field
                  v-model="record.notes"
                  label="หมายเหตุ"
                  variant="outlined"
                />
              </v-col>
              <!-- รูปภาพ -->
              <v-col cols="12" sm="12">
                <!-- <v-text-field
                  v-model="record.student_photo"
                  label="รูปภาพ"
                  variant="outlined"
                /> -->
                <v-card variant="outlined" class="mx-auto" max-width="100%">
                  <v-card-title style="font-size: 1.1rem">
                    รูปภาพนักเรียน
                  </v-card-title>
                  <v-card-text>
                    <v-btn @click="openCamera" color="primary">
                      <v-icon color="white" icon="mdi-camera" />
                      &nbsp;&nbsp;ถ่ายรูป
                    </v-btn>
                    <!-- input กล้อง -->
                    <input
                      ref="fileInput"
                      type="file"
                      accept="image/*"
                      capture="environment"
                      @change="onFileChange"
                      style="display: none"
                    />

                    <!-- รูปตัวอย่าง -->
                    <div v-if="imagePreview" style="margin-top: 20px">
                      <h3>รูปตัวอย่าง:</h3>
                      <v-img
                        :src="imagePreview"
                        alt="preview"
                        max-width="250"
                        max-height="250"
                        class="mx-auto"
                        style="border-radius: 12px; border: 1px solid #ccc"
                      />
                    </div>

                    <!-- แสดงภาพจากฐานข้อมูล หากยังไม่มี preview -->
                    <div
                      v-else-if="record?.student_photo"
                      class="mt-2 text-center"
                    >
                      <v-img
                        :src="getStudentImageUrl(record.student_photo)"
                        max-width="250"
                        max-height="250"
                        class="mx-auto"
                        style="border-radius: 12px; border: 1px solid #ccc"
                      />
                    </div>

                    <!-- fallback ถ้าไม่มีภาพเลย -->
                    <div v-else class="text-grey mt-2 text-center">
                      ยังไม่มีรูปภาพ
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
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
              :disabled="!isHealthFormValid"
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
const healthRecords = ref([]);
const teacherId = ref("1");

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
  health_id: null,
  student_id: "",
  classroom_id: "",
  body_temperature: "",
  attendance_status: "",
  nails_status: "",
  hair_status: "",
  teeth_status: "",
  body_status: "",
  eye_status: "",
  ear_status: "",
  nose_status: "",
  notes: "",
  student_photo: "",
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

// ตัวแปร
const fileInput = ref(null);
const imageFile = ref(null);
const imagePreview = ref(null);

// ฟังก์ชันเปิดกล้อง
const openCamera = () => {
  fileInput.value.click();
};

// เมื่อเลือกรูป / ถ่ายรูป
const onFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    imageFile.value = file;
    imagePreview.value = URL.createObjectURL(file);
  }
};

// ฟังก์ชันโหลดรูปภาพ
const getStudentImageUrl = (filename) => {
  if (!filename) return "";
  return `${API_BASE_URL}/uploads/${filename}`; // เปลี่ยน URL ตามจริง
};

// ฟังก์ชันอัปโหลดรูป (ตัวอย่าง POST ไป backend)
// const uploadImage = async () => {
//   if (!imageFile.value) return;

//   const formData = new FormData();
//   formData.append("image", imageFile.value);

//   try {
//     const res = await fetch("https://your-backend/upload", {
//       method: "POST",
//       body: formData,
//     });

//     if (res.ok) {
//       alert("อัปโหลดสำเร็จ!");
//     } else {
//       alert("อัปโหลดไม่สำเร็จ");
//     }
//   } catch (err) {
//     console.error("Upload failed:", err);
//     alert("เกิดข้อผิดพลาด");
//   }
// };

// Validation
const required = (v) => !!v || "จำเป็นต้องกรอก";
const isHealthFormValid = computed(() => {
  const r = record.value;
  return r.student_id && r.attendance_status;
  // return (
  //   r.student_id &&
  //   r.attendance_status &&
  //   r.nails_status &&
  //   r.hair_status &&
  //   r.teeth_status &&
  //   r.body_status &&
  //   r.eye_status &&
  //   r.ear_status &&
  //   r.nose_status &&
  //   r.student_photo
  // );
});

const formatThaiDate = (date) => {
  const day = String(date.getDate()).padStart(2, "0");
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const year = date.getFullYear() + 543;
  return `${day}/${month}/${year}`;
};

const fetchStudentHealthRecords = async () => {
  try {
    const token = localStorage.getItem("access_token");
    const response = await axios.get(
      `${API_BASE_URL}/student_health_records/${teacherId.value}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );
    console.log("fetchStudentHealthRecords:", response.data);
    healthRecords.value = response.data.health_records || [];
  } catch (error) {
    console.error("โหลดข้อมูลนักเรียนล้มเหลว", error);
  }
};

const toggleHealth = () => {
  isEditing.value = false;
  imagePreview.value = null;
  record.value = {
    health_id: null,
    student_id: "",
    classroom_id: null,
    body_temperature: "",
    attendance_status: "",
    nails_status: "",
    hair_status: "",
    teeth_status: "",
    body_status: "",
    eye_status: "",
    ear_status: "",
    nose_status: "",
    notes: "",
    student_photo: "",
  };
  dialog.value = true;
  // router.push("/health_records_add");
};

const addHealth = (healthReacord) => {
  if (healthReacord.health_id) {
    isEditing.value = true;
  } else {
    isEditing.value = false;
  }
  imagePreview.value = null;
  record.value = { ...healthReacord };
  dialog.value = true;
  console.log("Add Health:", record.value);
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
      `${API_BASE_URL}/health_records/delete/${deleteId.value}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    showSnackbar("ลบข้อมูลสำเร็จ!", "success");
    fetchStudentHealthRecords;
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
      health_id: record.value.health_id,
      student_id: record.value.student_id,
      classroom_id: record.value.classroom_id,
      body_temperature: record.value.body_temperature,
      attendance_status: record.value.attendance_status,
      nails_status: record.value.nails_status,
      hair_status: record.value.hair_status,
      teeth_status: record.value.teeth_status,
      body_status: record.value.body_status,
      eye_status: record.value.eye_status,
      ear_status: record.value.ear_status,
      nose_status: record.value.nose_status,
      notes: record.value.notes,
      student_photo: imagePreview.value,
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
        `${API_BASE_URL}/health_records/update/${payload.health_id}`,
        payload,
        config
      );
      showSnackbar("อัปเดตข้อมูลตรวจสุขภาพ/เช็คชื่อสำเร็จ!", "success");
    } else {
      await axios.post(
        `${API_BASE_URL}/health_records/insert`,
        payload,
        config
      );
      showSnackbar("เพิ่มข้อมูลตรวจสุขภาพ/เช็คชื่อสำเร็จ!", "success");
    }

    dialog.value = false;
    fetchStudentHealthRecords();
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

  fetchStudentHealthRecords();

  const today = new Date();
  currentDateFormatted.value = formatThaiDate(today);
});

const goBack = () => {
  router.push("/home");
};
</script>
