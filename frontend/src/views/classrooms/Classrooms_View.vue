<template>
  <!-- App Bar ด้านบน -->
  <AppBar @toggle-drawer="drawer = !drawer" />

  <v-main>
    <v-container>
      <!-- ปุ่มควบคุม -->
      <v-row class="align-center">
        <v-col cols="auto">
          <v-btn color="red" @click="goBack" class="btn-back">
            <v-icon start>mdi-arrow-left</v-icon> กลับ
          </v-btn>
        </v-col>
        <v-col cols="auto">
          <v-btn color="green-darken-1" @click="toggleSchool">
            <v-icon start>mdi-town-hall</v-icon> แสดงข้อมูลโรงเรียน
          </v-btn>
        </v-col>
        <v-col cols="auto">
          <v-btn color="green-darken-2" @click="toggleLevelTable">
            <v-icon start>mdi-table-furniture</v-icon> แสดงข้อมูลระดับชั้น
          </v-btn>
        </v-col>
        <v-col cols="auto">
          <v-btn color="green-darken-4" @click="toggleRoomTable">
            <v-icon start>mdi-google-classroom</v-icon> แสดงข้อมูลห้องเรียน
          </v-btn>
        </v-col>
      </v-row>

      <div style="height: 24px"></div>

      <!-- ตารางห้องเรียน -->
      <v-sheet
        v-if="currentTable === 'room'"
        rounded
        class="pa-4"
        style="background-color: #ffffff"
      >
        <v-row class="mb-4">
          <v-col cols="auto">
            <v-btn color="green-darken-4" @click="addRoomTable">
              <v-icon start>mdi-plus</v-icon> เพิ่มข้อมูลห้องเรียน
            </v-btn>
          </v-col>
        </v-row>

        <v-data-table
          :headers="roomHeaders"
          :items="rooms"
          :items-per-page="10"
          class="custom-table custom-footer elevation-1"
        >
          <template v-slot:top>
            <v-toolbar flat class="bg-green-darken-4 text-white">
              <v-toolbar-title>
                <v-icon
                  icon="mdi-google-classroom"
                  size="x-small"
                  class="me-2"
                  color="white"
                />
                ตารางข้อมูลห้องเรียน
              </v-toolbar-title>
              <v-spacer />
              <v-text-field
                v-model="roomSearch"
                label="ค้นหา"
                variant="outlined"
                density="compact"
                clearable
                hide-details
                style="max-width: 250px"
              />
            </v-toolbar>
          </template>

          <template v-slot:header="{ headers }">
            <thead>
              <tr>
                <th
                  v-for="header in headers"
                  :key="header.key"
                  style="background-color: #2e7d32; color: white"
                >
                  {{ header.title }}
                </th>
              </tr>
            </thead>
          </template>

          <template v-slot:item="{ item, index }">
            <tr
              :style="{
                backgroundColor: index % 2 === 0 ? '#E8F5E9' : '#FFFFFF',
              }"
            >
              <td style="color: black">{{ index + 1 }}</td>
              <td style="color: black">{{ item.classroom_name }}</td>
              <td style="color: black">{{ item.class_name }}</td>
              <td style="color: black">{{ item.school_name }}</td>
              <td style="color: black">{{ item.classroom_male }}</td>
              <td style="color: black">{{ item.classroom_female }}</td>
              <td style="color: black">{{ item.classroom_all }}</td>
              <td style="color: black">{{ item.teacher_name || "-" }}</td>
              <td class="text-center">
                <v-avatar
                  color="yellow-darken-2"
                  size="32"
                  class="elevation-1"
                  style="cursor: pointer"
                  @click="editItem(item, 'room')"
                >
                  <v-icon color="white" icon="mdi-pencil" size="20" />
                </v-avatar>
              </td>
              <td class="text-center">
                <v-avatar
                  color="red-darken-1"
                  size="32"
                  class="elevation-1"
                  style="cursor: pointer"
                  @click="confirmDelete(item, 'room')"
                >
                  <v-icon color="white" icon="mdi-delete" size="20" />
                </v-avatar>
              </td>
            </tr>
          </template>
        </v-data-table>
      </v-sheet>

      <!-- ตารางระดับชั้น -->
      <v-sheet
        v-else-if="currentTable === 'level'"
        rounded
        class="pa-4"
        style="background-color: #ffffff"
      >
        <v-row class="mb-4">
          <v-col cols="auto">
            <v-btn color="green-darken-2" @click="addLevelTable">
              <v-icon start>mdi-plus</v-icon> เพิ่มข้อมูลระดับชั้น
            </v-btn>
          </v-col>
        </v-row>

        <v-data-table
          :headers="levelHeaders"
          :items="filteredLevels"
          :items-per-page="10"
          class="custom-table custom-footer elevation-1"
        >
          <template #top>
            <v-toolbar flat class="bg-green-darken-2 text-white">
              <v-toolbar-title>
                <v-icon
                  icon="mdi-table-furniture"
                  size="x-small"
                  class="me-2"
                  color="white"
                />
                ตารางข้อมูลระดับชั้น
              </v-toolbar-title>
              <v-spacer />
              <v-text-field
                v-model="levelSearch"
                label="ค้นหา"
                variant="outlined"
                density="compact"
                clearable
                hide-details
                style="max-width: 250px"
              />
            </v-toolbar>
          </template>

          <template v-slot:header="{ headers }">
            <thead>
              <tr>
                <th
                  v-for="header in headers"
                  :key="header.key"
                  style="background-color: #388e3c; color: white"
                >
                  {{ header.title }}
                </th>
              </tr>
            </thead>
          </template>

          <template v-slot:item="{ item, index }">
            <tr
              :style="{
                backgroundColor: index % 2 === 0 ? '#E8F5E9' : '#FFFFFF',
              }"
            >
              <td style="color: black">{{ index + 1 }}</td>
              <td style="color: black">{{ item.level_name }}</td>
              <td style="color: black">{{ item.room_count }}</td>
              <td style="color: black">{{ item.school_name }}</td>

              <!-- ปุ่มแก้ไข -->
              <td class="text-center">
                <v-avatar
                  color="yellow-darken-2"
                  size="32"
                  class="elevation-1"
                  style="cursor: pointer"
                  @click="editItem(item, 'class')"
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
                  @click="confirmDelete(item, 'level')"
                >
                  <v-icon color="white" icon="mdi-delete" size="20" />
                </v-avatar>
              </td>
            </tr>
          </template>
        </v-data-table>
      </v-sheet>

      <!-- ตารางโรงเรียน -->
      <v-sheet v-else rounded class="pa-4" style="background-color: #ffffff">
        <v-row class="mb-4">
          <v-col cols="auto">
            <v-btn color="green-darken-1" @click="addSchool">
              <v-icon start>mdi-plus</v-icon> เพิ่มข้อมูลโรงเรียน
            </v-btn>
          </v-col>
        </v-row>
        <v-data-table
          :headers="schoolHeaders"
          :items="filteredSchools"
          :items-per-page="10"
          class="custom-table custom-footer elevation-1"
        >
          <template #top>
            <v-toolbar flat class="bg-green-darken-1 text-white">
              <v-toolbar-title>
                <v-icon
                  icon="mdi-town-hall"
                  size="x-small"
                  class="me-2"
                  color="white"
                />
                ตารางข้อมูลโรงเรียน
              </v-toolbar-title>
              <v-spacer />
              <v-text-field
                v-model="schoolSearch"
                label="ค้นหา"
                variant="outlined"
                density="compact"
                clearable
                hide-details
                style="max-width: 250px"
              />
            </v-toolbar>
          </template>

          <template v-slot:header="{ headers }">
            <thead>
              <tr>
                <th
                  v-for="header in headers"
                  :key="header.key"
                  style="background-color: #43a047; color: white"
                >
                  {{ header.title }}
                </th>
              </tr>
            </thead>
          </template>

          <template v-slot:item="{ item, index }">
            <tr
              :style="{
                backgroundColor: index % 2 === 0 ? '#E8F5E9' : '#FFFFFF',
              }"
            >
              <td style="color: black">{{ index + 1 }}</td>
              <td style="color: black">{{ item.school_name }}</td>
              <td class="text-center">
                <v-avatar
                  color="yellow-darken-2"
                  size="32"
                  class="elevation-1"
                  style="cursor: pointer"
                  @click="editItem(item, 'school')"
                >
                  <v-icon color="white" icon="mdi-pencil" size="20" />
                </v-avatar>
              </td>
              <td class="text-center">
                <v-avatar
                  color="red-darken-1"
                  size="32"
                  class="elevation-1"
                  style="cursor: pointer"
                  @click="confirmDelete(item, 'school')"
                >
                  <v-icon color="white" icon="mdi-delete" size="20" />
                </v-avatar>
              </td>
            </tr>
          </template>
        </v-data-table>
      </v-sheet>

      <!-- Dialog เพิ่ม/แก้ไขข้อมูล -->
      <v-dialog v-model="dialog" max-width="850" persistent>
        <v-card
          class="dialog-popup"
          style="background-color: #ffffff; color: black"
        >
          <v-toolbar flat :color="isEditing ? 'warning' : 'success'">
            <v-card-title class="dialog-title text-white">
              <v-icon start class="mr-2">{{
                isEditing ? "mdi-pencil" : "mdi-plus"
              }}</v-icon>
              {{
                isEditing
                  ? isRoom
                    ? "แก้ไขข้อมูลห้องเรียน"
                    : isLevel
                    ? "แก้ไขข้อมูลระดับชั้น"
                    : "แก้ไขข้อมูลโรงเรียน"
                  : isRoom
                  ? "เพิ่มข้อมูลห้องเรียน"
                  : isLevel
                  ? "เพิ่มข้อมูลระดับชั้น"
                  : "เพิ่มข้อมูลโรงเรียน"
              }}
            </v-card-title>
          </v-toolbar>
          <v-card-text>
            <v-row>
              <template v-if="isRoom">
                <!-- เลือกโรงเรียน -->
                <v-col cols="12" md="6">
                  <v-select
                    v-model="form.school_id"
                    :items="school"
                    item-title="school_name"
                    item-value="school_id"
                    label="เลือกโรงเรียน"
                    variant="outlined"
                    color="success"
                    @update:modelValue="form.level_id = null"
                    :rules="[required]"
                  />
                </v-col>

                <!-- เลือกระดับชั้น (กรองตามโรงเรียน) -->
                <v-col cols="12" md="6">
                  <v-select
                    v-model="form.level_id"
                    :items="filteredLevels"
                    item-title="level_name"
                    item-value="level_id"
                    label="ระดับชั้น"
                    variant="outlined"
                    color="success"
                    :disabled="!form.school_id"
                    :rules="[required]"
                  />
                </v-col>

                <!-- ชื่อห้องเรียน -->
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="form.room_name"
                    label="ชื่อห้องเรียน"
                    variant="outlined"
                    color="success"
                    :rules="[required]"
                  />
                </v-col>

                <!-- ครูประจำชั้น (multiple selection) -->
                <v-col cols="12" md="6">
                  <v-select
                    v-model="form.teacher_id"
                    :items="teachers"
                    item-title="teacher_name"
                    item-value="teacher_id"
                    label="ครูประจำชั้น"
                    variant="outlined"
                    color="success"
                    multiple
                    chips
                    :rules="[
                      (v) =>
                        (!!v && v.length > 0) || 'กรุณาเลือกอย่างน้อย 1 คน',
                    ]"
                  />
                </v-col>

                <!-- จำนวนนักเรียน -->
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="form.room_male"
                    label="นักเรียนชาย"
                    variant="outlined"
                    color="success"
                    type="number"
                    :rules="[required, (v) => v >= 0 || 'ต้องไม่น้อยกว่า 0']"
                  />
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="form.room_female"
                    label="นักเรียนหญิง"
                    variant="outlined"
                    color="success"
                    type="number"
                    :rules="[required, (v) => v >= 0 || 'ต้องไม่น้อยกว่า 0']"
                  />
                </v-col>

                <!-- นักเรียนรวม (คำนวณอัตโนมัติ) -->
                <v-col cols="12" md="6">
                  <v-text-field
                    :value="totalStudents"
                    label="นักเรียนรวม"
                    variant="outlined"
                    color="success"
                    readonly
                  />
                </v-col>
              </template>
              <template v-else-if="isLevel">
                <!-- ระดับชั้น -->
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="form.level_name"
                    label="ชื่อระดับชั้น"
                    variant="outlined"
                    color="success"
                    :rules="[required]"
                  />
                </v-col>

                <!-- จำนวนห้อง (แสดงอย่างเดียว) -->
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="form.room_count"
                    disabled
                    label="จำนวนห้อง"
                    variant="outlined"
                    color="success"
                  />
                </v-col>

                <!-- เลือกโรงเรียน -->
                <v-col cols="12" md="6">
                  <v-select
                    v-model="form.school_id"
                    :items="school"
                    item-title="school_name"
                    item-value="school_id"
                    label="เลือกโรงเรียน"
                    variant="outlined"
                    color="success"
                    :rules="[required]"
                  />
                </v-col>
              </template>

              <template v-else>
                <v-col cols="12" md="12">
                  <v-text-field
                    v-model="form.school_name"
                    label="ชื่อโรงเรียน"
                    variant="outlined"
                    color="success"
                    :rules="[required]"
                  />
                </v-col>
              </template>
            </v-row>
          </v-card-text>
          <v-card-actions class="justify-end">
            <v-btn
              color="red-darken-1"
              variant="flat"
              class="text-white"
              @click="dialog = false"
            >
              ยกเลิก
            </v-btn>
            <v-btn
              color="green-darken-1"
              variant="flat"
              class="text-white ml-2"
              @click="save"
              :disabled="!isFormValid"
              :loading="loading"
            >
              บันทึก
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Dialog ยืนยันการลบ -->
      <v-dialog v-model="confirmDeleteDialog" max-width="400">
        <v-card class="confirm-delete-dialog">
          <v-card-title class="text-h6 confirm-delete-title"
            >ยืนยันการลบ</v-card-title
          >
          <v-card-text class="confirm-delete-text"
            >คุณต้องการลบข้อมูลใช่หรือไม่?</v-card-text
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
              @click="deleteItem"
              >ลบ</v-btn
            >
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Snackbar แจ้งเตือน -->
      <v-snackbar
        v-model="snackbar.show"
        :color="snackbar.color"
        :timeout="2000"
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
    </v-container>
  </v-main>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "@/utils/axios"; // ใช้ instance แทน
import AppBar from "@/views/appbar/AppBar.vue";
import { API_BASE_URL } from "@/assets/config";

const router = useRouter();

// ตัวแปรควบคุม UI
const drawer = ref(true);
const currentTable = ref("room");
const dialog = ref(false);
const confirmDeleteDialog = ref(false);
const loading = ref(false);
const isEditing = ref(false);

// ตัวแปรค้นหา
const schoolSearch = ref("");
const levelSearch = ref("");
const roomSearch = ref("");

// ข้อมูล
const rooms = ref([]);
const levels = ref([]);
const school = ref([]);
const teachers = ref([]);

// ฟอร์มข้อมูล
const form = ref({
  room_id: null,
  room_name: "",
  room_male: 0,
  room_female: 0,
  room_all: 0,
  teacher_id: null,
  level_id: null,
  level_name: "",
  room_count: 0, // เพิ่มไว้
  school_id: null,
  school_name: "",
});

// ข้อมูลสำหรับการลบ
const itemToDelete = ref({
  id: null,
  type: null,
});

// Snackbar
const snackbar = ref({
  show: false,
  text: "",
  color: "success",
});

// Headers ตาราง
const roomHeaders = [
  { title: "ลำดับ", key: "num", sortable: false },
  { title: "ชื่อห้องเรียน", key: "classroom_name" },
  { title: "ระดับชั้น", key: "class_name" },
  { title: "โรงเรียน", key: "school_name" },
  { title: "นักเรียนชาย", key: "classroom_male" },
  { title: "นักเรียนหญิง", key: "classroom_female" },
  { title: "นักเรียนรวม", key: "classroom_all" },
  { title: "ครูประจำชั้น", key: "teacher_name" },
  { title: "แก้ไข", key: "edit", sortable: false, align: "center" },
  { title: "ลบ", key: "delete", sortable: false, align: "center" },
];

const levelHeaders = [
  { title: "ลำดับ", key: "num", sortable: false },
  { title: "ชื่อระดับชั้น", key: "level_name" },
  { title: "จำนวนห้อง", key: "room_count" },
  { title: "ชื่อโรงเรียน", key: "school_name" },
  { title: "แก้ไข", key: "edit", sortable: false, align: "center" },
  { title: "ลบ", key: "delete", sortable: false, align: "center" },
];

const schoolHeaders = [
  { title: "ลำดับ", key: "num", sortable: false },
  { title: "ชื่อโรงเรียน", key: "school_name" },
  { title: "แก้ไข", key: "edit", sortable: false, align: "center" },
  { title: "ลบ", key: "delete", sortable: false, align: "center" },
];

// Computed properties
const isRoom = computed(() => currentTable.value === "room");
const isLevel = computed(() => currentTable.value === "level");
// const isSchool = computed(() => currentTable.value === "school");

// const filteredRooms = computed(() => {
//   if (!roomSearch.value) return rooms.value;
//   return rooms.value.filter(
//     (r) =>
//       r.room_name.toLowerCase().includes(roomSearch.value.toLowerCase()) ||
//       (r.teacher_name &&
//         r.teacher_name.toLowerCase().includes(roomSearch.value.toLowerCase()))
//   );
// });

// const filteredLevels = computed(() => {
//   if (!form.value.school_id) return []; // ยังไม่เลือกโรงเรียน → ไม่แสดงอะไรเลย
//   return levels.value.filter(
//     (level) => level.school_id === form.value.school_id
//   );
// });

const filteredLevels = computed(() => {
  if (!levelSearch.value) return levels.value;
  return levels.value.filter(
    (l) =>
      l.level_name.toLowerCase().includes(levelSearch.value.toLowerCase()) ||
      (l.teacher_name &&
        l.teacher_name.toLowerCase().includes(levelSearch.value.toLowerCase()))
  );
});

const filteredSchools = computed(() => {
  if (!schoolSearch.value) return school.value;
  return school.value.filter((s) =>
    s.school_name.toLowerCase().includes(schoolSearch.value.toLowerCase())
  );
});

// Validation rule
const required = (v) => !!v || "กรุณากรอกข้อมูล";

const isFormValid = computed(() => {
  if (isRoom.value) {
    return (
      form.value.room_name &&
      form.value.level_id &&
      form.value.teacher_id &&
      form.value.room_male !== null &&
      form.value.room_female !== null &&
      form.value.room_male !== "" &&
      form.value.room_female !== ""
    );
  } else if (isLevel.value) {
    return (
      (form.value.level_name || "").trim() !== "" &&
      form.value.school_id !== null
    );
  } else {
    return (form.value.school_name || "").trim() !== "";
  }
});

// การคำนวณนักเรียนรวมอัตโนมัติ
const totalStudents = computed(() => {
  const male = parseInt(form.value.room_male) || 0;
  const female = parseInt(form.value.room_female) || 0;
  return male + female;
});

// Snackbar function
const showSnackbar = (text, color = "success") => {
  snackbar.value = { show: true, text, color };
};

// Toggle tables
const toggleRoomTable = () => {
  currentTable.value = "room";
  //console.log("Table switched to:", currentTable.value);
  fetchClassRoom();
};

const toggleLevelTable = () => {
  currentTable.value = "level";
  //console.log("Table switched to:", currentTable.value);
  fetchLevels();
};

const toggleSchool = () => {
  currentTable.value = "school";
  //console.log("Table switched to:", currentTable.value);
  fetchSchools();
};

const goBack = () => {
  router.push("/home");
};

// Add new items
const addRoomTable = () => {
  isEditing.value = false;
  form.value = {
    room_id: null,
    room_name: "",
    room_male: 0,
    room_female: 0,
    room_all: 0,
    level_id: null,
    teacher_id: null,
    school_id: null,
  };
  dialog.value = true;
};

const addLevelTable = () => {
  isEditing.value = false;
  form.value = {
    level_id: null,
    level_name: "",
    room_count: 0,
    teacher_id: null,
  };
  dialog.value = true;
};

const addSchool = () => {
  isEditing.value = false;
  form.value = {
    school_id: null,
    school_name: "",
  };
  dialog.value = true;
};

// Edit existing items
const editItem = (item, type) => {
  isEditing.value = true;
  form.value = { ...item };

  if (type === "room") {
    form.value.room_id = item.classroom_id ?? null;
    form.value.room_name = item.classroom_name ?? "";
    form.value.room_male = Number(item.classroom_male ?? 0);
    form.value.room_female = Number(item.classroom_female ?? 0);
    form.value.room_all =
      Number(item.classroom_male ?? 0) + Number(item.classroom_female ?? 0);
    form.value.level_id = item.class_id ?? null;
    form.value.school_id = item.school_id ?? null;
    form.value.school_name = item.school_name ?? "";

    // แปลง teacher_name string --> array teacher_id
    if (item.teacher_name) {
      const teacherNames = item.teacher_name.split(",").map((name) => {
        return name
          .trim()
          .replace(/^(ครู|นาย|นางสาว|นาง)/, "")
          .trim()
          .toLowerCase();
      });

      // แสดงผลลัพธ์ใน console
      //console.log("teacherNames", teacherNames);
      //console.log("teachers", teachers.value.map(t => `${t.prefix_name}${t.teacher_name}`));

      // เปรียบเทียบกับ teacher_name ที่ไม่มี prefix
      form.value.teacher_id = teachers.value
        .filter((t) =>
          teacherNames.includes(t.teacher_name.trim().toLowerCase())
        )
        .map((t) => t.teacher_id);
    } else {
      form.value.teacher_id = [];
    }
  } else if (type === "level") {
    form.value.level_id = item.class_id ?? null;
    form.value.level_name = item.class_name ?? "";
    form.value.room_count = item.room_count ?? 0;
    form.value.school_id = item.school_id ?? null;
    form.value.school_name = item.school_name ?? "";
  } else if (type === "school") {
    form.value.school_id = item.school_id ?? null;
    form.value.school_name = item.school_name ?? "";
  } else {
    form.value = { ...item };
  }

  dialog.value = true;
};

// Confirm delete dialog
const confirmDelete = (item, type) => {
  //console.log("confirmDelete item:", item);
  let id = null;
  if (type === "level" || type === "class") {
    id = item.level_id ?? item.class_id;
  } else if (type === "room") {
    id = item.classroom_id;
  } else if (type === "school") {
    id = item.school_id;
  }

  itemToDelete.value = { id, type };
  //console.log("Confirm delete id:", id, "type:", type); // ✅ log เช็คค่าตรง
  confirmDeleteDialog.value = true;
};

const deleteItem = async () => {
  console.log("ลบ:", itemToDelete.value); // ✅ เช็คตรงนี้ก่อน
  try {
    loading.value = true;
    const token = localStorage.getItem("access_token");
    const config = {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    };

    let url = "";
    if (itemToDelete.value.type === "room") {
      url = `${API_BASE_URL}/classrooms/delete/${itemToDelete.value.id}`;
    } else if (itemToDelete.value.type === "level") {
      url = `${API_BASE_URL}/class/delete/${itemToDelete.value.id}`;
    } else {
      url = `${API_BASE_URL}/school/delete/${itemToDelete.value.id}`;
    }

    await axios.delete(url, config);
    showSnackbar("ลบข้อมูลสำเร็จ", "success");

    // Refresh data
    if (itemToDelete.value.type === "room") {
      await fetchClassRoom();
    } else if (itemToDelete.value.type === "level") {
      await fetchLevels();
    } else {
      await fetchSchools();
    }

    confirmDeleteDialog.value = false;
  } catch (error) {
    console.error("Error deleting item:", error);
    showSnackbar("เกิดข้อผิดพลาดในการลบข้อมูล", "error");
  } finally {
    loading.value = false;
  }
};

// Save (insert/update)
const save = async () => {
  try {
    loading.value = true;

    const token = localStorage.getItem("access_token");
    const config = {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      withCredentials: true,
    };

    // Payload สำหรับโรงเรียน
    const payload_school = {
      school_id: form.value.school_id,
      school_name: form.value.school_name,
    };

    // Payload สำหรับระดับชั้น
    const payload_level = {
      level_id: form.value.level_id,
      level_name: form.value.level_name,
      school_id: form.value.school_id,
    };

    // Payload สำหรับห้องเรียน
    const payload_room = {
      room_name: form.value.room_name,
      room_male: Number(form.value.room_male),
      room_female: Number(form.value.room_female),
      room_all: totalStudents.value,
      level_id: form.value.level_id,
      school_id: form.value.school_id,

      // ปรับตรงนี้ให้แปลง teacher_id ออกจาก Vue Proxy
      teacher_id: Array.isArray(form.value.teacher_id)
        ? [...form.value.teacher_id]
        : [form.value.teacher_id],
    };

    // ห้องเรียน
    if (isRoom.value) {
      console.log("ห้องเรียน update :", payload_room);
      if (isEditing.value) {
        await axios.put(
          `${API_BASE_URL}/classrooms/update/${form.value.classroom_id}`,
          payload_room,
          config
        );
        showSnackbar("อัปเดตข้อมูลห้องเรียนสำเร็จ", "success");
      } else {
        //console.log("ห้องเรียน insert :", payload_room);
        await axios.post(
          `${API_BASE_URL}/classrooms/insert`,
          payload_room,
          config
        );
        showSnackbar("เพิ่มข้อมูลห้องเรียนสำเร็จ", "success");
      }
      await fetchClassRoom();
      // ระดับชั้น
    } else if (isLevel.value) {
      if (isEditing.value) {
        //console.log("ระดับชั้น update :", payload_level);
        await axios.put(
          `${API_BASE_URL}/class/update/${form.value.level_id}`,
          payload_level,
          config
        );
        showSnackbar("อัปเดตข้อมูลระดับชั้นสำเร็จ", "success");
      } else {
        //console.log("ระดับชั้น insert :", payload_level);
        await axios.post(`${API_BASE_URL}/class/insert`, payload_level, config);
        showSnackbar("เพิ่มข้อมูลระดับชั้นสำเร็จ", "success");
      }
      await fetchLevels();
    } else {
      // โรงเรียน
      if (isEditing.value) {
        await axios.put(
          `${API_BASE_URL}/school/update/${form.value.school_id}`,
          payload_school,
          config
        );
        showSnackbar("อัปเดตข้อมูลโรงเรียนสำเร็จ", "success");
      } else {
        await axios.post(
          `${API_BASE_URL}/school/insert`,
          payload_school,
          config
        );
        showSnackbar("เพิ่มข้อมูลโรงเรียนสำเร็จ", "success");
      }
      await fetchSchools();
    }

    dialog.value = false;
  } catch (error) {
    console.error("Error saving data:", error);
    showSnackbar("เกิดข้อผิดพลาดในการบันทึกข้อมูล", "error");
  } finally {
    loading.value = false;
  }
};

// ดึงรายห้องเรียน API แสดงในตาราง
const fetchClassRoom = async () => {
  try {
    const token = localStorage.getItem("access_token");
    const response = await axios.get(`${API_BASE_URL}/classrooms`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      withCredentials: true, // ถ้าคุณใช้ cookie-based auth ด้วย
    });

    // Log ข้อมูลที่ได้จาก backend
    console.log("Raw response.data from backend:", response.data);

    // แปลงข้อมูลให้มี school_name และ level_name
    rooms.value = response.data.map((room) => ({
      ...room,
      school_name:
        school.value.find((s) => s.school_id === room.school_id)?.school_name ||
        "",
      level_name:
        levels.value.find((l) => l.level_id === room.level_id)?.level_name ||
        "",
    }));
  } catch (error) {
    console.error("Error fetching rooms:", error);
    showSnackbar("ไม่สามารถโหลดข้อมูลห้องเรียนได้", "error");
  }
};

// ดึงรายระดับชั้นเรียน API
const fetchLevels = async () => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    showSnackbar("ไม่พบ Token การเข้าสู่ระบบ", "error");
    return;
  }

  try {
    const response = await axios.get(`${API_BASE_URL}/class`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      withCredentials: true, // กรณีที่ใช้ JWT และ CORS
    });

    //console.log("ระดับชั้นที่โหลดได้:", response.data.levels); // ดู data.levels

    if (response.data && response.data.levels) {
      levels.value = response.data.levels.map((item) => ({
        level_id: item.class_id,
        level_name: item.class_name,
        room_count: item.room_count,
        school_id: item.school_id,
        school_name: item.school_name,
      }));
    } else {
      levels.value = [];
      showSnackbar("ไม่พบข้อมูลระดับชั้น", "warning");
    }
  } catch (error) {
    console.error("เกิดข้อผิดพลาดในการโหลดข้อมูลระดับชั้น:", error);
    showSnackbar("ไม่สามารถโหลดข้อมูลระดับชั้นได้", "error");
  }
};

// ดึงรายชื่อโรงเรียนจาก API
const fetchSchools = async () => {
  try {
    const token = localStorage.getItem("access_token");
    const response = await axios.get(`${API_BASE_URL}/school`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      withCredentials: true,
    });
    school.value = response.data.schools || [];
  } catch (error) {
    console.error("Error fetching schools:", error);
    showSnackbar("ไม่สามารถโหลดข้อมูลโรงเรียนได้", "error");
  }
};

// ดึงรายครู API
const fetchTeachers = async () => {
  try {
    const token = localStorage.getItem("access_token");
    const response = await axios.get(`${API_BASE_URL}/teachers`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      withCredentials: true, // ถ้าคุณใช้ cookie-based auth ด้วย
    });
    // ✅ แปลง first_name + last_name เป็น teacher_name ที่ใช้ใน v-select
    teachers.value = response.data.teachers.map((t) => ({
      teacher_id: t.teacher_id,
      teacher_name: `${t.first_name} ${t.last_name}`,
    }));
  } catch (error) {
    console.error("Error fetching teachers:", error);
    showSnackbar("ไม่สามารถโหลดข้อมูลครูได้", "error");
  }
};

// Async function แยกออกจาก onMounted
const loadInitialData = async () => {
  await fetchSchools();
  await fetchLevels();
  await fetchClassRoom();

  const token = localStorage.getItem("access_token");
  if (!token) {
    router.push("/login");
    return;
  }

  fetchTeachers(); // ไม่ต้องรอ await ก็ได้ถ้าโหลดภายหลัง
};
// ใช้ onMounted แบบไม่ await ตรงๆ
onMounted(() => {
  loadInitialData();
});
</script>

<style scoped></style>
